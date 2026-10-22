import os
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "sayf_admin")

app = FastAPI()

def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
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

@app.get("/api/user/balance")
async def user_balance_api(user_id: int = 0):
    return {"balance": f"{get_user_balance(user_id):.2f}"}

@app.post("/api/store/order")
async def execute_order(request: Request):
    data = await request.json()
    u_id = data.get("user_id", 0)
    p_name = data.get("product_name")
    p_price = float(data.get("price", 0))
    player_id = data.get("player_id")

    current_bal = get_user_balance(u_id)
    if current_bal < p_price:
        return {"status": "error", "message": "قالدۇق پۇلىڭىز يەتمىدى! ئادېمىنغا باغلانما ئارقىلىق پۇل قاچىلىتىڭ."}

    update_user_balance(u_id, -p_price)

    order_msg = (
        f"🚨 <b>يېڭى زاكاز چۈشتى! (SAYF STORE)</b>\n\n"
        f"👤 <b>خېرىدار ID:</b> <code>{u_id}</code>\n"
        f"📦 <b>مەھسۇلات:</b> {p_name}\n"
        f"💰 <b>باھاسى:</b> ${p_price}\n"
        f"🎯 <b>Player ID:</b> <code>{player_id}</code>\n"
    )
    try:
        await bot_app.bot.send_message(chat_id=ADMIN_ID, text=order_msg, parse_mode="HTML")
    except Exception as e:
        print("Error sending to admin:", e)

    return {"status": "success", "message": "زاكاز مۇۋەپپەقىيەتلىك ئەۋەتىلدى! ئادېمىن تەستىقلاپ قاچىلايدۇ."}

