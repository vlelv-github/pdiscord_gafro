import random
from googleapiclient.discovery import build
import isodate

YOUTUBE_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxx' # YouTube API 키
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# 유튜브 음악 추천 모듈
def search_music_video_by_genre(genre, max_results=50):
    # YouTube 검색
    request = youtube.search().list(
        q=f'{genre} music',
        part='snippet',
        type='video',
        maxResults=max_results
    )
    response = request.execute()

    # 검색된 동영상 ID 목록 추출
    if 'items' not in response:
        return None

    video_ids = [item['id']['videoId'] for item in response['items']]

    # 2차 검색: 동영상 길이 필터링
    details_request = youtube.videos().list(
        part="contentDetails",
        id=",".join(video_ids)
    )
    details_response = details_request.execute()

    # 10분 이하(600초)의 동영상만 필터링
    valid_videos = []
    for item in details_response.get('items', []):
        duration = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
        if duration <= 600:  # 600초 = 10분
            valid_videos.append(item['id'])

    # 유효한 동영상 중 무작위 선택
    if valid_videos:
        random_video_id = random.choice(valid_videos)
        return f'https://www.youtube.com/watch?v={random_video_id}'


def youtube_setup(bot):
    @bot.command(name='music', aliases=['음악','youtube','音楽'])
    async def random_music(ctx, *genre):
        try:
            music_video_url = search_music_video_by_genre(genre)
            if music_video_url:
                await ctx.send(f'이 음악을 추천한다, 아쎄이! : {music_video_url}')
            else:
                await ctx.send("음악을 찾을 수 없다, 아쎄이!")
        except Exception:
            pass

    @bot.command(name="cat")
    async def send_cat_emoji(ctx):
        emoji_id = 1355984494284243186  # 사용할 이모지 ID
        emoji = f"<a:nyancat:{emoji_id}>"  # 애니메이션 이모지 형식
        await ctx.send(emoji)