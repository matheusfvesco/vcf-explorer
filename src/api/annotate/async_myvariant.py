import asyncio
from myvariant import MyVariantInfo
from pathlib import Path
from cyvcf2 import VCF
import logging


class AsyncMyVariantInfo:
    def __init__(self):
        self.client = MyVariantInfo()

    def get_hgvs_from_vcf(self, path: Path | str) -> list[str]:
        file = VCF(str(path))
        return list(
            self.client.format_hgvs(
                variant.CHROM, variant.POS, variant.REF, variant.ALT[0]
            )
            for variant in file
        )

    async def getvariants(self, ids: list, chunk_size=500, fields="all"):
        """
        Fetch variant information for a list of IDs asynchronously, divided into chunks.
        """
        loop = asyncio.get_event_loop()
        logger = logging.getLogger("annotate")
        # Divide the ids into chunks
        chunks = [ids[i : i + chunk_size] for i in range(0, len(ids), chunk_size)]
        logger.debug(f"Divided {len(ids)} SNPs into {len(chunks)} chunks of size {chunk_size}.")
        
        # Asynchronously fetch data for each chunk
        tasks = [
            loop.run_in_executor(
                None, lambda chunk=chunk: self.client.getvariants(chunk, fields=fields)
            )
            for chunk in chunks
        ]
        results = await asyncio.gather(*tasks)

        # Merge all results into a single list
        return sum(results, [])