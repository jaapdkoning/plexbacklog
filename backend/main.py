import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Setup FastAPI
app = FastAPI()

# Mount the Vue frontend build directory
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html for all frontend routes
@app.get("/{full_path:path}")
async def serve_vue_app(full_path: str):
    return FileResponse("static/index.html")

# --- Jouw bestaande POST endpoint blijft staan ---
@app.post("/add")
async def add(request: Request):
    form = await request.form()
    kind = form.get("kind")
    title = form.get("title")

    async with httpx.AsyncClient() as client:
        if kind == "movie":
            await client.post(
                f"{os.getenv('RADARR_URL')}/api/v3/movie",
                headers={"X-Api-Key": os.getenv("RADARR_API_KEY")},
                json={
                    "title": title,
                    "qualityProfileId": int(os.getenv("RADARR_QUALITY_PROFILE_ID", 1)),
                    "rootFolderPath": "/mediafolder/Movies",
                    "monitored": True,
                    "addOptions": {"searchForMovie": True}
                },
            )
        elif kind == "series":
            resp = await client.get(
                f"{os.getenv('SONARR_URL')}/api/v3/series/lookup?term={title}",
                headers={"X-Api-Key": os.getenv("SONARR_API_KEY")}
            )
            data = resp.json()
            if data:
                series = data[0]
                await client.post(
                    f"{os.getenv('SONARR_URL')}/api/v3/series",
                    headers={"X-Api-Key": os.getenv("SONARR_API_KEY")},
                    json={
                        "title": series["title"],
                        "qualityProfileId": int(os.getenv("SONARR_QUALITY_PROFILE_ID", 6)),
                        "languageProfileId": int(os.getenv("SONARR_LANGUAGE_PROFILE_ID", 1)),
                        "rootFolderPath": "/mediafolder/Series",
                        "tvdbId": series["tvdbId"],
                        "monitored": True,
                        "addOptions": {"searchForMissingEpisodes": True},
                        "seasons": [
                            {"seasonNumber": s["seasonNumber"], "monitored": True}
                            for s in series.get("seasons", [])
                        ]
                    }
                )
        elif kind == "music":
            resp = await client.get(
                f"{os.getenv('LIDARR_URL')}/api/v1/artist/lookup?term={title}",
                headers={"X-Api-Key": os.getenv("LIDARR_API_KEY")}
            )
            data = resp.json()
            if data:
                artist = data[0]
                await client.post(
                    f"{os.getenv('LIDARR_URL')}/api/v1/artist",
                    headers={"X-Api-Key": os.getenv("LIDARR_API_KEY")},
                    json={
                        "artistName": artist["artistName"],
                        "qualityProfileId": int(os.getenv("LIDARR_QUALITY_PROFILE_ID", 2)),
                        "metadataProfileId": int(os.getenv("LIDARR_METADATA_PROFILE_ID", 1)),
                        "rootFolderPath": "/music",
                        "foreignArtistId": artist["foreignArtistId"],
                        "monitored": True,
                        "addOptions": {"searchForNewAlbum": True}
                    }
                )

    return FileResponse("static/index.html")
