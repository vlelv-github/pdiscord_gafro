import requests, discord
from bs4 import BeautifulSoup

random_url = 'https://www.iwannawiki.com/fangamelist/random'

tool = ['tool', '툴', 'ツール']
boss = ['boss', '보스', 'ボス']
scratch = ['Scratch', '스크래치', 'スクラッチ']
engine = ['engine', '엔진', 'エンジン']
medley = ['medley', '메들리', 'メドレー']
puzzle = ['puzzle', '퍼즐', 'パズル']
adventure = ['adventure', '어드벤쳐', '道中']
special = ['special', '스페셜', '特殊']
needle = ['needle', 'spike', '가시', '針ゲ']
avoidance = ['avoidance', 'barrage', '탄막', '耐久']

def is_in_list(user_input, word_list):
    return user_input.lower() in (word.lower() for word in word_list)

async def get_random_all(ctx, url = random_url):
    res = requests.get(url)

    if res.status_code != 200:
        print("get 요청 실패")
    else:
        print("get 요청 성공")
        content = BeautifulSoup(res.text, 'html.parser')

        # 게임 이름 추출
        s_name = 'body > main > div > div > div.col-md-8.col-12.d-block > section.mb-3 > article > div.card-header > h3'
        game_name = content.select_one(s_name)
        for span in game_name.find_all('span'):
            span.extract()
        game_name = game_name.get_text(strip=True, separator=' ')

        # 제작자 추출
        s_creator = 'body > main > div > div > div.col-md-8.col-12.d-block > section.mb-3 > article > div.card-body > div:nth-child(3) > div.card-body > div > a'
        creator = ", ".join([a.get_text(strip=True) for a in content.select(s_creator)])

        # 다운로드 링크 추출
        s_dl = 'body > main > div > div > div.col-md-8.col-12.d-block > section.mb-3 > article > div.card-body > a'
        dl = content.select_one(s_dl)['href']

        print(game_name)
        print(creator)
        print(dl)

        embed = discord.Embed(title = f"**{game_name}**",
                              url = dl,
                              description=f"creator : {creator}")

        await ctx.reply(embed=embed)

async def get_random_creator(ctx, name):
    param = f'?utf8=%E2%9C%93&creator={name}&commit=Search'
    await get_random_all(ctx, random_url + param)

async def get_random_boss(ctx):
    param = f'?tag=ボス'
    await get_random_all(ctx, random_url + param)

async def get_random_adventure(ctx):
    param = f'?tag=道中'
    await get_random_all(ctx, random_url + param)

async def get_random_tool(ctx):
    param = f'?tag=ツール'
    await get_random_all(ctx, random_url + param)

async def get_random_scratch(ctx):
    param = f'?tag=Scratch'
    await get_random_all(ctx, random_url + param)

async def get_random_engine(ctx):
    param = f'?tag=エンジン'
    await get_random_all(ctx, random_url + param)

async def get_random_medley(ctx):
    param = f'?tag=メドレー'
    await get_random_all(ctx, random_url + param)

async def get_random_puzzle(ctx):
    param = f'?tag=パズル'
    await get_random_all(ctx, random_url + param)

async def get_random_special(ctx):
    param = f'?tag=特殊'
    await get_random_all(ctx, random_url + param)

async def get_random_needle(ctx):
    param = f'?tag=針ゲ'
    await get_random_all(ctx, random_url + param)

async def get_random_avoidance(ctx):
    param = f'?tag=耐久'
    await get_random_all(ctx, random_url + param)


def aiwanna_setup(bot):
    @bot.command(name='random', aliases=['랜덤', '랜덤워너', 'ランダム'])
    async def random_command(ctx, *args):
        if len(args) > 0:
            for arg in args:
                if arg.startswith('creator'):
                    await get_random_creator(ctx, "".join(args).split('=')[1])
                    break
                else:
                    if is_in_list(arg, boss):
                        await get_random_boss(ctx)
                    elif is_in_list(arg, adventure):
                        await get_random_adventure(ctx)
                    elif is_in_list(arg, tool):
                        await get_random_tool(ctx)
                    elif is_in_list(arg, scratch):
                        await get_random_scratch(ctx)
                    elif is_in_list(arg, engine):
                        await get_random_engine(ctx)
                    elif is_in_list(arg, medley):
                        await get_random_medley(ctx)
                    elif is_in_list(arg, puzzle):
                        await get_random_puzzle(ctx)
                    elif is_in_list(arg, special):
                        await get_random_special(ctx)
                    elif is_in_list(arg, needle):
                        await get_random_needle(ctx)
                    elif is_in_list(arg, avoidance):
                        await get_random_avoidance(ctx)
                    break
        else:
            await get_random_all(ctx)
