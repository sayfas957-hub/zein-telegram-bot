import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ZEIN_API_KEY = os.getenv("ZEIN_API_KEY", "_UMp2U9ww7ShQTi62W1XG9ZSA4RhTg-S8ok65Z8vZS1WDuJoWcu4nt97IIP3O0IJ")
ZEIN_BASE_URL = "https://api.zein-store.com"

app = FastAPI()

def get_headers():
    return {
        "Authorization": f"Bearer {ZEIN_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# 1-بۆلەك: Zein Store دىن كاتېگورىيە ۋە تۈرلەرنى ئاپتوماتىك تارتىش
@app.get("/api/zein/categories")
async def get_zein_categories():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/categories", headers=get_headers(), timeout=10.0)
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    # ئەگەر ئۇلىنىشتا مەسىلە بولسا زاپاس قۇرۇلما
    return {"categories": [{"id": 1, "name": "ئويۇنلار", "icon": "🎮"}, {"id": 2, "name": "كارتىلار", "icon": "💳"}]}

# 2-بۆلەك: خېرىدار ئۈچۈن قالدۇق پۇل ۋە ئاپتوماتىك زاكاز قىلىش
@app.post("/api/zein/order")
async def execute_zein_order(data: dict):
    product_id = data.get("product_id")
    player_id = data.get("player_id")
    payload = {
        "product_id": product_id,
        "player_id": player_id
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{ZEIN_BASE_URL}/api/orders", json=payload, headers=get_headers(), timeout=15.0)
            return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# دۇكان ئاساسىي كۆرۈنمە يۈزى (Frontend)
@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    # قالدۇق پۇلنى ئوقۇش
    balance_text = "0.00"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/profile", headers=get_headers(), timeout=5.0)
            if res.status_code == 200:
                profile = res.json()
                balance_text = str(profile.get("balance", "0.00"))
    except Exception:
        balance_text = "0.00"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ug" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>MaxStore</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {{ background: #0b1120; color: #f8fafc; font-family: sans-serif; padding: 16px; margin: 0; direction: rtl; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .balance {{ background: #1e293b; padding: 8px 16px; border-radius: 20px; color: #38bdf8; font-weight: bold; border: 1px solid #334155; }}
            .search {{ width: 100%; padding: 12px; background: #1e293b; border: 1px solid #334155; border-radius: 12px; color: white; box-sizing: border-box; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
            .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 12px 5px; text-align: center; cursor: pointer; }}
            .card:active {{ background: #2563eb; }}
            .icon {{ font-size: 26px; margin-bottom: 5px; }}
            .title {{ font-size: 11px; color: #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h3 style="margin:0;">MaxStore</h3>
            <div class="balance">{balance_text} $ 💳</div>
        </div>
        <input type="text" class="search" placeholder="مەھسۇلات ئىزدەش...">
        <div class="grid">
            <div class="card" onclick="orderItem('PUBG Mobile')"><div class="icon">🎮</div><div class="title">ئويۇنلار</div></div>
            <div class="card" onclick="orderItem('Telegram Premium')"><div class="icon">⭐</div><div class="title">تېلېگرام</div></div>
            <div class="card" onclick="orderItem('كارتىلار')"><div class="icon">💳</div><div class="title">كارتىلار</div></div>
            <div class="card" onclick="orderItem('ئىنتېرنېت')"><div class="icon">🌐</div><div class="title">ئىنتېرنېت</div></div>
            <div class="card" onclick="orderItem('ئەپلەر')"><div class="icon">📱</div><div class="title">ئەپلەر</div></div>
            <div class="card" onclick="orderItem('TikTok')"><div class="icon">🎵</div><div class="title">TikTok</div></div>
            <div class="card" onclick="orderItem('ھېساباتلار')"><div class="icon">🔐</div><div class="title">ھېساباتلار</div></div>
            <div class="card" onclick="orderItem('مۇلازىمەت')"><div class="icon">🎧</div><div class="title">مۇلازىمەت</div></div>
        </div>
        <script>
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            function orderItem(name) {{
                let id = prompt(name + " ئۈچۈن ئويۇن ياكى تېلېفون ID نى كىرگۈزۈڭ:");
                if (id) {{
                    alert("زاكاز يوللاندى: " + name + " (ID: " + id + ")");
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_content

# تېلېگرام بوت بۇيرۇقلىرى
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://google.com")
    keyboard = [
        [InlineKeyboardButton("🛍 دۇكاننى ئېچىش", web_app=WebAppInfo(url=render_url))]
    ]
    await update.message.reply_text(
        "MaxStore غا كەلگىنىڭىزنى قارشى ئالىمىز!\nتۆۋەندىكى كۇنۇپكىنى بېسىپ بىۋاسىتە زاكاز قىلىڭ:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

bot_app.add_handler(CommandHandler("start", start))

@app.on_event("startup")
async def startup_event():
    await bot_app.initialize()
    await bot_app.start()
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        await bot_app.bot.set_webhook(url=f"{render_url}/telegram")

@app.post("/telegram")
async def telegram_webhook(request: Request):
    req_json = await request.json()
    update = Update.de_json(req_json, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}
