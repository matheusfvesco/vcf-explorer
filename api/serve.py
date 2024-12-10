# gets data from postgres

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/variants")
def get_variants():
    return {"Variants": ["A", "B", "C"]}

@app.get("/filter")
def filter_variants():
    return {"Variants": ["A", "B", "C"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4000)