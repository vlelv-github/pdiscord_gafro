import random, discord

# 이모지 서버
# 컬렉션을 위한 이모지가 들어있는 이모지 서버입니다.
EMOJI_SERVER = [111111111111111111]

# 전체 이모지
full_emojis = []

# 스택 수
REQ_STACK = 10

# 하루 가챠 횟수
TICKET = 5



def init_ticket(user_data):
    from py_users import save_data
    for user_id, _ in user_data.items():
        if 'gacha' in user_data[user_id]:
            user_data[user_id]['gacha']['ticket'] = TICKET

    save_data()

def get_item_number(item_str):
    if item_str in full_emojis:
        # +1은 인덱스를 1부터 세겠다는 의미
        return full_emojis.index(item_str) + 1

def is_have_value(user_data, user_id, val):
    user_value = user_data[user_id]['gacha']['value'] # 2진수로 변환
    item_value = 1 << (val - 1)
    return user_value & item_value != 0

def get_new_item(user_data, user_id, val):
    user_value = user_data[user_id]['gacha']['value']  # 2진수로 변환
    item_value = 1 << (val - 1)

    user_data[user_id]['gacha']['value'] = user_value | item_value

def gacha_setup(bot, user_data):
    @bot.command(name='gacha', aliases=['가챠', 'ガチャ'])
    async def gacha(ctx, t: str = '1'):
        from py_users import save_data
        from py_users import user_gacha_init
        global full_emojis

        user_id = str(ctx.author.id)

        # 가챠 키가 없다면 추가
        user_gacha_init(user_data, user_id)

        # 파라미터가 옳지 않으면 정상화
        if t.isdigit() and int(t) > 0:
            times = min(int(t), user_data[user_id]['gacha']['ticket'])
        else:
            times = 1

        # 일일 사용량을 모두 소진했다면 반환
        if user_data[user_id]['gacha']['ticket'] < 1:
            await ctx.reply(f"**하루 {TICKET}회만!**")
            return False

        if not full_emojis:
            # 이모지 서버의 이모지 가져오기
            for server in EMOJI_SERVER:
                guild = bot.get_guild(server)  # 특정 서버 가져오기

                if not guild:
                    continue

                # 움직이는 이모지만
                full_emojis += [emoji.name + ":" + str(emoji.id) for emoji in guild.emojis if
                                emoji.animated]

        # 이모지가 아무것도 없으면 반환
        if not full_emojis:
            return False

        for i in range(times):
            user_data[user_id]['gacha']['times'] += 1 # 가챠 횟수 증가
            user_data[user_id]['gacha']['ticket'] -= 1 # 사용 횟수 감소

            # 요구 스택 이하는 통상 가챠
            if user_data[user_id]['gacha']['stack'] < REQ_STACK:
                # 통상 가챠 (전체 이모지중 하나 랜덤 선택)
                emo = random.choice(full_emojis)
            else:
                # 전체 이모지중에서 가지고 있는건 빼셈
                remain = (1 << len(full_emojis)) - 1
                remain ^= user_data[user_id]['gacha']['value']

                remaining_items = []
                for i in range(len(full_emojis)):
                    if remain & (1 << i):  # 비트가 1인 경우
                        remaining_items.append(full_emojis[i])

                if remaining_items:
                    emo = random.choice(remaining_items)

                    # 스택 초기화
                    user_data[user_id]['gacha']['stack'] -= REQ_STACK
                else:
                    # 더이상 뽑을게 없으면 스택을 초기화하지 않고 통상 가챠로 전환
                    emo = random.choice(full_emojis)

            ind = get_item_number(emo)
            emo_nid = full_emojis[ind - 1]

            # 가지고 있다면 스택 쌓기, 없다면 새로 획득
            # new_get은 신규 획득시의 아이콘
            # dup_get은 중복 획득시의 아이콘
            if is_have_value(user_data,user_id,ind):
                user_data[user_id]['gacha']['stack'] += 1
                reply = "<:dup_get:1356158198431748104>" + f"<a:{emo_nid}>"
            else:
                get_new_item(user_data,user_id,ind)
                reply = "<:new_get:1356159420072984606>" + f"<a:{emo_nid}>"

            # 얻었음을 알림
            await ctx.reply(reply)

        save_data()

    @bot.command(name='collection', aliases=['컬렉션', '콜렉션', 'コレクション', 'コレ'])
    async def collection(ctx, name: str = None):
        from py_users import user_gacha_init
        global full_emojis
        user_id = str(ctx.author.id)

        if name:
            user_tg = discord.utils.find(lambda m: m.display_name == name or m.name == name, ctx.guild.members)

            if user_tg:
                user_id = str(user_tg.id)
            else:
                await ctx.send("멤버를 찾을 수 없습니다")
                return False

        if not full_emojis:
            # 이모지 서버의 이모지 가져오기
            for server in EMOJI_SERVER:
                guild = bot.get_guild(server)  # 특정 서버 가져오기

                if not guild:
                    continue

                # 움직이는 이모지만
                full_emojis += [emoji.name + ":" + str(emoji.id) for emoji in guild.emojis if
                                emoji.animated]

        # 가챠 키가 없다면 추가
        user_gacha_init(user_data, user_id)

        if user_data[user_id]['gacha']['value'] == 0:
            reply = "보유한 컬렉션이 없습니다"
            await ctx.reply(reply)
        else:
            #보유한 컬렉션을 반환
            owned_items = [f"<a:{full_emojis[i]}>" for i in range(len(full_emojis)) if user_data[user_id]['gacha']['value'] & (1 << i) != 0]
            # 10개씩 끊어서 보여줌
            for i in range(0, len(owned_items), 10):
                reply = "".join(owned_items[i:i+10])
                if i == 0:
                    await ctx.reply(reply)
                else:
                    await ctx.send(reply)