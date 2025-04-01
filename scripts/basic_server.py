"""
Extremely basic FastAPI server to test connectivity
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting basic server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
