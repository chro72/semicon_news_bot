import os
import time
import requests
import feedparser
from google import genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload)

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
        send_telegram("❌ Gemini API 키를 찾을 수 없습니다.")
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

    # 429 오류 대비 강력한 재시도 안전장치 (최대 5회, 35초 대기)
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=prompt,
            )
            send_telegram(response.text)
            break  # 성공 시 정상 종료
        except Exception as e:
            error_msg = str(e)
            # 429 또는 Quota/Exhausted 관련 문구가 포함된 경우 무조건 재시도
            if ("429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg) and attempt < max_retries - 1:
                time.sleep(35)  # 35초 대기 후 재시도
                continue
            else:
                send_telegram(f"⚠️ 오류 발생:\n{error_msg}")
                break
