import os
import json
import sqlite3
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# بۇ يەرگە باياتىن ئېلىۋالغان ئۆزىڭىزنىڭ سانلىق ID سىنى قويىسىز (ئادېمىن تەستىقى ئۈچۈن)
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
# سىزنىڭ خېرىدارلار بىلەن سۆزلىشىدىغان تېلېگرام نامىڭىز (@ سىز)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "sayf_admin")

ZEIN_API_KEY = os.getenv("ZEIN_API_KEY", "_UMp2U9ww7ShQTi62W1XG9ZSA4RhTg-S8ok65Z8vZS1WDuJoWcu4nt97IIP3O0IJ")
ZEIN_BASE_URL = "https://api.zein-store.com"
PROFIT_MARGIN = 0.10

app = FastAPI()

# ==================== سانلىق مەلۇمات ئامبىرى (DATABASE) ====================
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    # ئىشلەتكۈچىلەر جەدۋىلى
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_user_balance(user_id: int):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0.0

def update_user_balance(user_id: int, amount: float):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

# ==================== مەھسۇلاتلار تىزىملىكى ====================
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
            {"id": "jawaker", "name": "قسم جواكر", "img": "https://i.postimg.cc/9FmH9xJz/jawaker.jpg"}
        ],
        "apps": [
            {"id": "tg_prem", "name": "تيليجرام بريميوم", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"},
            {"id": "tiktok", "name": "عملات تيك توك", "img": "https://i.postimg.cc/pT3wzHkW/apps-main.jpg"}
        ],
        "cards": [
            {"id": "google", "name": "بطاقات جوجل بلاي", "img": "https://i.postimg.cc/85zK2hB1/cards-main.jpg"}
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
            {"id": "ff_210", "name": "Free Fire 210+21 جواهر", "base_price": 1.80}
        ],
        "jawaker": [
            {"id": "jw_70", "name": "جواكر 70,000 توكنز", "base_price": 2.00}
        ],
        "tg_prem": [
            {"id": "tg_1m", "name": "Telegram Premium 1 شهر", "base_price": 3.60}
        ]
    }
}

