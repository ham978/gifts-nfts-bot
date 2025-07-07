import requests
import time
import telebot
from config import TELEGRAM_BOT_TOKEN, USER_CHAT_ID

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def fetch_nfts():
    urls = {
        "tonnel": "https://tonnel.io/api/gift-nfts",
        "mrkt": "https://api.mrkt.io/v1/gift-nfts",
        "portal": "https://api.getgems.io/v2/gift-nfts"
    }
    all_data = []

    for name, url in urls.items():
        try:
            res = requests.get(url)
            if res.status_code == 200:
                nfts = res.json()
                for nft in nfts:
                    nft["market"] = name
                    all_data.append(nft)
        except Exception as e:
            print(f"خطأ في {name}: {e}")
    return all_data

def filter_good_deals(nfts):
    good_nfts = []
    for nft in nfts:
        try:
            price = float(nft.get("price", 0))
            floor = float(nft.get("floor_price", 0))
            if price > 0 and floor > 0:
                discount = ((floor - price) / floor) * 100
                if discount >= 15:
                    nft["discount"] = round(discount, 2)
                    good_nfts.append(nft)
        except:
            continue
    return good_nfts

def send_alert(message):
    try:
        bot.send_message(USER_CHAT_ID, message, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"فشل إرسال الرسالة: {e}")

def check_gift_nfts():
    nfts = fetch_nfts()
    good_nfts = filter_good_deals(nfts)

    for nft in good_nfts:
        name = nft.get("name", "بدون اسم")
        price = nft.get("price")
        floor = nft.get("floor_price")
        link = nft.get("url", "#")
        market = nft.get("market")
        discount = nft.get("discount")

        message = f"""
🎁 <b>صفقة NFT محتملة ({market})</b>
📛 <b>{name}</b>
💰 <b>السعر:</b> {price} TON
📉 <b>الفلور:</b> {floor} TON
🔻 <b>خصم:</b> {discount}%
🔗 <a href="{link}">رابط الشراء</a>
"""
        send_alert(message)

# ✅ ضروري هذا السطر
if __name__ == "__main__":
    send_alert("✅ البوت بدا يخدم!")
    while True:
        check_gift_nfts()
        time.sleep(120)
