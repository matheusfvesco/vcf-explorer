from serve import app
from fastapi.testclient import TestClient
import pytest
import random
import polars as pl

client = TestClient(app)


def test_variants():
    for sample in client.get("/samples").json():
        response = client.get(f"/variants/{sample}")
        assert response.status_code == 200


def test_meta():
    response = client.get("/meta")
    assert response.status_code == 200
    json_resp = response.json()
    for sample in client.get("/samples").json():
        assert json_resp[sample]["num_SNPs"] > 0
        assert len(json_resp[sample]["dp"]) == 2
        assert len(json_resp[sample]["freq"]) == 2
        assert len(json_resp[sample]["male_freq"]) == 2
        assert len(json_resp[sample]["female_freq"]) == 2


@pytest.mark.parametrize(
    "param,op,val",
    [
        ("dp", "gt", "int"),
        ("dp", "lt", "int"),
        ("dp", "eq", "int"),
        ("dp", "gt", "float"),
        ("dp", "lt", "float"),
        ("dp", "eq", "float"),
        # freq
        ("freq", "gt", "float"),
        ("freq", "lt", "float"),
        ("freq", "eq", "float"),
        # male_freq
        ("male_freq", "gt", "float"),
        ("male_freq", "lt", "float"),
        ("male_freq", "eq", "float"),
        # female_freq
        ("female_freq", "gt", "float"),
        ("female_freq", "lt", "float"),
        ("female_freq", "eq", "float"),
    ],
)
def test_filter_correct(param, op, val):
    response = client.get("/meta")
    json_resp = response.json()
    for sample in client.get("/samples").json():
        min, max = tuple(json_resp[sample][param])
        if val == "int":
            val = random.randint(min, max)
        else:
            val = random.uniform(min, max)

        response = client.get(f"/filter/{sample}/{param}/{op}/{val}")
        assert response.status_code == 200


@pytest.mark.parametrize("param", ["dp", "freq", "male_freq", "female_freq"])
def test_filter_min_value(param):
    for sample in client.get("/samples").json():
        df = pl.from_dicts(client.get(f"/variants/{sample}").json()["variants"])
        num_SNPs = len(df.filter(pl.col(param).is_not_null()))
        json_resp = client.get("/meta").json()
        # num_SNPs = json_resp[sample]["num_SNPs"]

        # Ensure num_SNPs is greater than 0 to proceed
        assert num_SNPs > 0

        min_value, max_value = tuple(json_resp[sample][param])

        # Calculate the threshold value, which is 10% less than the minimum value
        threshold_value = max(min_value * 0.0001, 0)
        threshold_value = min_value - threshold_value

        # Query the filter endpoint with the 'lt' operator to get values less than the threshold
        response = client.get(f"/filter/{sample}/{param}/gt/{threshold_value}")

        # Ensure the response is successful
        assert response.status_code == 200

        # Assert that the length of the returned variants equals num_SNPs
        json_resp = response.json()
        assert len(json_resp["variants"]) == num_SNPs


@pytest.mark.parametrize("param", ["dp", "freq", "male_freq", "female_freq"])
def test_filter_max_value(param):
    for sample in client.get("/samples").json():
        df = pl.from_dicts(client.get(f"/variants/{sample}").json()["variants"])
        num_SNPs = len(df.filter(pl.col(param).is_not_null()))
        json_resp = client.get("/meta").json()
        # num_SNPs = json_resp[sample]["num_SNPs"]

        # Ensure num_SNPs is greater than 0 to proceed
        assert num_SNPs > 0

        min_value, max_value = tuple(json_resp[sample][param])

        # Calculate the threshold value, which is 10% less than the minimum value
        threshold_value = max_value * 0.0001
        threshold_value = max_value + threshold_value

        # Query the filter endpoint with the 'lt' operator to get values less than the threshold
        response = client.get(f"/filter/{sample}/{param}/lt/{threshold_value}")

        # Ensure the response is successful
        assert response.status_code == 200

        # Assert that the length of the returned variants equals num_SNPs
        json_resp = response.json()
        assert len(json_resp["variants"]) == num_SNPs
