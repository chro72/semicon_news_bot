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

if __name__ == "__main__":
    #Secrets 값 정상 수신 여부 확인
    if not GEMINI_API_KEY:
        send_telegram("❌ Gemini API 키를 찾을 수 없습니다. (Secrets 설정 확인 필요)")
        exit()

    try:
        # 뉴스 수집 테스트
        feed = feedparser.parse("https://seekingalpha.com/symbol/NVDA.xml")
        latest_title = feed.entries[0].title if feed.entries else "뉴스 없음"
        
        # Gemini AI 테스트
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"다음 뉴스 제목을 한국어로 한 줄 요약해 줘: {latest_title}",
        )
        
        # 성공 시 메시지 발송
        send_telegram(f"🎉 성공! 반도체 로봇 정상 동작 완료!\n\n요약 결과:\n{response.text}")

    except Exception as e:
        # 오류 발생 시 오류 내용을 텔레그램으로 바로 쏨
        send_telegram(f"⚠️ 오류 발생:\n{str(e)}")