# ==================== FASTAPI API لىرى ====================
@app.get("/api/store/data")
async def get_store_data(user_id: int = 0):
    formatted_data = {
        "user_balance": f"{get_user_balance(user_id):.2f}",
        "admin_contact": f"https://t.me/{ADMIN_USERNAME}",
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

# خېرىدار زاكاز چۈشۈرگەندە بىر تەرەپ قىلىش
@app.post("/api/store/order")
async def execute_order(request: Request):
    data = await request.json()
    u_id = data.get("user_id")
    p_name = data.get("product_name")
    p_price = float(data.get("price", 0))
    player_id = data.get("player_id")

    current_bal = get_user_balance(u_id)
    if current_bal < p_price:
        return {"status": "error", "message": "قالدۇق پۇلىڭىز يەتمىدى! ئادېمىن بىلەن ئالاقىلىشىپ پۇل قاچىلاڭ."}

    # قالدۇق پۇلنى كېمەيتىش
    update_user_balance(u_id, -p_price)

    # ئادېمىنغا بىۋاسىتە زاكاز ئۇچۇرىنى تېلېگرامدا يوللاش
    order_msg = (
        f"🚨 <b>يېڭى زاكاز چۈشتى! (SAYF STORE)</b>\n\n"
        f"👤 <b>خېرىدار ID:</b> <code>{u_id}</code>\n"
        f"📦 <b>مەھسۇلات:</b> {p_name}\n"
        f"💰 <b>باھاسى:</b> ${p_price}\n"
        f"🎯 <b>تولدۇرۇش ID (Player ID):</b> <code>{player_id}</code>\n\n"
        f"<i>قالدۇقتىن پۇل تۇتۇلدى، زاكازنى بېجىرىڭ!</i>"
    )
    try:
        await bot_app.bot.send_message(chat_id=ADMIN_ID, text=order_msg, parse_mode="HTML")
    except Exception as e:
        print("Admin notification error:", e)

    return {"status": "success", "message": "زاكاز مۇۋەپپەقىيەتلىك تاپشۇرۇلدى! ئادېمىن تەستىقلاپ قاچىلاپ بېرىدۇ."}

# ==================== كۆرۈنمە يۈز ====================
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
            * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
            body { background-color: #0b0c0e; color: #ffffff; direction: rtl; padding-bottom: 85px; }
            .top-navbar { background-color: #056a29; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; }
            .logo-box { display: flex; align-items: center; gap: 8px; }
            .back-arrow { display: none; font-size: 22px; color: #fff; cursor: pointer; }
            .brand-name { font-size: 19px; font-weight: 900; color: #22c55e; letter-spacing: 1px; }
            .balance-chip { background: rgba(0, 0, 0, 0.4); border-radius: 18px; padding: 4px 10px; display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: bold; }
            .plus-btn { background: #fff; color: #056a29; width: 17px; height: 17px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; cursor: pointer; }
            .content { padding: 14px; }
            .banner-box { background: radial-gradient(circle at center, #05451a 0%, #08170e 100%); border: 1.5px solid #10b981; border-radius: 16px; padding: 14px; text-align: center; margin-bottom: 14px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.25); }
            .banner-title { color: #34d399; font-size: 13px; font-weight: bold; margin-bottom: 10px; }
            .banner-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; border-top: 1px solid #14532d; padding-top: 10px; }
            .b-item { font-size: 9px; color: #a7f3d0; line-height: 1.2; }
            .b-icon { font-size: 15px; color: #10b981; margin-bottom: 4px; }
            .page-title { font-size: 17px; font-weight: bold; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; color: #f3f4f6; }
            .search-bar { width: 100%; background: #14171d; border: 1px solid #232733; border-radius: 22px; padding: 10px 16px; color: white; font-size: 13px; outline: none; margin-bottom: 16px; }
            .cards-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .card-wrap { background: #14171d; border: 1.5px solid #059669; border-radius: 16px; overflow: hidden; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: transform 0.15s; }
            .card-wrap:active { transform: scale(0.96); }
            .card-img { width: 100%; height: 105px; background: #000; overflow: hidden; }
            .card-img img { width: 100%; height: 100%; object-fit: cover; }
            .card-name { padding: 8px 4px; text-align: center; background: #0f131a; font-size: 12px; font-weight: bold; color: #f9fafb; }
            .product-item { background: #14171d; border: 1px solid #232733; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
            .p-name { font-size: 14px; font-weight: bold; }
            .p-price { color: #10b981; font-size: 13px; margin-top: 4px; }
            .btn-buy { background: #059669; color: white; border: none; padding: 8px 18px; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }
            .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #0d1117; border-top: 1px solid #1f2937; display: flex; justify-content: space-around; align-items: center; padding: 8px 0; z-index: 100; }
            .tab-btn { color: #9ca3af; font-size: 11px; text-align: center; cursor: pointer; flex: 1; text-decoration: none; }
            .center-tab { width: 48px; height: 48px; background: #056a29; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; margin-top: -24px; border: 3px solid #0b0c0e; box-shadow: 0 4px 10px rgba(5, 106, 41, 0.5); cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="top-navbar">
            <div class="logo-box">
                <span class="back-arrow" id="btnBack" onclick="goBack()">➜</span>
                <span class="brand-name">SAYF STORE</span>
            </div>
            <div class="balance-chip">
                <span class="plus-btn" onclick="contactAdmin()">+</span>
                <span id="uBal">$ 0.00</span>
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
            <div class="tab-btn" onclick="contactAdmin()">👤 حسابي</div>
            <div class="tab-btn" onclick="contactAdmin()">👛 شحن رصيد</div>
            <div class="center-tab" onclick="renderHome()">🏠</div>
            <div class="tab-btn" onclick="contactAdmin()">📋 طلباتي</div>
            <a class="tab-btn" id="supportLink" href="#" target="_blank">🎧 الدعم الفني</a>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            let currentUserId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : 0;
            let storeData = null;
            let currentLevel = 'home';
            let activeCat = null;
            let adminChatUrl = "";

            async function init() {
                try {
                    let res = await fetch('/api/store/data?user_id=' + currentUserId);
                    storeData = await res.json();
                    document.getElementById('uBal').innerText = '$ ' + storeData.user_balance;
                    adminChatUrl = storeData.admin_contact;
                    document.getElementById('supportLink').href = adminChatUrl;
                    renderHome();
                } catch(e) {
                    console.log("Error", e);
                }
            }

            function contactAdmin() {
                tg.openTelegramLink(adminChatUrl);
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
                    body: JSON.stringify({
                        user_id: currentUserId,
                        product_id: pId,
                        product_name: pName,
                        price: pPrice,
                        player_id: pid
                    })
                }).then(r => r.json()).then(res => {
                    if (res.status === 'error') {
                        alert(res.message);
                        contactAdmin();
                    } else {
                        alert(res.message);
                        location.reload();
                    }
                });
            }

            init();
        </script>
    </body>
    </html>
    """
    return html

# ==================== تېلېگرام قىسمى (BOT & ADMIN COMMANDS) ====================
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# 1-بۇيرۇق: خېرىدار كىرگەندە تىزىملىنىش ۋە ئادېمىنغا كۆرسىتىش
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute("INSERT INTO users (user_id, username, full_name, balance) VALUES (?, ?, ?, 0.0)",
                       (user.id, user.username or "", user.full_name))
        conn.commit()
        # سىزگە (ئادېمىنغا) يېڭى ئادەم كىرگەنلىك ئۇچۇرى بارىدۇ
        admin_alert = (
            f"👤 <b>يېڭى خېرىدار كىردى!</b>\n\n"
            f"🏷 <b>ئىسمى:</b> {user.full_name}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🔗 <b>Username:</b> @{user.username or 'يوق'}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="HTML")
        except Exception:
            pass
    conn.close()

    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://google.com")
    keyboard = [
        [InlineKeyboardButton("⚡ SAYF STORE نى ئېچىش", web_app=WebAppInfo(url=render_url))]
    ]
    await update.message.reply_text(
        f"مرحباً بك {user.first_name} في متجر SAYF STORE الرسمي! ⚡\n"
        f"المعرف الخاص بك (User ID): <code>{user.id}</code>\n"
        "اضغط على الزر أدناه لفتح المتجر وشراء ما تحتاجه:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# 2-بۇيرۇق: سىز (ئادېمىن) خېرىدارغا پۇل قوشۇپ بېرىدىغان بۇيرۇق
# ئىشلىتىش ئۇسۇلى: /add 12345678 10
async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        target_user = int(context.args[0])
        amount = float(context.args[1])
        update_user_balance(target_user, amount)

        await update.message.reply_text(f"✅ خېرىدار <code>{target_user}</code> نىڭ ھېساباتىغا ${amount} قوشۇلدى!", parse_mode="HTML")
        # خېرىدارغىمۇ ئاپتوماتىك تەبرىك خېتى بارىدۇ
        await context.bot.send_message(
            chat_id=target_user,
            text=f"🎉 <b>ھېساباتىڭىزغا ${amount} قوشۇلدى!</b>\nھازىرلا دۇكانغا كىرىپ خالىغان مالنى سېتىۋالالايسىز.",
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text("خاتا كىرگۈزدۈڭىز!\nئىشلىتىش ئۇسۇلى: <code>/add 12345678 10</code>", parse_mode="HTML")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("add", add_balance_cmd))

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
