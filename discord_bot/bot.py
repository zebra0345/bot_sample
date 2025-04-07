import discord
from discord.ext import commands
from player import MusicPlayer
from views import MusicView
import os
from dotenv import load_dotenv
load_dotenv()

# 봇의 기본 설정을 다루기 위한 코드
intents = discord.Intents.default() # 기본설정
intents.message_content = True # 메세지 설정 허용
intents.voice_states = True # 음성 채팅 이벤트 허용

# 봇 객체 생성
# 커멘드는 ! 고 intents 미리 설정한거 사용
bot = commands.Bot(command_prefix="!", intents=intents)
music_player = MusicPlayer(bot)
TOKEN = os.getenv("TOKEN")
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

# 봇 이벤트 핸들러
@bot.event
async def on_ready():
    # 정상로그인 표시
    print(f"Logged in as {bot.user.name}")

    # 설정된 텍스트 채널 기반 채널 객체 생성
    channel = bot.get_channel(TARGET_CHANNEL)

    if channel:
        # 채널 내 메시지 전부 삭제
        async for msg in channel.history(limit=None):
            try:
                await msg.delete()
            except:
                pass  # 삭제 안 되는 메시지는 무시 (오래됐거나 권한 문제)

        # 초기 embed 생성
        embed = discord.Embed(
            title="🎶 디스코드 음악봇",
            description="봇이 대기 중입니다... 유튜브 링크 또는 검색어를 붙여넣어주세요!",
            color=0x00ff99
        )

        embed.set_thumbnail(url="https://i.namu.wiki/i/z4nW20yBaVNGldlX_pnU9CZk669T1nO9PDALhcvgMQi6g4XWd_i7uEHXUgBQHI_A1zy3hcxAPfsTGWey4VYPqg.webp")
        view = MusicView(music_player)

        msg = await channel.send(embed=embed, view=view)
        music_player.current_message = msg

        print("🎶 초기 메시지 생성 완료")

@bot.event
async def on_message(message):
    # 봇 보낸 메세지는 무시
    if message.author.bot:
        return
    
    # 설정한 채널 이외의 채널은 무시
    if message.channel.id != TARGET_CHANNEL:
        return
    
    if message.content.strip():
        await music_player.handle_yotube_link(message)

bot.run(TOKEN)