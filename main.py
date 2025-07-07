import requests
import time
import telegram
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "NFT Sniper Bot is running!"

# إعدادات البوت
TELEGRAM_TOKEN = "ضع التوكن هنا"
TELEGRAM_CHAT_ID = "5804001091"  # أو استخدم @hamza345567

bot = telegram.Bot(token=TELEGRAM_TOKEN)

collections = [
    "vintage-cigar", "lol-pop", "tonpunks", "ton-cats", "tonopoly", "tonano", "tonimals", "ton-football", "ton-matrix"
]

def check_market():
    try:
        for collection in collections:
            url = f"https://api.mrkt.io/v1/collections/{collection}/items?sort=price_asc&limit=1"
            res = requests.get(url)
            data = res.json()

            if not data or 'items' not in data:
                continue

            cheapest = data['items'][0]
            price = float(cheapest['priceTon'])
            floor = float(data['floorPriceTon'])

            discount = ((floor - price) / floor) * 100

            if price <= 15 and discount >= 15:
                link = f"https://mrkt.io/asset/{cheapest['address']}"
                message = f"📉 صفقة قوية في: {collection}\n" \
                          f"💰 السعر: {price} TON\n" \
                          f"🏷️ الفلور: {floor} TON\n" \
                          f"🔻 أقل بـ{round(discount, 1)}%\n" \
                          f"🔗 {link}"

                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    except Exception as e:
        print("Error:", e)

# تشغيل البوت في الخلفية
def run_bot():
    while True:
        check_market()
        time.sleep(120)

import threading
threading.Thread(target=run_bot).start()

# تشغيل Flask لنجعل Render يبقي البوت شغال
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
