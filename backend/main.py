# media-request-app: basisopzet met FastAPI backend en Vue frontend

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

RADARR_API = os.getenv("RADARR_API")
RADARR_URL = os.getenv("RADARR_URL")
SONARR_API = os.getenv("SONARR_API")
SONARR_URL = os.getenv("SONARR_URL")
LIDARR_API = os.getenv("LIDARR_API")
LIDARR_URL = os.getenv("LIDARR_URL")

class SearchRequest(BaseModel):
    type: str  # radarr, sonarr, lidarr
    query: str

class AddRequest(BaseModel):
    type: str
    payload: dict

@app.get("/api")
def read_root():
    return {"message": "PlexBacklog draait!"}

@app.post("/api/search")
async def search(req: SearchRequest):
    base_url, api = get_base_url(req.type), get_api_key(req.type)
    if not base_url or not api:
        raise HTTPException(status_code=400, detail="Invalid type")

    endpoint = {
        "radarr": "movie/lookup",
        "sonarr": "series/lookup",
        "lidarr": "artist/lookup"
    }.get(req.type)

    if not endpoint:
        raise HTTPException(status_code=400, detail="Unknown type")

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{base_url}/api/v3/{endpoint}",
            params={"term": req.query},
            headers={"X-Api-Key": api},
            timeout=10
        )
        try:
            return r.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Invalid response from downstream service")

@app.post("/api/add")
async def add(req: AddRequest):
    base_url, api = get_base_url(req.type), get_api_key(req.type)
    if not base_url or not api:
        raise HTTPException(status_code=400, detail="Invalid type")

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{base_url}/api/v3/{get_endpoint(req.type)}", json=req.payload, headers={"X-Api-Key": api})
        return r.json()

def get_base_url(t):
    return {"radarr": RADARR_URL, "sonarr": SONARR_URL, "lidarr": LIDARR_URL}.get(t)

def get_api_key(t):
    return {"radarr": RADARR_API, "sonarr": SONARR_API, "lidarr": LIDARR_API}.get(t)

def get_endpoint(t):
    return {"radarr": "movie", "sonarr": "series", "lidarr": "artist"}.get(t)

# Serve frontend static files AFTER the API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")