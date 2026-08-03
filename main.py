import os
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

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        send_telegram("❌ Gemini API 키를 찾을 수 없습니다. (Secrets 설정 확인 필요)")
        exit()

    try:
        # 뉴스 수집
        feed = feedparser.parse("https://seekingalpha.com/symbol/NVDA.xml")
        latest_title = feed.entries[0].title if feed.entries else "뉴스 없음"
        
        # 최신 SDK 방식으로 Gemini 호출
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"다음 뉴스 제목을 한국어로 한 줄 요약해 줘: {latest_title}",
        )
        
        send_telegram(f"🎉 성공! 반도체 로봇 정상 동작 완료!\n\n요약 결과:\n{response.text}")

    except Exception as e:
        send_telegram(f"⚠️ 오류 발생:\n{str(e)}")
