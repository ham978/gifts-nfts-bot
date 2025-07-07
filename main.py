import logging
import asyncio
import aiohttp
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# إعدادات اللوج
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# بيانات البوت
TOKEN = "7438194972:AAFpPmLMbvJz6841CmDXDhqvSqlGMkNUvZw"
CHAT_ID = "7438194972"  # ID تاعك

bot = Bot(token=TOKEN)

# فلور مبدئي لكل سلسلة
floor_prices = {}

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يخدم! رايح يراقب سوق Tonnel وMrkt.io ويعلمك بأي فرصة 🔥")

# جلب بيانات السوق
async def fetch_market_data():
    urls = [
        "https://api.getgems.io/nft/items?limit=100&order_by=price&owner=marketplace&sale_type=fixed_price",
        "https://mrkt.io/api/v1/nfts?limit=100&sort=price_asc"
    ]
    nfts = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if "nft_items" in data:
                        items = data["nft_items"]
                    elif "nfts" in data:
                        items = data["nfts"]
                    else:
                        items = []
                    nfts.extend(items)
            except Exception as e:
                logging.error(f"خطأ في جلب السوق: {e}")
    return nfts

# مقارنة السعر وإرسال تنبيه
async def check_deals():
    nfts = await fetch_market_data()
    for nft in nfts:
        try:
            # التحقق من المصدر
            if "metadata" in nft:
                name = nft["metadata"].get("name", "No name")
                collection = nft.get("collection", {}).get("name", "Unknown")
                image = nft["metadata"].get("preview", nft["metadata"].get("image", ""))
                price = float(nft["price"]) / 10**9
                link = f"https://getgems.io/nft/{nft['address']}" if "address" in nft else "https://mrkt.io"

            else:
                name = nft.get("name", "Unknown")
                collection = nft.get("collection_slug", "Unknown")
                image = nft.get("image_url", "")
                price = float(nft["price"]) / 10**9
                link = f"https://mrkt.io/nft/{nft['slug']}" if "slug" in nft else "https://mrkt.io"

            # فلور برايس لكل كوليكشن
            key = collection.lower()
            if key not in floor_prices or price < floor_prices[key]:
                floor_prices[key] = price

            # مقارنة السعر الحالي بالفلور
            floor = floor_prices[key]
            if price <= floor * 0.85:
                text = f"🔥 فرصة!\n\n📛 {name}\n💎 الكوليكشن: {collection}\n💰 السعر: {price:.2f} TON\n\n📎 [رابط العرض]({link})"
                await bot.send_photo(chat_id=CHAT_ID, photo=image, caption=text, parse_mode="Markdown")
        except Exception as e:
            logging.warning(f"خطأ في NFT: {e}")

# جدولة المراقبة كل دقيقة
async def run_monitor():
    while True:
        await check_deals()
        await asyncio.sleep(60)

# التشغيل
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    loop = asyncio.get_event_loop()
    loop.create_task(run_monitor())

    app.run_polling()


        
