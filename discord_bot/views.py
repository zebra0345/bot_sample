import asyncio
import discord
import math

# 🎛️ 음악 컨트롤 UI 뷰
class MusicView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player
        self.queue_page = 0  # 현재 페이지

        # 🔼 첫 번째 줄: 이전/다음 페이지 버튼
        self.add_item(PreviousPageButton(self))
        self.add_item(NextPageButton(self))

        # ▶️ 두 번째 줄: 음악 재생 제어 버튼
        self.add_item(PauseResumeButton(player))
        self.add_item(SkipButton(player))
        self.add_item(StopButton(player))
        self.add_item(PlaylistButton(player))

# ◀️ 이전 페이지 버튼
class PreviousPageButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="◀️ 이전 페이지", style=discord.ButtonStyle.secondary, row=0)
        self.view_obj = view

    async def callback(self, interaction: discord.Interaction):
        if self.view_obj.queue_page > 0:
            self.view_obj.queue_page -= 1
            embed = await self.view_obj.player.get_queue_embed(self.view_obj.queue_page)
            await interaction.response.edit_message(embed=embed, view=self.view_obj)
        else:
            await interaction.response.send_message("⛔ 이미 첫 번째 페이지입니다.", ephemeral=True)

# ▶️ 다음 페이지 버튼
class NextPageButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="▶️ 다음 페이지", style=discord.ButtonStyle.secondary, row=0)
        self.view_obj = view

    async def callback(self, interaction: discord.Interaction):
        queue_len = len(self.view_obj.player.queue)
        max_page = math.ceil(queue_len / 10) - 1

        if self.view_obj.queue_page < max_page:
            self.view_obj.queue_page += 1
            embed = await self.view_obj.player.get_queue_embed(self.view_obj.queue_page)
            await interaction.response.edit_message(embed=embed, view=self.view_obj)
        else:
            await interaction.response.send_message("⛔ 마지막 페이지입니다.", ephemeral=True)

# ⏯ 일시정지 / 재개 버튼
class PauseResumeButton(discord.ui.Button):
    def __init__(self, player):
        super().__init__(label="⏯ 일시정지 / 재개", style=discord.ButtonStyle.secondary, row=1)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        authorized, reason = self.player.check_authorization(interaction)
        if not authorized:
            await interaction.response.send_message(reason, ephemeral=True)
            return
        await interaction.response.defer()
        await self.player.pause_resume()

# ⏭ 다음 곡으로 스킵
class SkipButton(discord.ui.Button):
    def __init__(self, player):
        super().__init__(label="⏭ 다음 곡", style=discord.ButtonStyle.primary, row=1)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        authorized, reason = self.player.check_authorization(interaction)
        if not authorized:
            await interaction.response.send_message(reason, ephemeral=True)
            return
        if not self.player.queue:
            await interaction.response.send_message("⏭ 마지막 곡이라서 스킵할 수 없습니다.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.player.skip()

# ⏹ 재생 정지 및 초기화
class StopButton(discord.ui.Button):
    def __init__(self, player):
        super().__init__(label="⏹ 정지", style=discord.ButtonStyle.danger, row=1)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        authorized, reason = self.player.check_authorization(interaction)
        if not authorized:
            await interaction.response.send_message(reason, ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.followup.send("🛑 음악 재생이 중지되었습니다.", ephemeral=True)
        asyncio.create_task(self.player.stop())

# 📜 전체 곡 목록 (ephemeral)
class PlaylistButton(discord.ui.Button):
    def __init__(self, player):
        super().__init__(label="📜 전체 곡 목록", style=discord.ButtonStyle.success, row=1)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        if not self.player.queue:
            await interaction.response.send_message("🎶 대기 중인 곡이 없습니다.", ephemeral=True)
            return

        lines = [f"{i+1}. {item['title'][:100]}" for i, item in enumerate(self.player.queue)]
        full_text = "\n".join(lines)
        await interaction.response.send_message(full_text, ephemeral=True)
