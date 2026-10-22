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

# Zein Store سانلىق مەلۇمات ئامبىرى
STORE_DATA = {
    "categories": [
        {"id": "games", "name": "قسم الألعاب", "icon": "🎮", "img": "https://i.postimg.cc/k47ZfX2K/games-main.jpg"},
        {"id": "apps", "name": "قسم التطبيقات", "icon": "🔮", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"},
        {"id": "cards", "name": "بطاقات الكترونية", "icon": "💳", "img": "https://i.postimg.cc/85zK2hB1/cards-main.jpg"},
        {"id": "balance", "name": "الأرصدة والعملات", "icon": "🪙", "img": "https://i.postimg.cc/Pq03zGg8/balance-main.jpg"}
    ],
    "subcategories": {
        "games": [
            {"id": "pubg", "name": "قسم ببجي", "img": "https://i.postimg.cc/8PjM3LWy/pubg.jpg"},
            {"id": "freefire", "name": "قسم فري فاير", "img": "https://i.postimg.cc/G307N1sP/freefire.jpg"},
            {"id": "mlbb", "name": "موبايل ليجند", "img": "https://i.postimg.cc/52M6vJ61/mlbb.jpg"},
            {"id": "jawaker", "name": "قسم جواكر", "img": "https://i.postimg.cc/9FmH9xJz/jawaker.jpg"},
            {"id": "8ball", "name": "8BALL POOL", "img": "https://i.postimg.cc/SKM4t2wL/8ball.jpg"},
            {"id": "fcmobile", "name": "FCMobile", "img": "https://i.postimg.cc/44k4xH8t/fcmobile.jpg"}
        ],
        "apps": [
            {"id": "tg_prem", "name": "تيليجرام بريميوم", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"},
            {"id": "tiktok", "name": "عملات تيك توك", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"}
        ],
        "cards": [
            {"id": "google", "name": "بطاقات جوجل بلاي", "img": "https://i.postimg.cc/85zK2hB1/cards-main.jpg"},
            {"id": "itunes", "name": "بطاقات آيتونز", "img": "https://i.postimg.cc/85zK2hB1/cards-main.jpg"}
        ],
        "balance": [
            {"id": "usdt", "name": "شحن باينانس وباي بيت", "img": "https://i.postimg.cc/Pq03zGg8/balance-main.jpg"}
        ]
    },
    "products": {
        "pubg": [
            {"id": 1, "name": "PUBG 60 UC", "price": "0.95"},
            {"id": 2, "name": "PUBG 325 UC", "price": "4.85"},
            {"id": 3, "name": "PUBG 660 UC", "price": "9.60"}
        ],
        "freefire": [
            {"id": 4, "name": "Free Fire 100+10 جواهر", "price": "0.98"},
            {"id": 5, "name": "Free Fire 210+21 جواهر", "price": "1.95"},
            {"id": 6, "name": "Free Fire 530+53 جواهر", "price": "4.80"}
        ],
        "jawaker": [
            {"id": 7, "name": "جواكر 70,000 توكنز", "price": "2.10"},
            {"id": 8, "name": "جواكر 250,000 توكنز", "price": "6.50"}
        ]
    }
}

@app.get("/api/store/data")
async def get_store_data():
    return JSONResponse(content=STORE_DATA)

@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    # قالدۇق پۇلنى Zein API ئارقىلىق تەكشۈرۈش
    bal = "0.008"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/profile", headers=get_headers(), timeout=5.0)
            if res.status_code == 200:
                bal = str(res.json().get("balance", "0.008"))
    except Exception:
        bal = "0.008"

    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>ZEIN STORE</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {{
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0; padding: 0;
                -webkit-tap-highlight-color: transparent;
            }}
            body {{
                background-color: #0b0c0e;
                color: #ffffff;
                direction: rtl;
                padding-bottom: 85px;
            }}

            /* ئۈستۈنكى تاختا */
            .top-navbar {{
                background-color: #056a29;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px;
            }}
            .logo-box {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .back-arrow {{
                display: none;
                font-size: 20px;
                color: #fff;
                cursor: pointer;
            }}
            .brand-name {{
                font-size: 19px;
                font-weight: 900;
                color: #22c55e;
                letter-spacing: 1px;
            }}
            .top-actions {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .balance-chip {{
                background: rgba(0, 0, 0, 0.4);
                border-radius: 18px;
                padding: 4px 10px;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            .plus-btn {{
                background: #fff;
                color: #056a29;
                width: 17px;
                height: 17px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                cursor: pointer;
            }}
            .vip-btn {{
                background: #000;
                border: 1px solid #ffd700;
                color: #ffd700;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 8px;
            }}
            .bell-btn {{
                position: relative;
                font-size: 18px;
            }}
            .badge {{
                position: absolute;
                top: -6px; right: -6px;
                background: #ef4444;
                color: #fff;
                font-size: 9px;
                width: 15px; height: 15px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .content {{
                padding: 14px;
            }}

            /* چوڭ بەلۋاغ */
            .banner-box {{
                background: radial-gradient(circle at center, #05451a 0%, #08170e 100%);
                border: 1.5px solid #10b981;
                border-radius: 16px;
                padding: 14px;
                text-align: center;
                margin-bottom: 14px;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
            }}
            .banner-title {{
                color: #34d399;
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .banner-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 4px;
                border-top: 1px solid #14532d;
                padding-top: 10px;
            }}
            .b-item {{
                font-size: 9px;
                color: #a7f3d0;
                line-height: 1.2;
            }}
            .b-icon {{
                font-size: 15px;
                color: #10b981;
                margin-bottom: 4px;
            }}

            /* ماۋزۇ قىسمى */
            .page-title {{
                font-size: 17px;
                font-weight: bold;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                color: #f3f4f6;
            }}

            .search-bar {{
                width: 100%;
                background: #14171d;
                border: 1px solid #232733;
                border-radius: 22px;
                padding: 10px 16px;
                color: white;
                font-size: 13px;
                outline: none;
                margin-bottom: 16px;
            }}

            /* 2 تالدىن تۇرىدىغان قوش كارتىلار */
            .cards-layout {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }}
            .card-wrap {{
                background: #14171d;
                border: 1.5px solid #059669;
                border-radius: 16px;
                overflow: hidden;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                transition: transform 0.15s;
            }}
            .card-wrap:active {{
                transform: scale(0.96);
            }}
            .card-img {{
                width: 100%;
                height: 105px;
                background: #000;
                overflow: hidden;
            }}
            .card-img img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            .card-name {{
                padding: 8px 4px;
                text-align: center;
                background: #0f131a;
                font-size: 12px;
                font-weight: bold;
                color: #f9fafb;
            }}

            /* زاكاز تىزىملىكى بەلبېغى */
            .product-item {{
                background: #14171d;
                border: 1px solid #232733;
                border-radius: 12px;
                padding: 12px 14px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .p-name {{
                font-size: 14px;
                font-weight: bold;
            }}
            .p-price {{
                color: #10b981;
                font-size: 13px;
                margin-top: 4px;
            }}
            .btn-buy {{
                background: #059669;
                color: white;
                border: none;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                cursor: pointer;
            }}

            /* ئاستىنقى يول باشلاش */
            .bottom-bar {{
                position: fixed;
                bottom: 0; left: 0; right: 0;
                background: #0d1117;
                border-top: 1px solid #1f2937;
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 8px 0;
                z-index: 100;
            }}
            .tab-btn {{
                color: #9ca3af;
                font-size: 11px;
                text-align: center;
                cursor: pointer;
                flex: 1;
            }}
            .center-tab {{
                width: 48px;
                height: 48px;
                background: #056a29;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 20px;
                margin-top: -24px;
                border: 3px solid #0b0c0e;
                box-shadow: 0 4px 10px rgba(5, 106, 41, 0.5);
                cursor: pointer;
            }}
        </style>
    </head>
    <body>

        <div class="top-navbar">
            <div class="logo-box">
                <span class="back-arrow" id="btnBack" onclick="goBack()">➜</span>
                <span class="brand-name">ZEIN STORE</span>
            </div>
            <div class="top-actions">
                <div class="bell-btn" onclick="alert('تەڭشەك ۋە ئۇقتۇرۇشلار')">🔔<span class="badge">10</span></div>
                <div class="vip-btn">VIP</div>
                <div class="balance-chip">
                    <span class="plus-btn">+</span>
                    <span>$ {bal}</span>
                </div>
            </div>
        </div>

        <div class="content">
            <!-- چوڭ لوزۇنكا پەقەت باش بەتتىلا كۆرۈنىدۇ -->
            <div id="homeBanner">
                <div class="banner-box">
                    <div class="banner-title">بوابتك لكافة الخدمات الرقمية ⚡ ZEIN STORE</div>
                    <div class="banner-grid">
                        <div class="b-item"><div class="b-icon">⚡</div>95% تلقائي</div>
                        <div class="b-item"><div class="b-icon">🎯</div>دقة عالية</div>
                        <div class="b-item"><div class="b-icon">🎧</div>دعم متواصل</div>
                        <div class="b-item"><div class="b-icon">💎</div>أفضل سعر</div>
                    </div>
                </div>
            </div>

            <!-- بېكەت ماۋزۇسى -->
            <div class="page-title" id="secTitle">
                <span>تصنيفات المتجر</span>
            </div>

            <input type="text" class="search-bar" placeholder="بحث...">

            <!-- مەزمۇن گىرىدى -->
            <div id="viewContainer" class="cards-layout"></div>
        </div>

        <!-- ئاستىدىكى تاختا -->
        <div class="bottom-bar">
            <div class="tab-btn" onclick="alert('ھېسابات تەڭشەكلىرى')">🛡️</div>
            <div class="tab-btn" onclick="alert('ھەميان ۋە چىقىم')">👛</div>
            <div class="center-tab" onclick="renderHome()">🏠</div>
            <div class="tab-btn" onclick="alert('سوۋغاتلار')">🎁</div>
            <div class="tab-btn" onclick="alert('سېۋەت')">🛒</div>
        </div>

        <script>
            let storeData = null;
            let currentLevel = 'home'; // 'home' | 'sub' | 'prod'
            let activeCat = null;

            async function init() {{
                let res = await fetch('/api/store/data');
                storeData = await res.json();
                renderHome();
            }}

            // 1-دەرىجە: باش بەت ۋە ئاساسىي كاتېگورىيەلەر
            function renderHome() {{
                currentLevel = 'home';
                document.getElementById('homeBanner').style.display = 'block';
                document.getElementById('btnBack').style.display = 'none';
                document.getElementById('secTitle').innerText = 'تصنيفات المتجر';
                
                let container = document.getElementById('viewContainer');
                container.className = 'cards-layout';
                container.innerHTML = '';

                storeData.categories.forEach(c => {{
                    let div = document.createElement('div');
                    div.className = 'card-wrap';
                    div.onclick = () => renderSubcategories(c.id, c.name);
                    div.innerHTML = `
                        <div class="card-img"><img src="${{c.img}}" alt="${{c.name}}"></div>
                        <div class="card-name">${{c.name}}</div>
                    `;
                    container.appendChild(div);
                }});
            }}

            // 2-دەرىجە: تۈرلەر ئىچىگە كىرىش (PUBG, Free Fire, Jawaker...)
            function renderSubcategories(catId, catName) {{
                currentLevel = 'sub';
                activeCat = catId;
                document.getElementById('homeBanner').style.display = 'none';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = catName;

                let items = storeData.subcategories[catId] || [];
                let container = document.getElementById('viewContainer');
                container.className = 'cards-layout';
                container.innerHTML = '';

                items.forEach(s => {{
                    let div = document.createElement('div');
                    div.className = 'card-wrap';
                    div.onclick = () => renderProducts(s.id, s.name);
                    div.innerHTML = `
                        <div class="card-img"><img src="${{s.img}}" alt="${{s.name}}"></div>
                        <div class="card-name">${{s.name}}</div>
                    `;
                    container.appendChild(div);
                }});
            }}

            // 3-دەرىجە: زاكاز تىزىملىكى (UC, كود باھالىرى)
            function renderProducts(subId, subName) {{
                currentLevel = 'prod';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = subName;

                let products = storeData.products[subId] || [
                    {{"id": 1, "name": subName + " باكىتى 1", "price": "1.20"}},
                    {{"id": 2, "name": subName + " باكىتى 2", "price": "3.50"}}
                ];

                let container = document.getElementById('viewContainer');
                container.className = '';
                container.innerHTML = '';

                products.forEach(p => {{
                    let div = document.createElement('div');
                    div.className = 'product-item';
                    div.innerHTML = `
                        <div>
                            <div class="p-name">${{p.name}}</div>
                            <div class="p-price">${{p.price}} $</div>
                        </div>
                        <button class="btn-buy" onclick="orderPrompt('${{p.name}}')">شراء</button>
                    `;
                    container.appendChild(div);
                }});
            }}

            // ئارقىغا قايتىش كۇنۇپكىسى
            function goBack() {{
                if (currentLevel === 'prod') {{
                    renderSubcategories(activeCat, 'تۈرلەرگە قايتىش');
                }} else if (currentLevel === 'sub') {{
                    renderHome();
                }}
            }}

            function orderPrompt(prodName) {{
                let pid = prompt(prodName + " زاكاز قىلىش ئۈچۈن Player ID نى كىرگۈزۈڭ:");
                if (pid) {{
                    alert("زاكاز تەلىپى قوبۇل قىلىندى: " + prodName + " (ID: " + pid + ")");
                }}
            }}

            init();
        </script>
    </body>
    </html>
    """
    return html

# تېلېگرام قىسمى
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://google.com")
    keyboard = [
        [InlineKeyboardButton("⚡ ZEIN STORE نى ئېچىش", web_app=WebAppInfo(url=render_url))]
    ]
    await update.message.reply_text(
        "مرحباً بك في ZEIN STORE!\nبوابتك لكافة الخدمات الرقمية ⚡",
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
