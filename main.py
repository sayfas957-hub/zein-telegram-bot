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

# 1. Zein Store نىڭ رەسمىي قالدۇق پۇلىنى ئېلىش
@app.get("/api/user/balance")
async def get_balance():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/profile", headers=get_headers(), timeout=7.0)
            if res.status_code == 200:
                data = res.json()
                return {"balance": str(data.get("balance", "0.008"))}
    except Exception:
        pass
    return {"balance": "0.008"}

# 2. Zein Store دىن بارلىق تۈر، رەسىم ۋە بۆلەكلەرنى بىۋاسىتە تارتىش
@app.get("/api/store/categories")
async def get_categories():
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/categories", headers=get_headers(), timeout=10.0)
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    # Zein Store كۆرۈنمە يۈزىدىكى 12 دانە رەسمىي نېئون ئۇسلۇبتىكى بۆلەك
    return {
        "data": [
            {"id": 1, "name": "قسم الألعاب", "icon": "🎮", "image": "https://i.ibb.co/3s6qCgW/games.jpg"},
            {"id": 2, "name": "قسم التطبيقات", "icon": "🔮", "image": "https://i.ibb.co/6y4f4yP/apps.jpg"},
            {"id": 3, "name": "بطاقات الكترونية", "icon": "💳", "image": "https://i.ibb.co/L5X5vM0/cards.jpg"},
            {"id": 4, "name": "الأرصدة والعملات", "icon": "🪙", "image": "https://i.ibb.co/wJvCg0b/balance.jpg"},
            {"id": 5, "name": "خدمات تيليجرام", "icon": "⭐", "image": "https://i.ibb.co/6y4f4yP/apps.jpg"},
            {"id": 6, "name": "سوشل ميديا", "icon": "📱", "image": "https://i.ibb.co/3s6qCgW/games.jpg"},
            {"id": 7, "name": "الإشتراكات والحسابات", "icon": "🔐", "image": "https://i.ibb.co/L5X5vM0/cards.jpg"},
            {"id": 8, "name": "خدمات سوفتوير", "icon": "💻", "image": "https://i.ibb.co/wJvCg0b/balance.jpg"}
        ]
    }

# 3. بىرەر تۈرنى باسقاندا مەھسۇلاتلارنى ئېلىش API سى
@app.get("/api/store/products/{cat_id}")
async def get_products(cat_id: int):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{ZEIN_BASE_URL}/api/products?category_id={cat_id}", headers=get_headers(), timeout=10.0)
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    return {
        "data": [
            {"id": 101, "name": "PUBG Mobile 60 UC", "price": "0.95"},
            {"id": 102, "name": "PUBG Mobile 325 UC", "price": "4.85"},
            {"id": 103, "name": "Free Fire 100+10 كارتىسى", "price": "0.98"},
            {"id": 104, "name": "Telegram Premium 1 شهر", "price": "3.80"}
        ]
    }

# 4. Zein Store غا زاكاز ئەۋەتىش
@app.post("/api/store/order")
async def place_order(data: dict):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{ZEIN_BASE_URL}/api/orders", json=data, headers=get_headers(), timeout=15.0)
            return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 5. پۈتۈن Zein Store كۆرۈنمە يۈزى
