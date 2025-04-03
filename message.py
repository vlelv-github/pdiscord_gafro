from py_users import user_data
def user_data_init(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'chat': {}}

async def def_message(bot, message):
    from py_users import save_data
    if message.author == bot.user:
        return

    # 채팅을 친 유저의 아이디 반환
    user_id = str(message.author.id)
    channel_id = str(message.channel.id)

    # 유저 데이터가 없다면 생성
    user_data_init(user_id)

    #유저 데이터에 채널에 대한 채팅 기록이 없다면 생성
    if channel_id not in user_data[user_id]['chat']:
        user_data[user_id]['chat'][channel_id] = 0

    user_data[user_id]['chat'][channel_id] += 1

    # 변경된 데이터를 파일에 저장
    save_data()

    await bot.process_commands(message)

