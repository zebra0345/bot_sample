import httpx
import asyncio
import os
from dotenv import load_dotenv
import traceback
load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_HOST")


# 오디오 정보가져오기
async def get_audio_info(query:str) -> list[dict]:
    try:
        print(FASTAPI_URL)
        timeout = httpx.Timeout(20.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{FASTAPI_URL}/resolve", json={"query": query})
            response.raise_for_status()
            print(response.json())
            return response.json()
    except Exception as e:
        print(f"[FastAPI ERROR]")
        traceback.print_exc()
        return []