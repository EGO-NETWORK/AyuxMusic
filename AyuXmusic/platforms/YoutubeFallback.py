import asyncio

import yt_dlp

from AyuXmusic.logging import LOGGER
from .Youtube import YouTubeAPI as BaseYouTubeAPI
from .Youtube import _apply_cookiefile_option

logger = LOGGER(__name__)


class YouTubeAPI(BaseYouTubeAPI):
    """YouTube API wrapper with yt-dlp metadata fallback.

    youtube-search-python often fails on VPS IPs or after YouTube changes.
    This subclass keeps the original lookup first, then falls back to yt-dlp.
    """

    def _duration_to_text(self, duration):
        if duration in (None, "", 0):
            return "Unknown"
        try:
            duration = int(duration)
        except (TypeError, ValueError):
            return str(duration) or "Unknown"

        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def _normalize_ytdlp_info(self, info):
        if not isinstance(info, dict):
            return None

        entries = info.get("entries")
        if entries:
            info = next((entry for entry in entries if entry), None)
            if not isinstance(info, dict):
                return None

        video_id = info.get("id") or self._extract_video_id(
            info.get("webpage_url") or info.get("url")
        )
        title = info.get("title")

        if not video_id or not title:
            return None

        thumbnail = info.get("thumbnail")
        thumbnails = [{"url": thumbnail}] if thumbnail else []
        view_count = info.get("view_count")
        view_text = str(view_count) if view_count not in (None, "") else None

        return {
            "id": video_id,
            "title": title,
            "link": f"{self.base}{video_id}",
            "duration": self._duration_to_text(info.get("duration")),
            "thumbnails": thumbnails,
            "channel": {
                "name": info.get("channel") or info.get("uploader"),
                "id": info.get("channel_id") or info.get("uploader_id"),
                "link": info.get("channel_url") or info.get("uploader_url"),
            },
            "viewCount": {
                "text": view_text,
                "short": view_text,
            },
        }

    def _get_video_details_ytdlp_sync(self, link):
        prepared = self._prepare_lookup(link)
        if not prepared:
            return None

        video_id = self._extract_video_id(prepared)
        source = f"{self.base}{video_id}" if video_id else f"ytsearch1:{prepared}"

        ydl_opts = _apply_cookiefile_option(
            {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "extract_flat": False,
                "default_search": "ytsearch1",
                "http_headers": self._build_browser_headers(),
            }
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source, download=False)
            return self._normalize_ytdlp_info(info)
        except Exception as exc:
            logger.error(f"yt-dlp metadata fallback failed for {prepared}: {exc}")
            return None

    async def _get_video_details(self, link: str, limit: int = 20):
        result = await super()._get_video_details(link, limit)
        if result:
            return result

        logger.warning(
            f"Primary YouTube metadata lookup failed for {link}. Trying yt-dlp fallback."
        )
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._get_video_details_ytdlp_sync, link)

        if result:
            video_id = result["id"]
            prepared = self._prepare_lookup(link) or link
            try:
                self._cache_set(
                    self._video_details_cache,
                    ("video", video_id),
                    result,
                    self._cache_ttls["video"],
                )
                self._cache_set(
                    self._video_details_cache,
                    ("lookup", prepared.casefold(), int(limit or 20)),
                    result,
                    self._cache_ttls["video"],
                )
            except Exception:
                pass

        return result