@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    # سىرتتىن ھېچ نەرسە كۈتمەيدىغان، تېلېگرام ئىچىدە كاپالەتلىك ئېچىلىدىغان HTML بېتى
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>SAYF STORE</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * { box-sizing: border-box; font-family: sans-serif; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
            body { background-color: #0b0c0e; color: #ffffff; direction: rtl; padding-bottom: 90px; }
            .top-navbar { background-color: #056a29; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; }
            .brand-name { font-size: 19px; font-weight: 900; color: #22c55e; letter-spacing: 1px; }
            .back-arrow { display: none; font-size: 20px; color: #fff; cursor: pointer; margin-left: 8px; }
            .balance-chip { background: rgba(0, 0, 0, 0.4); border-radius: 18px; padding: 4px 10px; display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: bold; }
            .plus-btn { background: #fff; color: #056a29; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; cursor: pointer; }
            .content { padding: 14px; }
            .banner-box { background: radial-gradient(circle, #05451a 0%, #08170e 100%); border: 1.5px solid #10b981; border-radius: 16px; padding: 14px; text-align: center; margin-bottom: 14px; }
            .banner-title { color: #34d399; font-size: 13px; font-weight: bold; margin-bottom: 8px; }
            .banner-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; border-top: 1px solid #14532d; padding-top: 8px; }
            .b-item { font-size: 9px; color: #a7f3d0; }
            .page-title { font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #f3f4f6; }
            .cards-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .card-wrap { background: #14171d; border: 1.5px solid #059669; border-radius: 16px; padding: 20px 10px; text-align: center; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
            .card-wrap:active { transform: scale(0.96); background: #1e2430; }
            .card-icon { font-size: 34px; margin-bottom: 8px; }
            .card-name { font-size: 13px; font-weight: bold; color: #f9fafb; }
            .product-item { background: #14171d; border: 1px solid #232733; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
            .p-name { font-size: 14px; font-weight: bold; }
            .p-price { color: #10b981; font-size: 13px; margin-top: 4px; }
            .btn-buy { background: #059669; color: white; border: none; padding: 8px 18px; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }
            .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #0d1117; border-top: 1px solid #1f2937; display: flex; justify-content: space-around; align-items: center; padding: 8px 0; z-index: 100; }
            .tab-btn { color: #9ca3af; font-size: 11px; text-align: center; cursor: pointer; flex: 1; }
            .center-tab { width: 46px; height: 46px; background: #056a29; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; margin-top: -22px; border: 3px solid #0b0c0e; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="top-navbar">
            <div style="display:flex; align-items:center;">
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
                    <div class="banner-title">بوابتك لكافة الخدمات الرقمية ⚡ SAYF STORE</div>
                    <div class="banner-grid">
                        <div class="b-item">⚡ فوري</div>
                        <div class="b-item">🎯 أمان</div>
                        <div class="b-item">🎧 دعم 24/7</div>
                        <div class="b-item">💎 أفضل سعر</div>
                    </div>
                </div>
            </div>

            <div class="page-title" id="secTitle">تصنيفات المتجر</div>
            <div id="viewContainer" class="cards-layout"></div>
        </div>

        <div class="bottom-bar">
            <div class="tab-btn" onclick="contactAdmin()">👤 حسابي</div>
            <div class="tab-btn" onclick="contactAdmin()">👛 شحن</div>
            <div class="center-tab" onclick="renderHome()">🏠</div>
            <div class="tab-btn" onclick="contactAdmin()">📋 طلباتي</div>
            <div class="tab-btn" onclick="contactAdmin()">🎧 الدعم</div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            try { tg.ready(); tg.expand(); } catch(e){}

            let currentUserId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : 0;
            let currentLevel = 'home';
            let activeCat = null;

            const DB = {
                categories: [
                    { id: "games", name: "قسم الألعاب", icon: "🎮" },
                    { id: "apps", name: "قسم التطبيقات", icon: "🔮" },
                    { id: "cards", name: "بطاقات الكترونية", icon: "💳" },
                    { id: "balance", name: "الأرصدة والعملات", icon: "🪙" }
                ],
                subcategories: {
                    "games": [
                        { id: "pubg", name: "قسم ببجي (PUBG)", icon: "🎯" },
                        { id: "freefire", name: "قسم فري فاير", icon: "🔥" },
                        { id: "jawaker", name: "قسم جواكر", icon: "🃏" }
                    ],
                    "apps": [
                        { id: "tg_prem", name: "تيليجرام بريميوم", icon: "⭐" },
                        { id: "tiktok", name: "عملات تيك توك", icon: "🎵" }
                    ],
                    "cards": [
                        { id: "google", name: "بطاقات جوجل بلاي", icon: "🎁" }
                    ],
                    "balance": [
                        { id: "usdt", name: "شحن رصيد US", icon: "💵" }
                    ]
                },
                products: {
                    "pubg": [
                        { id: "pubg_60", name: "PUBG Mobile 60 UC", price: "0.99" },
                        { id: "pubg_325", name: "PUBG Mobile 325 UC", price: "4.95" },
                        { id: "pubg_660", name: "PUBG Mobile 660 UC", price: "9.90" }
                    ],
                    "freefire": [
                        { id: "ff_100", name: "Free Fire 100+10 جواهر", price: "0.99" },
                        { id: "ff_210", name: "Free Fire 210+21 جواهر", price: "1.98" }
                    ],
                    "jawaker": [
                        { id: "jw_70", name: "جواكر 70,000 توكنز", price: "2.20" }
                    ],
                    "tg_prem": [
                        { id: "tg_1m", name: "Telegram Premium 1 شهر", price: "3.95" }
                    ]
                }
            };

            function contactAdmin() {
                tg.openTelegramLink("https://t.me/sayf_admin");
            }

            function updateBal() {
                if(!currentUserId) return;
                fetch('/api/user/balance?user_id=' + currentUserId)
                    .then(r => r.json())
                    .then(d => { document.getElementById('uBal').innerText = '$ ' + d.balance; })
                    .catch(e => {});
            }

            function renderHome() {
                currentLevel = 'home';
                document.getElementById('homeBanner').style.display = 'block';
                document.getElementById('btnBack').style.display = 'none';
                document.getElementById('secTitle').innerText = 'تصنيفات المتجر';

                let c = document.getElementById('viewContainer');
                c.className = 'cards-layout';
                c.innerHTML = '';

                DB.categories.forEach(item => {
                    let d = document.createElement('div');
                    d.className = 'card-wrap';
                    d.onclick = () => renderSub(item.id, item.name);
                    d.innerHTML = `<div class="card-icon">${item.icon}</div><div class="card-name">${item.name}</div>`;
                    c.appendChild(d);
                });
            }

            function renderSub(id, name) {
                currentLevel = 'sub';
                activeCat = id;
                document.getElementById('homeBanner').style.display = 'none';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = name;

                let c = document.getElementById('viewContainer');
                c.className = 'cards-layout';
                c.innerHTML = '';

                let items = DB.subcategories[id] || [];
                items.forEach(item => {
                    let d = document.createElement('div');
                    d.className = 'card-wrap';
                    d.onclick = () => renderProd(item.id, item.name);
                    d.innerHTML = `<div class="card-icon">${item.icon}</div><div class="card-name">${item.name}</div>`;
                    c.appendChild(d);
                });
            }

            function renderProd(id, name) {
                currentLevel = 'prod';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = name;

                let c = document.getElementById('viewContainer');
                c.className = '';
                c.innerHTML = '';

                let prods = DB.products[id] || [];
                prods.forEach(p => {
                    let d = document.createElement('div');
                    d.className = 'product-item';
                    d.innerHTML = `
                        <div>
                            <div class="p-name">${p.name}</div>
                            <div class="p-price">${p.price} $</div>
                        </div>
                        <button class="btn-buy" onclick="makeOrder('${p.id}', '${p.name}', '${p.price}')">شراء</button>
                    `;
                    c.appendChild(d);
                });
            }

            function goBack() {
                if (currentLevel === 'prod') renderSub(activeCat, 'الأقسام');
                else if (currentLevel === 'sub') renderHome();
            }

            function makeOrder(id, name, price) {
                let pid = prompt(name + " (" + price + " $)\\nادخل المعرف الخاص بك (Player ID):");
                if (!pid) return;

                fetch('/api/store/order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: currentUserId, product_id: id, product_name: name, price: price, player_id: pid })
                }).then(r => r.json()).then(res => {
                    alert(res.message);
                    updateBal();
                });
            }

            renderHome();
            updateBal();
        </script>
    </body>
    </html>
    """

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, username, full_name, balance) VALUES (?, ?, ?, 0.0)",
                       (user.id, user.username or "", user.full_name))
        conn.commit()
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"👤 <b>يېڭى خېرىدار:</b> {user.full_name}\n🆔 ID: <code>{user.id}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass
    conn.close()

    render_url = os.getenv("RENDER_EXTERNAL_URL", "https://google.com")
    keyboard = [[InlineKeyboardButton("⚡ SAYF STORE نى ئېچىش", web_app=WebAppInfo(url=render_url))]]
    await update.message.reply_text(
        f"مرحباً بك {user.first_name} في متجر SAYF STORE الرسمي! ⚡\nالمعرف: <code>{user.id}</code>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target = int(context.args[0])
        amount = float(context.args[1])
        update_user_balance(target, amount)
        await update.message.reply_text(f"✅ خېرىدار <code>{target}</code> غا ${amount} قوشۇلدى!", parse_mode="HTML")
    except Exception:
        await update.message.reply_text("ئىشلىتىش: <code>/add 12345678 10</code>", parse_mode="HTML")

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
