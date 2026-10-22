import os
import json
import sqlite3
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "sayf_admin")
ZEIN_API_KEY = os.getenv("ZEIN_API_KEY", "_UMp2U9ww7ShQTi62W1XG9ZSA4RhTg-S8ok65Z8vZS1WDuJoWcu4nt97IIP3O0IJ")
ZEIN_BASE_URL = "https://api.zein-store.com"

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
        return {"status": "error", "message": "قالدۇق پۇلىڭىز يەتمىدى! ئادېمىن بىلەن ئالاقىلىشىپ پۇل قاچىلاڭ."}

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
        print("Admin notification error:", e)

    return {"status": "success", "message": "زاكاز مۇۋەپپەقىيەتلىك تاپشۇرۇلدى!"}

@app.get("/", response_class=HTMLResponse)
async def serve_shop():
    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>SAYF STORE</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }}
            body {{ background-color: #0b0c0e; color: #ffffff; direction: rtl; padding-bottom: 90px; }}
            .top-navbar {{ background-color: #056a29; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; }}
            .logo-box {{ display: flex; align-items: center; gap: 8px; }}
            .back-arrow {{ display: none; font-size: 22px; color: #fff; cursor: pointer; }}
            .brand-name {{ font-size: 19px; font-weight: 900; color: #22c55e; letter-spacing: 1px; }}
            .balance-chip {{ background: rgba(0, 0, 0, 0.4); border-radius: 18px; padding: 4px 10px; display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: bold; }}
            .plus-btn {{ background: #fff; color: #056a29; width: 17px; height: 17px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; cursor: pointer; }}
            .content {{ padding: 14px; }}
            .banner-box {{ background: radial-gradient(circle at center, #05451a 0%, #08170e 100%); border: 1.5px solid #10b981; border-radius: 16px; padding: 14px; text-align: center; margin-bottom: 14px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.25); }}
            .banner-title {{ color: #34d399; font-size: 13px; font-weight: bold; margin-bottom: 10px; }}
            .banner-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; border-top: 1px solid #14532d; padding-top: 10px; }}
            .b-item {{ font-size: 9px; color: #a7f3d0; line-height: 1.2; }}
            .b-icon {{ font-size: 15px; color: #10b981; margin-bottom: 4px; }}
            .page-title {{ font-size: 17px; font-weight: bold; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; color: #f3f4f6; }}
            .search-bar {{ width: 100%; background: #14171d; border: 1px solid #232733; border-radius: 22px; padding: 10px 16px; color: white; font-size: 13px; outline: none; margin-bottom: 16px; }}
            .cards-layout {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
            .card-wrap {{ background: #14171d; border: 1.5px solid #059669; border-radius: 16px; overflow: hidden; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }}
            .card-wrap:active {{ transform: scale(0.96); }}
            .card-img {{ width: 100%; height: 105px; background: #000; overflow: hidden; }}
            .card-img img {{ width: 100%; height: 100%; object-fit: cover; }}
            .card-name {{ padding: 8px 4px; text-align: center; background: #0f131a; font-size: 12px; font-weight: bold; color: #f9fafb; }}
            .product-item {{ background: #14171d; border: 1px solid #232733; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .p-name {{ font-size: 14px; font-weight: bold; }}
            .p-price {{ color: #10b981; font-size: 13px; margin-top: 4px; }}
            .btn-buy {{ background: #059669; color: white; border: none; padding: 8px 18px; border-radius: 8px; font-weight: bold; font-size: 13px; cursor: pointer; }}
            .bottom-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: #0d1117; border-top: 1px solid #1f2937; display: flex; justify-content: space-around; align-items: center; padding: 8px 0; z-index: 100; }}
            .tab-btn {{ color: #9ca3af; font-size: 11px; text-align: center; cursor: pointer; flex: 1; }}
            .center-tab {{ width: 48px; height: 48px; background: #056a29; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; margin-top: -24px; border: 3px solid #0b0c0e; box-shadow: 0 4px 10px rgba(5, 106, 41, 0.5); cursor: pointer; }}
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
            <div class="tab-btn" onclick="contactAdmin()">🎧 الدعم الفني</div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            const ADMIN_CHAT = "https://t.me/{ADMIN_USERNAME}";
            let currentUserId = tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.id : 0;
            let currentLevel = 'home';
            let activeCat = null;

            // كودنىڭ ئىچىگە بىۋاسىتە كىرگۈزۈلگەن سىفىرلىق سانلىق مەلۇمات (تور توختاپ قالمايدۇ)
            const LOCAL_DATA = {{
                categories: [
                    {{"id": "games", "name": "قسم الألعاب", "img": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500&auto=format&fit=crop"}},
                    {{"id": "apps", "name": "قسم التطبيقات", "img": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop"}},
                    {{"id": "cards", "name": "بطاقات الكترونية", "img": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=500&auto=format&fit=crop"}},
                    {{"id": "balance", "name": "الأرصدة والعملات", "img": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=500&auto=format&fit=crop"}}
                ],
                subcategories: {{
                    "games": [
                        {{"id": "pubg", "name": "قسم ببجي", "img": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500&auto=format&fit=crop"}},
                        {{"id": "freefire", "name": "قسم فري فاير", "img": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=500&auto=format&fit=crop"}},
                        {{"id": "jawaker", "name": "قسم جواكر", "img": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop"}}
                    ],
                    "apps": [
                        {{"id": "tg_prem", "name": "تيليجرام بريميوم", "img": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop"}},
                        {{"id": "tiktok", "name": "عملات تيك توك", "img": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=500&auto=format&fit=crop"}}
                    ],
                    "cards": [
                        {{"id": "google", "name": "بطاقات جوجل بلاي", "img": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=500&auto=format&fit=crop"}}
                    ],
                    "balance": [
                        {{"id": "usdt", "name": "شحن عملات رقمية", "img": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=500&auto=format&fit=crop"}}
                    ]
                }},
                products: {{
                    "pubg": [
                        {{"id": "pubg_60", "name": "PUBG Mobile 60 UC", "price": "0.99"}},
                        {{"id": "pubg_325", "name": "PUBG Mobile 325 UC", "price": "4.95"}},
                        {{"id": "pubg_660", "name": "PUBG Mobile 660 UC", "price": "9.90"}}
                    ],
                    "freefire": [
                        {{"id": "ff_100", "name": "Free Fire 100+10 جواهر", "price": "0.99"}},
                        {{"id": "ff_210", "name": "Free Fire 210+21 جواهر", "price": "1.98"}}
                    ],
                    "jawaker": [
                        {{"id": "jw_70", "name": "جواكر 70,000 توكنز", "price": "2.20"}}
                    ],
                    "tg_prem": [
                        {{"id": "tg_1m", "name": "Telegram Premium 1 شهر", "price": "3.95"}}
                    ]
                }}
            }};

            function contactAdmin() {{
                tg.openTelegramLink(ADMIN_CHAT);
            }}

            async function updateBalanceUI() {{
                try {{
                    let res = await fetch('/api/user/balance?user_id=' + currentUserId);
                    let data = await res.json();
                    document.getElementById('uBal').innerText = '$ ' + data.balance;
                }} catch(e) {{}}
            }}

            function renderHome() {{
                currentLevel = 'home';
                document.getElementById('homeBanner').style.display = 'block';
                document.getElementById('btnBack').style.display = 'none';
                document.getElementById('secTitle').innerText = 'تصنيفات المتجر';
                
                let container = document.getElementById('viewContainer');
                container.className = 'cards-layout';
                container.innerHTML = '';

                LOCAL_DATA.categories.forEach(c => {{
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

            function renderSubcategories(catId, catName) {{
                currentLevel = 'sub';
                activeCat = catId;
                document.getElementById('homeBanner').style.display = 'none';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = catName;

                let items = LOCAL_DATA.subcategories[catId] || [];
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

            function renderProducts(subId, subName) {{
                currentLevel = 'prod';
                document.getElementById('btnBack').style.display = 'inline-block';
                document.getElementById('secTitle').innerText = subName;

                let prods = LOCAL_DATA.products[subId] || [];
                let container = document.getElementById('viewContainer');
                container.className = '';
                container.innerHTML = '';

                if (prods.length === 0) {{
                    container.innerHTML = '<p style="text-align:center; color:#9ca3af; padding:20px;">المزيد من الباقات ستتوفر قريباً...</p>';
                    return;
                }}

                prods.forEach(p => {{
                    let div = document.createElement('div');
                    div.className = 'product-item';
                    div.innerHTML = `
                        <div>
                            <div class="p-name">${{p.name}}</div>
                            <div class="p-price">${{p.price}} $</div>
                        </div>
                        <button class="btn-buy" onclick="makeOrder('${{p.id}}', '${{p.name}}', '${{p.price}}')">شراء</button>
                    `;
                    container.appendChild(div);
                }});
            }}

            function goBack() {{
                if (currentLevel === 'prod') {{
                    renderSubcategories(activeCat, 'العودة للأقسام');
                }} else if (currentLevel === 'sub') {{
                    renderHome();
                }}
            }}

            function makeOrder(pId, pName, pPrice) {{
                let pid = prompt(pName + " (" + pPrice + " $)\\nادخل المعرف الخاص بك (Player ID):");
                if (!pid) return;

                fetch('/api/store/order', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        user_id: currentUserId,
                        product_id: pId,
                        product_name: pName,
                        price: pPrice,
                        player_id: pid
                    }})
                }}).then(r => r.json()).then(res => {{
                    if (res.status === 'error') {{
                        alert(res.message);
                        contactAdmin();
                    }} else {{
                        alert(res.message);
                        updateBalanceUI();
                    }}
                }});
            }}

            updateBalanceUI();
            renderHome();
        </script>
    </body>
    </html>
    """
    return html

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

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

async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        target_user = int(context.args[0])
        amount = float(context.args[1])
        update_user_balance(target_user, amount)

        await update.message.reply_text(f"✅ خېرىدار <code>{target_user}</code> گە ${amount} قوشۇلدى!", parse_mode="HTML")
        await context.bot.send_message(
            chat_id=target_user,
            text=f"🎉 <b>ھېساباتىڭىزغا ${amount} قوشۇلدى!</b>\nھازىرلا دۇكانغا كىرىپ زاكاز بېرەلەيسىز.",
            parse_mode="HTML"
        )
    except Exception:
        await update.message.reply_text("ئىشلىتىش ئۇسۇلى: <code>/add 12345678 10</code>", parse_mode="HTML")

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
