import os
import requests
import feedparser
from google import genai

# 1. 환경 변수 체크
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload)

# 2. 무료 RSS 피드 수집
RSS_URLS = [
    "https://seekingalpha.com/symbol/NVDA.xml",
    "https://seekingalpha.com/symbol/TSM.xml",
    "https://news.google.com/rss/search?q=semiconductor+stock&hl=en-US&gl=US&ceid=US:en"
]

def fetch_latest_news():
    news_items = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            news_items.append(f"제목: {entry.title}\n내용: {entry.get('summary', '내용 없음')}")
    return "\n---\n".join(news_items[:5])

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        send_telegram("❌ Gemini API 키를 찾을 수 없습니다. (Secrets 설정 확인 필요)")
        exit()

    raw_news = fetch_latest_news()
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    당신은 미국 반도체 주식 전문 분석가입니다. 
    아래 수집된 최신 뉴스들을 바탕으로 한국어로 완벽하게 번역하고 핵심 요점을 정리해 주세요.

    [작성 양식]
    1. 💡 오늘의 반도체 핵심 요약 (3줄)
    2. 🔍 주요 종목/이슈별 상세 내용

    뉴스 데이터:
    {raw_news}
    """

    # 가장 안정적이고 무료 한도가 여유로운 gemini-1.5-flash 모델 적용
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        send_telegram(response.text)
    except Exception as e:
        send_telegram(f"⚠️ 오류 발생:\n{str(e)}")
