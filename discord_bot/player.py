from service.playback import handle_youtube_link, play_next, stop, skip, pause_resume
from service.message_embed import update_now_playing_embed, reset_message, get_queue_embed
from service.state import reset_state, cleanup_voice, check_authorization, safe_delete

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        reset_state(self)

    async def handle_yotube_link(self, message):
        await handle_youtube_link(self, message)

    async def play_next(self, channel):
        await play_next(self, channel)

    async def stop(self):
        await stop(self)

    async def update_now_playing_embed(self):
        await update_now_playing_embed(self)

    async def skip(self):
        await skip(self)

    async def pause_resume(self):
        await pause_resume(self)

    async def reset_message(self, channel):
        await reset_message(self, channel)

    async def get_queue_embed(self, page=0):
        return await get_queue_embed(self, page)

    def check_authorization(self, interaction):
        return check_authorization(self, interaction)

    async def cleanup_voice(self):
        await cleanup_voice(self)

    async def _safe_delete(self, message):
        await safe_delete(self, message)
