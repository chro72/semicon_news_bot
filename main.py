import os
import requests
import feedparser
import google.generativeai as genai

# 1. 환경 변수에서 비밀키 불러오기
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini AI 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 무료 RSS 피드 주소 (엔비디아, TSMC, 반도체 전체 뉴스)
RSS_URLS = [
    "https://seekingalpha.com/symbol/NVDA.xml",
    "https://seekingalpha.com/symbol/TSM.xml",
    "https://news.google.com/rss/search?q=semiconductor+stock&hl=en-US&gl=US&ceid=US:en"
]

def fetch_latest_news():
    news_items = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:  # 피드당 최신 2개 수집
            news_items.append(f"제목: {entry.title}\n내용: {entry.get('summary', '내용 없음')}")
    return "\n---\n".join(news_items[:5])  # 상위 5개 정리

def summarize_and_translate(text):
    prompt = f"""
    당신은 미국 반도체 주식 전문 분석가입니다. 
    아래 수집된 최신 뉴스들을 바탕으로 한국어로 완벽하게 번역하고 핵심 요점을 정리해 주세요.

    [작성 양식]
    1. 💡 오늘의 반도체 핵심 요약 (3줄)
    2. 🔍 주요 종목/이슈별 상세 내용

    뉴스 데이터:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    raw_news = fetch_latest_news()
    summary = summarize_and_translate(raw_news)
    send_telegram_message(summary)
