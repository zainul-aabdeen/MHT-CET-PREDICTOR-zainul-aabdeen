from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import SearchRequest, CollegeResponse, OptionsResponse
from data_loader import data_loader

app = FastAPI(title="MHT CET College Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/options", response_model=OptionsResponse)
def get_options():
    try:
        opts = data_loader.get_options()
        return OptionsResponse(**opts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search", response_model=List[CollegeResponse])
def search_colleges(request: SearchRequest):
    try:
        results = data_loader.search(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
