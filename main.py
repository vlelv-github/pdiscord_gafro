import discord, asyncio
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from message import def_message
from aiwanna import aiwanna_setup
from youtube import youtube_setup
from py_users import users_setup
from gacha import gacha_setup
from date_event import create_today

intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용을 다룰 권한을 활성화
intents.members = True
intents.messages = True
intents.guilds = True
api_key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# 유저가 채팅을 보낼시 이벤트
@bot.event
async def on_message(message):
    await def_message(bot, message)

# 헬프 명령어
@bot.command(name='헬프', aliases=['command', 'commands'])
async def help_command(ctx):
    commands = ["   !" + command.name for command in bot.commands]
    commands.sort()
    output = "Commands : " + "\n\n"
    output += "\n".join(commands)
    await ctx.send(f'```{output}```')

# 유저 데이터 관련 기능
user_data = users_setup(bot)

# 아이워너 관련 기능
aiwanna_setup(bot)

# 유튜브 관련 기능
youtube_setup(bot)

# 가챠 관련 기능
gacha_setup(bot, user_data)

# 매일 자정마다 알림
TARGET_HOUR = 0
TARGET_MINUTE = 0
@tasks.loop(hours = 24)
async def ev_midnight():
    print("자정!")
    create_today(user_data)

# 봇이 준비되면 호출되는 이벤트
@bot.event
async def on_ready():
    print(f'가프로 채널에 {bot.user} 봇이 준비되었습니다.')

    # 오늘 날짜가 적힌 텍스트 파일 생성
    create_today(user_data)
    # 현재 시간과 지정한 시간까지 남은 시간 계산
    now = datetime.now()
    target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)

    # 지정한 시간이 이미 지났다면, 내일 같은 시간으로 설정
    if now > target_time:
        target_time += timedelta(days=1)

    wait_time = (target_time - now).total_seconds()  # 지정 시간까지 남은 시간 (초 단위)

    # 지정 시간이 되면 첫 번째 이벤트 시작
    await asyncio.sleep(wait_time)
    ev_midnight.start()

# 봇을 실행
bot.run(api_key)
