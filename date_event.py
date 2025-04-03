from datetime import datetime
from py_users import DATA
import os
from gacha import init_ticket

DAY_FILE = DATA + "\\date.txt"

#디렉토리가 없으면 생성
if not os.path.exists(DATA):
    os.makedirs(DATA)

def create_today(user_data):
    now_day = datetime.today().strftime("%Y%m%d")
    # 파일이 있으면 읽어
    if os.path.exists(DAY_FILE):
        f = open(DAY_FILE, 'r')
        old_day = f.read()
        f.close()
        # 날짜가 달라지면 초기화
        if old_day != now_day:
            init_ticket(user_data)

    f = open(DAY_FILE, 'w')
    f.write(now_day)
    f.close()