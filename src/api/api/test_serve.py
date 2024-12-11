from serve import app
from fastapi.testclient import TestClient
import pytest
import random

client = TestClient(app)

def test_variants():
    response = client.get('/variants')
    assert response.status_code == 200

def test_meta():
    response = client.get('/meta')
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["num_SNPs"] > 0
    assert len(json_resp["dp"]) == 2
    assert len(json_resp["freq"]) == 2
    assert len(json_resp["male_freq"]) == 2
    assert len(json_resp["female_freq"]) == 2


@pytest.mark.parametrize(
    "param,op,val", [
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
    ]
)
def test_filter_correct(param, op, val):
    response = client.get('/meta')
    json_resp = response.json()
    min, max = tuple(json_resp[param])
    if val == "int":
        val = random.randint(min, max)
    else:
        val = random.uniform(min, max)
    
    response = client.get(f'/filter/{param}/{op}/{val}')
    assert response.status_code == 200
