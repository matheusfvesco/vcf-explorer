import sys
import argparse
import os
print(os.getcwd())
print(os.listdir("."))
print(os.listdir("./src"))
print()
print()
from annotate import AsyncMyVariantInfo
import polars as pl
import asyncio
import logging
from pathlib import Path
import time

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

sys.excepthook = handle_exception

def annotate_variant(data: dict):
    global_freq = None
    male_freq = (None,)
    female_freq = None
    global_dp = None
    # gets gene
    genes = data.get("cadd", {}).get("gene", [])
    if isinstance(genes, list):
        gene_ids = [gene.get("gene_id") for gene in genes]
    else:
        gene_ids = [genes.get("gene_id")]

    # gets rsid
    rsid = data.get("dbsnp", {}).get("rsid", None)

    # gets frequency
    # global
    gnomad_freq = data.get("gnomad_exome", {}).get("af", {}).get("af", None)
    gnomad_male_freq = data.get("gnomad_exome", {}).get("af", {}).get("af_male", None)
    gnomad_female_freq = (
        data.get("gnomad_exome", {}).get("af", {}).get("af_female", None)
    )
    genome_1k_freq = data.get("cadd", {}).get("1000g", {}).get("af", None)
    exac_freq = data.get("exac", {}).get("af", None)

    # gets depth
    exome_dp = data.get("gnomad_exome", {}).get("dp", None)
    genome_dp = data.get("gnomad_genome", {}).get("dp", None)
    exac_dp = data.get("exac", {}).get("dp", None)

    # fill in preferred values
    global_freq = gnomad_freq or genome_1k_freq or exac_freq
    male_freq = gnomad_male_freq
    female_freq = gnomad_female_freq

    global_dp = exome_dp or genome_dp or exac_dp

    return (
        data["query"],
        rsid,
        gene_ids,
        global_freq,
        male_freq,
        female_freq,
        global_dp,
    )


async def main(input_path, output_path, logger):
    client = AsyncMyVariantInfo()
    logger.info(f"Reading {input_path}...")
    hgvs_notations = client.get_hgvs_from_vcf(input_path)
    logger.info(f"Success! There are {len(hgvs_notations)} SNPs")

    # queries myvariant
    # ----------------
    fields = [
        # frequency
        "cadd.1000g.af",
        "dbnsfp.1000gp3.af",
        "gnomad_exome.af.af_male",
        "gnomad_exome.af.af",
        "gnomad_exome.af.af_female",
        "dbnsfp.exac.af",
        "dbsnp.alleles.freq.exac",
        "exac.af",
        # geneid
        "dbnsfp.ensembl.geneid",
        "docm.ensembl_gene_id",
        "cadd.gene.gene_id",
        # rsid
        "dbsnp.rsid",
        "dbnsfp.rsid",
        "gnomad_genome.rsid",
        # dp
        "gnomad_exome.dp",
        "gnomad_genome.dp",
        "exac.dp",
        # vcf
        "vcf",
    ]

    logger.info(f"Querying {len(hgvs_notations)} SNPs...")

    start_time = time.perf_counter()  # Record the start time
    response = await client.getvariants(
        ids=hgvs_notations, fields=fields, chunk_size=500
    )
    end_time = time.perf_counter()  # Record the end time
    elapsed_time = end_time - start_time

    logger.info(f"Success! Query took {elapsed_time:.2f} seconds.")

    annotations = [annotate_variant(data) for data in response]

    output_dict = {
        "hgvs": [],
        "rsid": [],
        "genes": [],
        "freq": [],
        "male_freq": [],
        "female_freq": [],
        "dp": [],
    }
    for (
        hgvs,
        rsid,
        gene_ids,
        global_freq,
        male_freq,
        female_freq,
        global_dp,
    ) in annotations:
        output_dict["hgvs"].append(hgvs)
        output_dict["rsid"].append(rsid)
        genes = ",".join(gene_ids) if gene_ids else None
        output_dict["genes"].append(genes)
        output_dict["freq"].append(global_freq)
        output_dict["male_freq"].append(male_freq)
        output_dict["female_freq"].append(female_freq)
        output_dict["dp"].append(global_dp)
    df = pl.from_dict(output_dict)
    df.write_csv(output_path, separator="\t")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")

    args = parser.parse_args()
    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    # Setup logging
    # setup third party logs
    logging.basicConfig(level=logging.NOTSET)
    logging.getLogger("biothings.client").setLevel(logging.WARNING)  # Suppress info/debug logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # Suppress info/debug logs
    logger = logging.getLogger("annotate")
    logger.setLevel(logging.NOTSET)  # Allow all messages to pass to handlers
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)  # Only log INFO, WARNING, and ERROR to console
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler
    log_path = Path("logs") / "annotate.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_log = logging.FileHandler(filename=log_path)
    file_log.setLevel(logging.NOTSET)  # Log absolutely everything to file
    file_log.setFormatter(formatter)
    logger.addHandler(file_log)

    asyncio.run(main(input_path=input_path, output_path=output_path, logger=logger))
