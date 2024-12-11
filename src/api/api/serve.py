from fastapi import FastAPI, HTTPException
import polars as pl
from pathlib import Path

df_paths = sorted(Path("data").rglob("*.tsv"))
variants_dfs: dict[str, pl.DataFrame] = {
    df_path.stem: pl.read_csv(df_path, separator="\t").sort("freq", nulls_last=True)
    for df_path in df_paths
}

tags_metadata = [
    {
        "name": "filter",
        "description": "Operations with filtering.",
    },
    {
        "name": "items",
        "description": "Operations using the entire dataset",
    },
]

description = f"""
# API for the {', '.join(list(variants_dfs.keys()))} samples

This API is designed to be used for accessing and filtering the variants in the sample.
"""

app = FastAPI(
    openapi_tags=tags_metadata,
    title="vcf api",
    description=description,
    summary=f"API for the {', '.join(list(variants_dfs.keys()))} samples",
    version="0.0.1",
)


@app.get(
    "/",
    summary="Retrieves information about the API and the sample",
    description="Retrieves information about the API and the sample",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def read_root():
    return {
        "info": f"Serving API for the {', '.join(list(variants_dfs.keys()))} samples",
        "samples": list(variants_dfs.keys()),
        "num_SNPs": {sample: len(variants_dfs[sample]) for sample in variants_dfs},
    }


@app.get(
    "/meta",
    summary="Retrieves meta from the entire dataset",
    description="Retrieves meta from the entire dataset",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def meta():
    out = {}
    for sample in variants_dfs:
        out[sample] = {
            "num_SNPs": len(variants_dfs[sample]),
            "dp": [variants_dfs[sample]["dp"].min(), variants_dfs[sample]["dp"].max()],
            "freq": [
                variants_dfs[sample]["freq"].min(),
                variants_dfs[sample]["freq"].max(),
            ],
            "male_freq": [
                variants_dfs[sample]["male_freq"].min(),
                variants_dfs[sample]["male_freq"].max(),
            ],
            "female_freq": [
                variants_dfs[sample]["female_freq"].min(),
                variants_dfs[sample]["female_freq"].max(),
            ],
        }
    return out


@app.get(
    "/samples",
    summary="Lists the samples available",
    description="Lists the samples available",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def samples():
    return [sample for sample in variants_dfs]


@app.get(
    "/variants/{sample}",
    summary="Retrieves the entire dataset for a sample",
    description="Retrieves the entire dataset for a sample",
    tags=["items"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
    },
)
def get_variants(sample: str):
    if sample not in variants_dfs:
        raise HTTPException(status_code=404, detail="Sample not found")

    return {"sample": sample, "variants": variants_dfs[sample].to_dicts()}


@app.get(
    "/filter/{sample}/{parameter}/{operator}/{value}",
    summary="Filters the dataset",
    description="Filters the dataset using the specified parameter, based on the specified operator and value",
    tags=["filter"],
    responses={
        200: {"description": "Successful response with dataframe as a list of dicts"},
        400: {"description": "User mistake on the query"},
        404: {"description": "Sample not found"},
    },
)
def filter_variants(sample: str, parameter: str, operator: str, value: float):
    # hgvs	rsid	genes	freq	male_freq	female_freq	dp
    accepted_columns = ["freq", "male_freq", "female_freq", "dp"]
    accepted_params = ["gt", "lt", "eq"]
    if sample not in variants_dfs:
        raise HTTPException(status_code=404, detail="Sample not found")
    if parameter not in accepted_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter: {parameter}. Must be one of: {accepted_columns}",
        )
    if operator not in accepted_params:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operator. Must be one of: {accepted_params}",
        )

    if operator == "eq":
        filtered_variants = variants_dfs[sample].filter(pl.col(parameter) == value)
    elif operator == "gt":
        filtered_variants = variants_dfs[sample].filter(pl.col(parameter) >= value)
    elif operator == "lt":
        filtered_variants = variants_dfs[sample].filter(pl.col(parameter) <= value)

    return {"sample": sample, "variants": filtered_variants.to_dicts()}
