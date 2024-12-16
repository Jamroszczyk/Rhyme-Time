from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import aiohttp
from random import choice
from typing import List
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.realpath(__file__))


async def get_rhyme(session: aiohttp.ClientSession, word: str) -> str:
    try:
        async with session.get(
            f"https://api.datamuse.com/words?rel_rhy={word}"
        ) as response:
            data = await response.json()
            if data:
                return choice(data)["word"]
            return "No rhyme found"
    except Exception:
        return "Error finding rhyme"


@app.get("/")
async def read_root():
    return FileResponse(os.path.join(current_dir, "index.html"))


@app.post("/api")
async def get_rhymes(request: dict):
    async with aiohttp.ClientSession() as session:
        tasks = [get_rhyme(session, word) for word in request["words"]]
        rhymes = await asyncio.gather(*tasks)

    return {"rhymes": rhymes}


app.mount("/", StaticFiles(directory=current_dir), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
