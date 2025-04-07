from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import yt_dlp
import asyncio
import uvicorn

app = FastAPI()

# 최대 길이
MAX_TRACKS = 30

# 쿼리문 클래스
class QueryRequest(BaseModel):
    query:str

# 트랙정보
class TrackInfo(BaseModel):
    title:str
    url:str
    webpage_url:str
    thumbnail:str
    is_playlist:bool=False

# 곡 정보들 추출하는 함수
def _extract_info_sync(query: str) -> List[TrackInfo]:
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": False,
        "ignoreerrors": True  #일부 영상이 오류 나도 무시
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        print(info)
        # 🎵 재생목록 처리
        if "entries" in info:
            entries = info.get("entries", [])
            # 유효한 영상만 필터링
            valid_entries = [
                entry for entry in entries
                if entry and isinstance(entry, dict) and entry.get("url")
            ][:MAX_TRACKS]

            return [
                {
                    "title": entry.get("title", "Unknown"),
                    "url": entry["url"],
                    "webpage_url": entry.get("webpage_url", ""),
                    "thumbnail": entry.get("thumbnail", ""),
                    "is_playlist": True
                }
                for entry in valid_entries
            ]

        # 🎵 단일 곡 처리
        else:
            return [{
                "title": info.get("title", "Unknown"),
                "url": info["url"],
                "webpage_url": info.get("webpage_url", ""),
                "thumbnail": info.get("thumbnail", ""),
                "is_playlist": False
            }]

        
# 재생목록추출하는 비동기함수
@app.post("/resolve", response_model=List[TrackInfo])
async def resolve_query(req:QueryRequest):
    try:
        result = await asyncio.to_thread(_extract_info_sync, req.query)
        if not result:
            raise HTTPException(status_code=404, detail="No audio found.")
        return result
    except Exception as e:
        print(f"[yt_dlp ERROR] {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)