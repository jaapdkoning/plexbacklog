import os
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment settings
RADARR_URL = os.getenv("RADARR_URL")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
RADARR_ROOT_FOLDER_ID = int(os.getenv("RADARR_ROOT_FOLDER_ID", 1))
RADARR_QUALITY_PROFILE_ID = int(os.getenv("RADARR_QUALITY_PROFILE_ID", 1))

SONARR_URL = os.getenv("SONARR_URL")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")
SONARR_ROOT_FOLDER_ID = int(os.getenv("SONARR_ROOT_FOLDER_ID", 2))
SONARR_QUALITY_PROFILE_ID = int(os.getenv("SONARR_QUALITY_PROFILE_ID", 6))
SONARR_LANGUAGE_PROFILE_ID = int(os.getenv("SONARR_LANGUAGE_PROFILE_ID", 1))

LIDARR_URL = os.getenv("LIDARR_URL")
LIDARR_API_KEY = os.getenv("LIDARR_API_KEY")
LIDARR_ROOT_FOLDER_ID = int(os.getenv("LIDARR_ROOT_FOLDER_ID", 1))
LIDARR_QUALITY_PROFILE_ID = int(os.getenv("LIDARR_QUALITY_PROFILE_ID", 2))
LIDARR_METADATA_PROFILE_ID = int(os.getenv("LIDARR_METADATA_PROFILE_ID", 1))

# Setup FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add")
async def add(request: Request, kind: str = Form(...), title: str = Form(...)):
    async with httpx.AsyncClient() as client:
        if kind == "movie":
            response = await client.post(
                f"{RADARR_URL}/api/v3/movie",
                headers={"X-Api-Key": RADARR_API_KEY},
                json={
                    "title": title,
                    "qualityProfileId": RADARR_QUALITY_PROFILE_ID,
                    "rootFolderPath": "/mediafolder/Movies",
                    "monitored": True,
                    "addOptions": {"searchForMovie": True}
                },
            )
        elif kind == "series":
            response = await client.post(
                f"{SONARR_URL}/api/v3/series/lookup?term={title}",
                headers={"X-Api-Key": SONARR_API_KEY}
            )
            data = response.json()
            if data:
                series = data[0]
                payload = {
                    "title": series["title"],
                    "qualityProfileId": SONARR_QUALITY_PROFILE_ID,
                    "languageProfileId": SONARR_LANGUAGE_PROFILE_ID,
                    "rootFolderPath": "/mediafolder/Series",
                    "tvdbId": series["tvdbId"],
                    "monitored": True,
                    "addOptions": {"searchForMissingEpisodes": True},
                    "seasons": [
                        {"seasonNumber": s["seasonNumber"], "monitored": True}
                        for s in series.get("seasons", [])
                    ]
                }
                await client.post(
                    f"{SONARR_URL}/api/v3/series",
                    headers={"X-Api-Key": SONARR_API_KEY},
                    json=payload
                )
        elif kind == "music":
            response = await client.get(
                f"{LIDARR_URL}/api/v1/artist/lookup?term={title}",
                headers={"X-Api-Key": LIDARR_API_KEY}
            )
            data = response.json()
            if data:
                artist = data[0]
                payload = {
                    "artistName": artist["artistName"],
                    "qualityProfileId": LIDARR_QUALITY_PROFILE_ID,
                    "metadataProfileId": LIDARR_METADATA_PROFILE_ID,
                    "rootFolderPath": "/music",
                    "foreignArtistId": artist["foreignArtistId"],
                    "monitored": True,
                    "addOptions": {"searchForNewAlbum": True}
                }
                await client.post(
                    f"{LIDARR_URL}/api/v1/artist",
                    headers={"X-Api-Key": LIDARR_API_KEY},
                    json=payload
                )

    return RedirectResponse("/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
