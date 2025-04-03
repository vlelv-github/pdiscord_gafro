import os, json, discord
from gacha import TICKET
from discord.ext import commands
from color import color_list


# 유저 데이터 자료구조
user_data = {}
# 데이터 디렉토리
DATA = 'data'
# 유저 데이터 저장 파일 절대 경로
DATA_FILE = DATA + '\\user_data.json'
# 스프레드시트 키
SHEET_KEY = DATA + '\\bot_gafro_credentials.json'
# 권한 보호를 위한 역할 리스트
protected_role = ['관리자 / admin', 'bot', '외국인 / foreigner', 'verified', '@everyone',
                  'bot_gafro', 'minicuda', 'streamcord', 'mee6']

#디렉토리가 없으면 생성
if not os.path.exists(DATA):
    os.makedirs(DATA)

#파일에서 유저 데이터 불러오기
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding="utf-8") as f:
        user_data = json.load(f)

def save_data():
    with open(DATA_FILE, 'w', encoding="utf-8") as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

def load_data(filename='data/user_data.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def user_gacha_init(user_data, user_id):
    from message import user_data_init
    # 유저 데이터가 있는지부터 확인
    user_data_init(user_id)
    # 가챠 키가 없다면 부여
    if 'gacha' not in user_data[user_id]:
        user_data[user_id]['gacha'] = {'value': 0, 'stack': 0, 'times': 0, 'ticket': TICKET}

        save_data()

def users_setup(bot):
    @bot.command(name='profile', aliases=['프로필', 'プロフィール'])
    async def profile(ctx, name: str = None):

        user_id = str(ctx.author.id)
        user = ctx.author

        if name:
            user_tg = discord.utils.find(lambda m: m.display_name == name or m.name == name, ctx.guild.members)

            if user_tg:
                user_id = str(user_tg.id)
                user = user_tg
            else:
                await ctx.send("멤버를 찾을 수 없습니다")
                return False

        nickname = user.display_name if user.display_name else user.name

        most_active_channel_id = max(user_data[user_id]['chat'], key=user_data[user_id]['chat'].get)
        most_active_channel = bot.get_channel(int(most_active_channel_id))

        total_messages = sum(user_data[user_id]['chat'].values())

        user_gacha_init(user_data, user_id)
        total_gacha = user_data[user_id]['gacha']['times']
        stack_gacha = user_data[user_id]['gacha']['stack']

        # 임베드 메시지 작성
        embed = discord.Embed(title=f"{nickname}님의 프로필", color=discord.Color.blue())
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="<a:iw_cherry:1355984902683889765> 닉네임", value=nickname, inline=False)
        embed.add_field(name="🏠 가장 많이 활동한 채널", value=most_active_channel.mention if most_active_channel else "채널 없음",
                        inline=False)
        embed.add_field(name="💬 총 채팅 횟수", value=str(total_messages), inline=False)
        embed.add_field(name=":slot_machine: 가챠 횟수", value=f"{total_gacha} (스택 {stack_gacha})")

        await ctx.send(embed=embed)

    @bot.command(name='color', aliases=['색', '색깔', '色', 'カラー'])
    async def color(ctx, col: str, name: str = None):
        from discord.utils import get
        import re

        user_id = str(ctx.author.id)
        user = ctx.author
        
        roles = [role.name.lower() for role in ctx.guild.roles]  # 역할 이름 리스트 생성
        # 예외 처리
        # 이미 존재하는 역할은, 내 nick_rule과 같아야함
        if name and name.lower() in roles:
            if not ('nick_rule' in user_data[user_id] and user_data[user_id]['nick_rule'] == name.lower()):
                await ctx.send("이미 존재하는 역할명입니다")
                return False
        
        col_digit = col.strip('#')
        if col_digit.lower() in color_list:
            col_digit = color_list[col.lower()]
        elif col_digit.lower() in protected_role or not bool(re.fullmatch(r'[0-9a-fA-F]{6}', col_digit)):
            return False

        _name = user.display_name if user.display_name else user.name

        color = discord.Color(int(col_digit, 16))

        # 해당 유저에게 nick_rule이 존재하면
        if 'nick_rule' in user_data[user_id]:
            # 그 이름 가져와
            rule_name = user_data[user_id]['nick_rule']

            role = get(ctx.guild.roles, name=rule_name)

            if role:
                # 있으면 수정
                new_name = name if name else rule_name
                await role.edit(name=new_name, color=color)
                await ctx.send('닉네임 색상 변경 완료!')
            else:
                # 없으면 만들어
                new_name = name if name else _name
                new_role = await ctx.guild.create_role(name=new_name, color=color)
                positions = {new_role: 36}
                await ctx.guild.edit_role_positions(positions=positions)
                await ctx.author.add_roles(new_role)
                await ctx.send('닉네임 색상 생성 및 변경 완료!')
        else:
            # 존재하지 않으면 만들고 부여
            new_name = name if name else _name
            new_role = await ctx.guild.create_role(name=new_name, color=color)
            positions = {new_role: 36}
            await ctx.guild.edit_role_positions(positions=positions)
            await ctx.author.add_roles(new_role)
            await ctx.send('닉네임 색상 생성 및 변경 완료!')

        user_data[user_id]['nick_rule'] = new_name
        save_data()

    @bot.command(name='role')
    async def role_member(ctx, *, text: commands.clean_content):
        from discord.utils import get

        if not text:
            return False

        role = get(ctx.guild.roles, name=text)

        # 해당 역할을 가진 유저가 없으면 반환
        if not role:
            return False

        members_with_role = [member.display_name for member in role.members]
        members_list = "\n- ".join(members_with_role) if members_with_role else "이 역할을 가진 유저가 없습니다."

        reply = f"**[{text}]** 칭호를 획득한 유저\n\n- " + members_list

        await ctx.reply(reply)

    return user_data