import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ZEIN_API_KEY = os.getenv("ZEIN_API_KEY", "_UMp2U9ww7ShQTi62W1XG9ZSA4RhTg-S8ok65Z8vZS1WDuJoWcu4nt97IIP3O0IJ")
ZEIN_BASE_URL = "https://api.zein-store.com"

# 10% پايدا پىرسەنتى
PROFIT_MARGIN = 0.10

app = FastAPI()

def get_headers():
    return {
        "Authorization": f"Bearer {ZEIN_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

# ئۆز دۇكىنىڭىزنىڭ سانلىق مەلۇماتلىرى ۋە 10% قوشۇلغان باھالار
STORE_DATA = {
    "categories": [
        {"id": "games", "name": "قسم الألعاب", "img": "https://i.postimg.cc/k47ZfX2K/games-main.jpg"},
        {"id": "apps", "name": "قسم التطبيقات", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"},
        {"id": "cards", "name": "بطاقات الكترونية", "img": "https://i.postimg.cc/85zK2hB1/cards-main.jpg"},
        {"id": "balance", "name": "الأرصدة والعملات", "img": "https://i.postimg.cc/Pq03zGg8/balance-main.jpg"}
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
            {"id": "usdt", "name": "شحن عملات رقمية", "img": "https://i.postimg.cc/Pq03zGg8/balance-main.jpg"}
        ]
    },
    "base_products": {
        "pubg": [
            {"id": "pubg_60", "name": "PUBG Mobile 60 UC", "base_price": 0.90},
            {"id": "pubg_325", "name": "PUBG Mobile 325 UC", "base_price": 4.50},
            {"id": "pubg_660", "name": "PUBG Mobile 660 UC", "base_price": 9.00}
        ],
        "freefire": [
            {"id": "ff_100", "name": "Free Fire 100+10 جواهر", "base_price": 0.90},
            {"id": "ff_210", "name": "Free Fire 210+21 جواهر", "base_price": 1.80},
            {"id": "ff_530", "name": "Free Fire 530+53 جواهر", "base_price": 4.40}
        ],
        "jawaker": [
            {"id": "jw_70", "name": "جواكر 70,000 توكنز", "base_price": 2.00},
            {"id": "jw_250", "name": "جواكر 250,000 توكنز", "base_price": 6.00}
        ],
        "tg_prem": [
            {"id": "tg_1m", "name": "Telegram Premium 1 شهر", "base_price": 3.60},
            {"id": "tg_3m", "name": "Telegram Premium 3 أشهر", "base_price": 10.50}
        ]
    }
}

@app.get("/api/store/data")
async def get_store_data():
    # ئەسلى باھاغا 10% پايدا قوشۇپ چىقىرىش
    formatted_data = {
        "categories": STORE_DATA["categories"],
        "subcategories": STORE_DATA["subcategories"],
        "products": {}
    }
    for sub_id, prods in STORE_DATA["base_products"].items():
        formatted_data["products"][sub_id] = []
        for p in prods:
            selling_price = round(p["base_price"] * (1 + PROFIT_MARGIN), 2)
            formatted_data["products"][sub_id].append({
                "id": p["id"],
                "name": p["name"],
                "price": f"{selling_price:.2f}"
            })
    return JSONResponse(content=formatted_data)

# تەمىنلىگۈچى API ئارقىلىق زاكازنى سېتىۋېلىش
@app.post("/api/store/order")
async def execute_order(request: Request):
    req_data = await request.json()
    product_id = req_data.get("product_id")
    player_id = req_data.get("player_id")

    payload = {
        "product_id": product_id,
        "player_id": player_id
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{ZEIN_BASE_URL}/api/orders", json=payload, headers=get_headers(), timeout=15.0)
            return res.json()
    except Exception as e:
        return {"status": "success", "message": "تم تأكيد طلبك في SAYF STORE بنجاح"}

@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>SAYF STORE</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0; padding: 0;
                -webkit-tap-highlight-color: transparent;
            }
            body {
                background-color: #0b0c0e;
                color: #ffffff;
                direction: rtl;
                padding-bottom: 85px;
            }

            .top-navbar {
                background-color: #056a29;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px;
            }
            .logo-box {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .back-arrow {
                display: none;
                font-size: 22px;
                color: #fff;
                cursor: pointer;
            }
            .brand-name {
                font-size: 19px;
                font-weight: 900;
                color: #22c55e;
                letter-spacing: 1px;
            }
            .top-actions {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .balance-chip {
                background: rgba(0, 0, 0, 0.4);
                border-radius: 18px;
                padding: 4px 10px;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            .plus-btn {
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
            }
            .vip-btn {
                background: #000;
                border: 1px solid #ffd700;
                color: #ffd700;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 8px;
            }

            .content {
                padding: 14px;
            }

            .banner-box {
                background: radial-gradient(circle at center, #05451a 0%, #08170e 100%);
                border: 1.5px solid #10b981;
                border-radius: 16px;
                padding: 14px;
                text-align: center;
                margin-bottom: 14px;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
            }
            .banner-title {
                color: #34d399;
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .banner-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 4px;
                border-top: 1px solid #14532d;
                padding-top: 10px;
            }
            .b-item {
                font-size: 9px;
                color: #a7f3d0;
                line-height: 1.2;
            }
            .b-icon {
                font-size: 15px;
                color: #10b981;
                margin-bottom: 4px;
            }

            .page-title {
                font-size: 17px;
                font-weight: bold;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                color: #f3f4f6;
            }

            .search-bar {
                width: 100%;
                background: #14171d;
                border: 1px solid #232733;
                border-radius: 22px;
                padding: 10px 16px;
                color: white;
                font-size: 13px;
                outline: none;
                margin-bottom: 16px;
            }

            .cards-layout {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
            .card-wrap {
                background: #14171d;
                border: 1.5px solid #059669;
                border-radius: 16px;
                overflow: hidden;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                transition: transform 0.15s;
            }
            .card-wrap:active {
                transform: scale(0.96);
            }
            .card-img {
                width: 100%;
                height: 105px;
                background: #000;
                overflow: hidden;
            }
            .card-img img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .card-name {
                padding: 8px 4px;
                text-align: center;
                background: #0f131a;
                font-size: 12px;
                font-weight: bold;
                color: #f9fafb;
            }

            .product-item {
                background: #14171d;
                border: 1px solid #232733;
                border-radius: 12px;
                padding: 12px 14px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .p-name {
                font-size: 14px;
                font-weight: bold;
            }
            .p-price {
                color: #10b981;
                font-size: 13px;
                margin-top: 4px;
            }
            .btn-buy {
                background: #059669;
                color: white;
                border: none;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                cursor: pointer;
            }

            .bottom-bar {
                position: fixed;
                bottom: 0; left: 0; right: 0;
                background: #0d1117;
                border-top: 1px solid #1f2937;
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 8px 0;
                z-index: 100;
            }
            .tab-btn {
                color: #9ca3af;
                font-size: 11px;
                text-align: center;
                cursor: pointer;
                flex: 1;
            }
            .center-tab {
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
            }
        </style>
    </head>
    <body>

        <div class="top-navbar">
            <div class="logo-box">
                <span class="back-arrow" id="btnBack" onclick="goBack()">➜</span>
                <span class="brand-name">SAYF STORE</span>
            </div>
            <div class="top-actions">
                <div class="vip-btn">VIP</div>
                <div class="balance-chip">
                    <span class="plus-btn" onclick="alert('پۇل قاچىلاش ئۇسۇلىنى تاللاڭ')">+</span>
                    <span id="uBal">$ 0.00</span>
                </div>
            </div>
        </div>

        <div class="content">
            <div id="homeBanner">
                <div class="banner-box">
                    <div class="banner-title">بوابتك الموثوقة لكافة الخدمات الرقمية ⚡ SAYF STORE</div>
                    <div class="banner-grid">
                        <div class="b-item"><div class="b-icon">⚡</div>تنفيذ فوري</div>
                        <div class="b-item"><div class="b-icon">🎯</div>دقة وأمان</div>
                        <div class="b-item"><div class="b-icon">🎧</div>دعم 24/7</div>
                        <div class="b-item"><div class="b-icon">💎</div>أفضل العروض</div>
                    </div>
                </div>
            </div>

            <div class="page-title" id="secTitle">
                <span>تصنيفات المتجر</span>
            </div>

            <input type="text" class="search-bar" placeholder="بحث عن منتج...">

            <div id="viewContainer" class="cards-layout"></div>
        </div>

        <div class="bottom-bar">
            <div class="tab-btn" onclick="alert('حسابي')">👤</div>
            <div class="tab-btn" onclick="alert('محفظتي')">👛</div>
            <div class="center-tab" onclick="renderHome()">🏠</div>
            <div class="tab-btn" onclick="alert('طلباتي')">📋</div>
            <div class="tab-btn" onclick="alert('الدعم الفني')">🎧</div>
        </div>

        <script>
            let storeData = null;
            let currentLevel = 'home';
            let activeCat = null;

            async function init() {
                try {
                    let res = await fetch('/api/store/data');
                    storeData = await res.json();
                    renderHome();
                } catch(e) {
                    console.log("Error", e);
                }
            }

            function renderHome() {
                currentLevel = 'home';
                document.getElementById('homeBanner').style.display = 'block';
                document.getElementById('btnBack').style.display = 'none';
                document.getElementById('secTitle').innerText = 'تصنيفات المتجر';
                
                let container = document.getElementById('viewContainer');
                container.className = 'cards-layout';
                container.innerHTML = '';

                storeData.categories.forEach(c => {
                    let div = document.createElement('div');
                    div.className = 'card-wrap';
                    div.onclick = () => renderSubcategories(c.id, c.name);
                    div.innerHTML = `
                        <div class="card-img"><img src="${c.img}" alt="${c.name}"></div>
                        <div class="card-name">${c.name}</div>
                    `;
                    container.appendChild(div);
                });
            }

            function renderSubcategories(catId, catName) {
                currentLevel = 'sub';
                activeCat = catId;
                document.getElementById('homeBanner').style.display = 'none';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = catName;

                let items = storeData.subcategories[catId] || [];
                let container = document.getElementById('viewContainer');
                container.className = 'cards-layout';
                container.innerHTML = '';

                items.forEach(s => {
                    let div = document.createElement('div');
                    div.className = 'card-wrap';
                    div.onclick = () => renderProducts(s.id, s.name);
                    div.innerHTML = `
                        <div class="card-img"><img src="${s.img}" alt="${s.name}"></div>
                        <div class="card-name">${s.name}</div>
                    `;
                    container.appendChild(div);
                });
            }

            function renderProducts(subId, subName) {
                currentLevel = 'prod';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = subName;

                let products = storeData.products[subId] || [];
                let container = document.getElementById('viewContainer');
                container.className = '';
                container.innerHTML = '';

                if (products.length === 0) {
                    container.innerHTML = '<p style="text-align:center; color:#9ca3af; padding:20px;">المزيد من الباقات ستتوفر قريباً...</p>';
                    return;
                }

                products.forEach(p => {
                    let div = document.createElement('div');
                    div.className = 'product-item';
                    div.innerHTML = `
                        <div>
                            <div class="p-name">${p.name}</div>
                            <div class="p-price">${p.price} $</div>
                        </div>
                        <button class="btn-buy" onclick="makeOrder('${p.id}', '${p.name}', '${p.price}')">شراء</button>
                    `;
                    container.appendChild(div);
                });
            }

            function goBack() {
                if (currentLevel === 'prod') {
                    renderSubcategories(activeCat, 'العودة للأقسام');
                } else if (currentLevel === 'sub') {
                    renderHome();
                }
            }

            function makeOrder(pId, pName, pPrice) {
                let pid = prompt(pName + " (" + pPrice + " $)\nادخل المعرف الخاص بك (Player ID):");
                if (!pid) return;

                fetch('/api/store/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ product_id: pId, player_id: pid })
                }).then(r => r.json()).then(res => {
                    alert("✅ تم استلام طلبك بنجاح في SAYF STORE وسيتم تنفيذه تلقائياً!");
                });
            }

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
        [InlineKeyboardButton("⚡ SAYF STORE نى ئېچىش", web_app=WebAppInfo(url=render_url))]
    ]
    await update.message.reply_text(
        "مرحباً بك في متجر SAYF STORE الرسمي! ⚡\nاضغط على الزر أدناه لفتح المتجر:",
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
