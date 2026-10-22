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

@app.get("/api/categories")
async def get_categories():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/categories", headers=get_headers(), timeout=10.0)
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    return {
        "data": [
            {"id": 1, "name": "العاب", "image": "https://cdn-icons-png.flaticon.com/512/686/686589.png"},
            {"id": 2, "name": "التطبيقات", "image": "https://cdn-icons-png.flaticon.com/512/888/888839.png"},
            {"id": 3, "name": "الرصيد", "image": "https://cdn-icons-png.flaticon.com/512/2933/2933116.png"},
            {"id": 4, "name": "البطاقات", "image": "https://cdn-icons-png.flaticon.com/512/9334/9334584.png"},
            {"id": 5, "name": "سوشل ميديا", "image": "https://cdn-icons-png.flaticon.com/512/1384/1384060.png"},
            {"id": 6, "name": "مدفوعات الكترونية", "image": "https://cdn-icons-png.flaticon.com/512/1019/1019607.png"},
            {"id": 7, "name": "الإشتراكات والحسابات", "image": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png"},
            {"id": 8, "name": "خدمات سوفتوير", "image": "https://cdn-icons-png.flaticon.com/512/2092/2092663.png"},
            {"id": 9, "name": "فواتير الأنترنت", "image": "https://cdn-icons-png.flaticon.com/512/2885/2885417.png"},
            {"id": 10, "name": "خدمات تيليجرام", "image": "https://cdn-icons-png.flaticon.com/512/2111/2111646.png"},
            {"id": 11, "name": "إستضافات وسيرفرات", "image": "https://cdn-icons-png.flaticon.com/512/4248/4248332.png"},
            {"id": 12, "name": "الارقام الإفتراضية", "image": "https://cdn-icons-png.flaticon.com/512/806/806642.png"}
        ]
    }

@app.post("/api/order")
async def place_order(data: dict):
    # خېرىدار زاكاز قىلغاندا ئىشلەيدىغان زاكاز قىسمى
    return {"status": "success", "message": "تم استلام الطلب بنجاح"}

@app.get("/", response_class=HTMLResponse)
async def serve_shop():
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
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>MaxStore</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {{
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 0;
                -webkit-tap-highlight-color: transparent;
            }}
            body {{
                background-color: #0b0f19;
                color: #ffffff;
                padding: 12px 14px 75px 14px;
                direction: rtl;
            }}
            .top-bar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
            }}
            .balance-box {{
                display: flex;
                align-items: center;
                background-color: #171d2d;
                border: 1px solid #232d42;
                border-radius: 20px;
                padding: 4px 10px;
                gap: 6px;
            }}
            .plus-btn {{
                background: #4f46e5;
                color: #fff;
                width: 22px;
                height: 22px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                font-size: 14px;
                font-weight: bold;
            }}
            .balance-amount {{
                font-size: 13px;
                font-weight: bold;
                color: #f1f5f9;
            }}
            .coin-icon {{
                color: #f59e0b;
                font-size: 14px;
            }}
            .actions-box {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .icon-btn {{
                background: #171d2d;
                border: 1px solid #232d42;
                border-radius: 50%;
                width: 34px;
                height: 34px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                position: relative;
            }}
            .badge {{
                position: absolute;
                top: -3px;
                right: -3px;
                background: #ef4444;
                color: white;
                font-size: 9px;
                border-radius: 50%;
                width: 14px;
                height: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .search-container {{
                margin-bottom: 18px;
            }}
            .search-input {{
                width: 100%;
                background: #131926;
                border: 1px solid #232d42;
                padding: 11px 14px;
                border-radius: 22px;
                color: white;
                font-size: 13px;
                outline: none;
                text-align: right;
            }}
            .section-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 14px;
            }}
            .section-title {{
                font-size: 15px;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .bar-mark {{
                width: 4px;
                height: 16px;
                background: #4f46e5;
                border-radius: 2px;
            }}
            .category-count {{
                color: #818cf8;
                font-size: 13px;
                font-weight: bold;
            }}
            .categories-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
            }}
            .category-card {{
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
            }}
            .card-visual {{
                width: 100%;
                aspect-ratio: 1;
                background: #131926;
                border: 1.5px solid #232d42;
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            }}
            .card-visual:active {{
                transform: scale(0.92);
                border-color: #4f46e5;
                background: #1e293b;
            }}
            .card-visual img {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                border-radius: 12px;
            }}
            .card-label {{
                font-size: 11px;
                color: #cbd5e1;
                margin-top: 6px;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                width: 100%;
            }}
            /* زاكاز قىلىش سۈزۈلمە كۆزنىكى (Modal) */
            .order-modal {{
                display: none;
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.75);
                z-index: 999;
                align-items: flex-end;
                justify-content: center;
            }}
            .modal-content {{
                background: #131926;
                width: 100%;
                border-radius: 24px 24px 0 0;
                padding: 20px 16px;
                border-top: 1px solid #232d42;
            }}
            .modal-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 12px;
                color: #38bdf8;
            }}
            .input-id {{
                width: 100%;
                padding: 12px;
                background: #0b0f19;
                border: 1px solid #334155;
                border-radius: 12px;
                color: white;
                margin-bottom: 14px;
                outline: none;
                font-size: 14px;
            }}
            .submit-btn {{
                width: 100%;
                background: #4f46e5;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                cursor: pointer;
                margin-bottom: 8px;
            }}
            .cancel-btn {{
                width: 100%;
                background: #1e293b;
                color: #94a3b8;
                padding: 10px;
                border: none;
                border-radius: 12px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="top-bar">
            <div class="balance-box">
                <span class="plus-btn">+</span>
                <span class="balance-amount">{balance_text}$</span>
                <span class="coin-icon">🟡</span>
            </div>
            <div class="actions-box">
                <div class="icon-btn">⚙️</div>
                <div class="icon-btn">🔔<span class="badge">1</span></div>
                <div class="icon-btn">💲</div>
            </div>
        </div>

        <div class="search-container">
            <input type="text" class="search-input" placeholder="ابحث عن منتج...">
        </div>

        <div class="section-header">
            <div class="section-title">
                <span class="bar-mark"></span>
                <span>تصنيفات المتجر</span>
            </div>
            <span class="category-count" id="catCount">12</span>
        </div>

        <div class="categories-grid" id="catGrid"></div>

        <!-- سۈزۈلمە زاكاز كۆزنىكى -->
        <div class="order-modal" id="orderModal">
            <div class="modal-content">
                <div class="modal-title" id="mTitle">زاكاز قىلىش</div>
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 10px;">ID ياكى ئالاقە نومۇرىڭىزنى كىرگۈزۈڭ:</p>
                <input type="text" class="input-id" id="playerId" placeholder="Player ID / Account ID">
                <button class="submit-btn" onclick="confirmOrder()">زاكازنى جەزملەش</button>
                <button class="cancel-btn" onclick="closeModal()">بىكار قىلىش</button>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            let selectedCategory = "";

            function openModal(name) {{
                selectedCategory = name;
                document.getElementById('mTitle').innerText = name + " - طلب جديد";
                document.getElementById('orderModal').style.display = 'flex';
            }}

            function closeModal() {{
                document.getElementById('orderModal').style.display = 'none';
            }}

            function confirmOrder() {{
                let pid = document.getElementById('playerId').value;
                if (!pid) {{
                    alert("ID نى كىرگۈزۈڭ!");
                    return;
                }}
                closeModal();
                tg.sendData(JSON.stringify({{
                    category: selectedCategory,
                    player_id: pid
                }}));
                if (tg.close) tg.close();
            }}

            async function loadCategories() {{
                try {{
                    let response = await fetch('/api/categories');
                    let res = await response.json();
                    let items = res.data || res.categories || [];
                    document.getElementById('catCount').innerText = items.length;
                    
                    let grid = document.getElementById('catGrid');
                    grid.innerHTML = '';
                    
                    items.forEach(item => {{
                        let div = document.createElement('div');
                        div.className = 'category-card';
                        div.onclick = function() {{
                            openModal(item.name);
                        }};
                        div.innerHTML = `
                            <div class="card-visual">
                                <img src="${{item.image || 'https://cdn-icons-png.flaticon.com/512/686/686589.png'}}" alt="${{item.name}}">
                            </div>
                            <span class="card-label">${{item.name}}</span>
                        `;
                        grid.appendChild(div);
                    }});
                }} catch (e) {{
                    console.log("Error loading", e);
                }}
            }}
            loadCategories();
        </script>
    </body>
    </html>
    """
    return html_content

# تېلېگرام قىسمى
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://google.com")
    keyboard = [
        [InlineKeyboardButton("🛍 دۇكاننى ئېچىش", web_app=WebAppInfo(url=render_url))]
    ]
    await update.message.reply_text(
        "MaxStore غا كەلگىنىڭىزنى قارشى ئالىمىز!\nتۆۋەندىكى كۇنۇپكىنى بېسىڭ:",
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