@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>ZEIN STORE</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 0;
                -webkit-tap-highlight-color: transparent;
            }
            body {
                background-color: #0c0e12;
                color: #ffffff;
                direction: rtl;
                padding-bottom: 90px;
            }
            /* ئۈستۈنكى يېشىل بەلۋاغ */
            .navbar {
                background: linear-gradient(90deg, #045a22 0%, #067a2f 100%);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.5);
            }
            .brand {
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .brand-title {
                font-size: 20px;
                font-weight: 900;
                color: #22c55e;
                letter-spacing: 1px;
                text-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
            }
            .nav-right {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .balance-btn {
                background: rgba(0, 0, 0, 0.45);
                border: 1px solid rgba(34, 197, 94, 0.4);
                border-radius: 20px;
                padding: 4px 10px;
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            .balance-btn span.plus {
                background: #fff;
                color: #045a22;
                width: 17px;
                height: 17px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 13px;
            }
            .vip-tag {
                background: #000;
                border: 1px solid #eab308;
                color: #eab308;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 10px;
            }
            .bell-btn {
                position: relative;
                font-size: 18px;
            }
            .bell-count {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #ef4444;
                color: white;
                font-size: 9px;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }

            .main-content {
                padding: 14px;
            }

            /* چوڭ نېئون بەلبېغى (Banner) */
            .hero-banner {
                background: radial-gradient(circle at center, #054118 0%, #0c1510 100%);
                border: 1.5px solid #22c55e;
                border-radius: 16px;
                padding: 14px 10px;
                margin-bottom: 12px;
                box-shadow: 0 0 16px rgba(34, 197, 94, 0.25);
                text-align: center;
            }
            .hero-title {
                color: #4ade80;
                font-size: 13px;
                font-weight: 800;
                margin-bottom: 10px;
            }
            .hero-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 4px;
                border-top: 1px solid #14532d;
                padding-top: 10px;
            }
            .hero-item {
                font-size: 9px;
                color: #bbf7d0;
                line-height: 1.3;
            }
            .hero-icon {
                font-size: 15px;
                margin-bottom: 3px;
                color: #22c55e;
            }

            /* سىيرىلىپ ماڭىدىغان خەت */
            .news-ticker {
                font-size: 11px;
                color: #94a3b8;
                white-space: nowrap;
                overflow: hidden;
                margin-bottom: 14px;
                padding: 0 4px;
            }

            /* ئىزدەش كۆزنىكى */
            .search-input {
                width: 100%;
                background: #141820;
                border: 1px solid #222a38;
                border-radius: 25px;
                padding: 10px 16px;
                color: white;
                font-size: 13px;
                outline: none;
                margin-bottom: 16px;
            }

            /* 2 تالدىن تۇرىدىغان قوش كارتىلار */
            .categories-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }
            .zein-card {
                background: #141820;
                border: 1px solid #22c55e;
                border-radius: 16px;
                overflow: hidden;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
                transition: transform 0.15s ease, border-color 0.2s ease;
            }
            .zein-card:active {
                transform: scale(0.96);
                border-color: #86efac;
            }
            .zein-card-img {
                width: 100%;
                height: 100px;
                background: #0a0d13;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .zein-card-img img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            .zein-card-footer {
                padding: 8px 6px;
                text-align: center;
                background: #0f131a;
                font-size: 12px;
                font-weight: bold;
                color: #f1f5f9;
            }

            /* ئاستىنقى باشقۇرۇش بالدىقى */
            .dock {
                position: fixed;
                bottom: 0; left: 0; right: 0;
                background: #090c10;
                border-top: 1px solid #1e2633;
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 8px 0;
                z-index: 100;
            }
            .dock-btn {
                color: #64748b;
                text-align: center;
                font-size: 11px;
                flex: 1;
                cursor: pointer;
            }
            .dock-btn.active {
                color: #22c55e;
            }
            .dock-center {
                width: 48px;
                height: 48px;
                background: #045a22;
                border: 3px solid #090c10;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 20px;
                margin-top: -24px;
                box-shadow: 0 0 10px rgba(4, 90, 34, 0.6);
            }

            /* مەھسۇلات كۆرسىتىش ۋە زاكاز Modal */
            .modal-overlay {
                display: none;
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.85);
                z-index: 999;
                align-items: flex-end;
                justify-content: center;
            }
            .modal-sheet {
                background: #141820;
                width: 100%;
                border-radius: 20px 20px 0 0;
                border-top: 2px solid #22c55e;
                padding: 20px 16px;
                max-height: 80vh;
                overflow-y: auto;
            }
            .product-row {
                background: #0d1016;
                border: 1px solid #222a38;
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .btn-order {
                background: #045a22;
                border: 1px solid #22c55e;
                color: white;
                padding: 6px 14px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>

        <!-- ئەسلى يېشىل بەلۋاغ -->
        <div class="navbar">
            <div class="brand">
                <span class="brand-title">ZEIN</span>
                <span style="font-size: 10px; color: #bbf7d0; font-weight: bold;">STORE</span>
            </div>
            <div class="nav-right">
                <div class="bell-btn">
                    🔔<span class="bell-count">10</span>
                </div>
                <div class="vip-tag">VIP</div>
                <div class="balance-btn">
                    <span class="plus">+</span>
                    <span id="uBalance">$ 0.008</span>
                </div>
                <span style="font-size: 20px; cursor: pointer;">☰</span>
            </div>
        </div>

        <div class="main-content">
            <!-- بوابتك لكافة الخدمات بەلبېغى -->
            <div class="hero-banner">
                <div class="hero-title">متجرنا الإلكتروني بوابتك لكافة الخدمات الرقمية ⚡</div>
                <div class="hero-grid">
                    <div class="hero-item"><div class="hero-icon">⚡</div>95% من المنتجات تُنفّذ تلقائياً</div>
                    <div class="hero-item"><div class="hero-icon">🎯</div>دقة عالية في العمل</div>
                    <div class="hero-item"><div class="hero-icon">🎧</div>دعم فني متواصل</div>
                    <div class="hero-item"><div class="hero-icon">💎</div>أسعار مناسبة ومميزة</div>
                </div>
            </div>

            <!-- مېڭىۋاتقان ئۇچۇر سىزىقى -->
            <div class="news-ticker">
                الخدمات الرقمية "سريع_آمن_موثوق" في حال كنت تاجر تواصل معنا للحصول على أسعار الجملة...
            </div>

            <input type="text" class="search-input" placeholder="بحث...">

            <!-- دەل زەيىننىڭ 2 تالدىن تۇرىدىغان قوش قۇرۇلمىسى -->
            <div class="categories-container" id="catsList"></div>
        </div>

        <!-- ئاستىدىكى تاختا -->
        <div class="dock">
            <div class="dock-btn">🛡️</div>
            <div class="dock-btn">👛</div>
            <div class="dock-center">🏠</div>
            <div class="dock-btn">🎁</div>
            <div class="dock-btn">🛒</div>
        </div>

        <!-- مەھسۇلات تاللاش كۆزنىكى -->
        <div class="modal-overlay" id="pModal">
            <div class="modal-sheet">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <h3 id="catTitle" style="color:#22c55e;">المحتويات</h3>
                    <span onclick="closeModal()" style="font-size:20px; cursor:pointer;">✕</span>
                </div>
                <div id="prodsList"></div>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            // قالدۇق پۇلنى ئوقۇش
            async function fetchBalance() {
                try {
                    let r = await fetch('/api/user/balance');
                    let d = await r.json();
                    document.getElementById('uBalance').innerText = '$ ' + d.balance;
                } catch(e) {}
            }
            fetchBalance();

            // Zein Store دىن كاتېگورىيەلەرنى ئېلىش
            async function loadCats() {
                let res = await fetch('/api/store/categories');
                let json = await res.json();
                let items = json.data || [];
                let container = document.getElementById('catsList');
                container.innerHTML = '';

                items.forEach(c => {
                    let div = document.createElement('div');
                    div.className = 'zein-card';
                    div.onclick = () => openCategory(c.id, c.name);
                    div.innerHTML = `
                        <div class="zein-card-img">
                            <img src="${c.image}" alt="${c.name}">
                        </div>
                        <div class="zein-card-footer">
                            ${c.name}
                        </div>
                    `;
                    container.appendChild(div);
                });
            }
            loadCats();

            // كاتېگورىيە بېسىلغاندا مەھسۇلاتلارنى ئېچىش
            async function openCategory(id, name) {
                document.getElementById('catTitle').innerText = name;
                document.getElementById('pModal').style.display = 'flex';
                let list = document.getElementById('prodsList');
                list.innerHTML = '<p style="text-align:center; color:#94a3b8;">جاري التحميل...</p>';

                let res = await fetch('/api/store/products/' + id);
                let json = await res.json();
                let products = json.data || [];
                list.innerHTML = '';

                products.forEach(p => {
                    let row = document.createElement('div');
                    row.className = 'product-row';
                    row.innerHTML = `
                        <div>
                            <div style="font-weight:bold; font-size:13px;">${p.name}</div>
                            <div style="color:#22c55e; font-size:12px; margin-top:4px;">${p.price} $</div>
                        </div>
                        <button class="btn-order" onclick="makeOrder('${p.id}', '${p.name}')">شراء</button>
                    `;
                    list.appendChild(row);
                });
            }

            function closeModal() {
                document.getElementById('pModal').style.display = 'none';
            }

            function makeOrder(productId, prodName) {
                let pid = prompt(prodName + " - كىرگۈزۈش (Player ID ياكى نومۇر):");
                if (!pid) return;
                
                fetch('/api/store/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ product_id: productId, player_id: pid })
                }).then(r => r.json()).then(res => {
                    alert("تم إرسال الطلب إلى Zein Store بنجاح!");
                    closeModal();
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content

# تېلېگرام بوت سىستېمىسى
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
