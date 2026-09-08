import io
import os
import random
import urllib.parse
from datetime import datetime
import pandas as pd
from PIL import Image, ImageStat
import requests
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# 🗝️ CONFIGURATION & API KEYS
# ==============================================================================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rewewstbknigolxiozwp.supabase.co")

SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJld2V3c3Ria25pZ29seGlvendwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNDU5MTUsImV4cCI6MjEwMzkyMTkxNX0.s1reBkT9vmYSKGM0yPJTJiAWxT0xxdO446GVOI6ib3U",
)


PAYSTACK_SECRET_KEY = os.environ.get(
    "PAYSTACK_SECRET_KEY",
    "sk_live_5d70f03c20eea14b71be5b116e453e6a6848eebe",
)

PAYSTACK_CALLBACK_URL = os.environ.get("PAYSTACK_CALLBACK_URL", "https://feed-the-nations.onrender.com")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ==============================================================================
# 1. PAGE CONFIG & RESPONSIVE SCREEN-FITTING STYLING
# ==============================================================================
st.set_page_config(
    page_title="FEED THE NATIONS - Direct Agri Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Montserrat:wght@700;800;900&display=swap');

    :root {
        --primary: #1B4D3E;
        --primary-light: #2C6E49;
        --accent: #D4A373;
        --bg-main: #F4F7F4;
        --card-bg: #FFFFFF;
        --text-dark: #1E293B;
        --text-muted: #64748B;
        --border-color: #E2E8F0;
    }

    .stApp {
        background-color: var(--bg-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-dark);
        margin: 0 auto;
        max-width: 100vw;
        overflow-x: hidden;
    }

    .brand-header-container {
        position: relative;
        background: linear-gradient(-45deg, #062319, #0E3A2B, #1B4D3E, #2D6A4F, #124131);
        background-size: 400% 400%;
        animation: bgShift 10s ease infinite;
        padding: clamp(20px, 4vw, 45px) clamp(12px, 3vw, 24px);
        border-radius: 22px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 16px 36px rgba(10, 47, 35, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.18);
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
    }

    @keyframes bgShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .brand-header-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: -150%;
        width: 80%;
        height: 100%;
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0) 0%,
            rgba(255, 255, 255, 0.2) 20%,
            rgba(255, 255, 255, 0.95) 50%,
            rgba(255, 255, 255, 0.2) 80%,
            rgba(255, 255, 255, 0) 100%
        );
        transform: skewX(-30deg);
        animation: headerShimmer 3s infinite ease-in-out;
        pointer-events: none;
        filter: blur(4px);
    }

    @keyframes headerShimmer {
        0% { left: -150%; }
        100% { left: 220%; }
    }

    .brand-title {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(1.8rem, 5vw, 3.8rem);
        font-weight: 900;
        letter-spacing: 1px;
        margin: 5px 0 10px 0;
        text-transform: uppercase;
        text-shadow: 0 4px 15px rgba(0,0,0,0.4);
        word-break: break-word;
    }

    .header-emojis {
        font-size: clamp(1.4rem, 3.5vw, 2.1rem);
        margin: 10px 0;
        letter-spacing: clamp(6px, 1.5vw, 12px);
        display: inline-block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }

    .brand-subtext {
        color: #E2E8F0;
        font-size: clamp(0.9rem, 2vw, 1.15rem);
        font-weight: 600;
        margin-top: 5px;
        margin-bottom: 18px;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }

    .brand-badge {
        display: inline-block;
        background: rgba(212, 163, 115, 0.25);
        border: 1px solid #E6C594;
        color: #FFF3E0;
        padding: clamp(6px, 1.5vw, 8px) clamp(14px, 2.5vw, 22px);
        border-radius: 30px;
        font-size: clamp(0.75rem, 1.5vw, 0.85rem);
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* Warning Callout Box */
    .warning-box {
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        color: #92400E;
    }

    .warning-box h4 {
        margin: 0 0 6px 0;
        color: #B45309;
        font-weight: 800;
    }

    .alert-danger-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        color: #991B1B;
    }

    .alert-success-box {
        background-color: #F0FDF4;
        border-left: 5px solid #22C55E;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        color: #166534;
    }

    /* BROWN SIGN-OFF BUTTON STYLING */
    div.stButton > button.brown-signoff-btn {
        background: linear-gradient(135deg, #7F4F24 0%, #582F0E 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        border: 2px solid #3D200A !important;
        box-shadow: 0 6px 18px rgba(88, 47, 14, 0.35) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div.stButton > button.brown-signoff-btn:hover {
        background: linear-gradient(135deg, #935E31 0%, #6F3C13 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 22px rgba(88, 47, 14, 0.45) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid var(--border-color);
    }
    
    .user-profile-badge {
        background: #F1F5F9;
        padding: 16px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }

    .product-grid-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 16px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
        box-sizing: border-box;
    }

    .product-grid-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(0,0,0,0.1);
        border-color: #CBD5E1;
    }

    .user-msg-box {
        background-color: #E2E8F0;
        color: #1E293B;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        border-left: 4px solid #64748B;
    }

    .ai-msg-box {
        background-color: #E6F4EA;
        color: #1B4D3E;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        border-left: 4px solid #1B4D3E;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1B4D3E 0%, #2C6E49 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: clamp(0.85rem, 1.2vw, 0.95rem) !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        border: none !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2C6E49 0%, #3A8659 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(27, 77, 62, 0.3) !important;
    }

    .whatsapp-btn {
        display: block;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        font-weight: 700;
        padding: 12px 18px;
        border-radius: 10px;
        text-decoration: none;
        margin-top: 10px;
        margin-bottom: 10px;
        font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
    }

    @media (max-width: 768px) {
        .stMainBlockContainer {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .product-grid-card {
            margin-bottom: 14px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. HELPER FUNCTIONS & DB CONNECTIONS
# ==============================================================================
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"Supabase Client Initialization Warning: {e}")

AGRI_CATEGORIES = [
    "🌾 Crop Farming (Rice, Beans, Maize, Grains)",
    "🏭 Agro-Processing & Packaged Goods",
    "🐂 Livestock Farming",
    "🐓 Poultry Farming",
    "🐟 Fishery / Aquaculture",
    "🍎 Horticulture (Fruits & Vegetables)",
    "🥛 Dairy Farming",
]

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", 
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT - Abuja", "Gombe", 
    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", 
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", 
    "Taraba", "Yobe", "Zamfara"
]

LOGISTICS_PARTNERS = {
    "GIG Logistics": {"whatsapp": "13467744344"},
    "Maersk Nigeria": {"whatsapp": "2349087848100"},
    "Fortune Global Shipping": {"whatsapp": "2348182784572"},
    "CourierPlus": {"whatsapp": "2347033074129"},
    "Kobo360 Haulage": {"whatsapp": "2348186780000"},
    "DHL Express Nigeria": {"whatsapp": "2347011126221"},
    "Red Star Express": {"whatsapp": "2347007337827"},
    "SkyNet Worldwide": {"whatsapp": "2349056533136"},
    "Tranex Cargo": {"whatsapp": "2348123682573"},
    "Sendbox Delivery": {"whatsapp": "23417006150"},
}

NIGERIAN_BANKS = [
    "Access Bank", "First Bank of Nigeria", "GTBank (Guaranty Trust)", "Zenith Bank",
    "UBA (United Bank for Africa)", "Fidelity Bank", "Stanbic IBTC", "Kuda Bank",
    "OPay", "Palmpay", "Moniepoint", "Sterling Bank", "Wema Bank (ALAT)"
]

def verify_farm_photo(image):
    try:
        img = image.convert("RGB")
        stat = ImageStat.Stat(img)
        avg_stddev = sum(stat.stddev) / len(stat.stddev)
        if avg_stddev < 15:
            return False, "Image appears blank or low contrast. Please upload a clear produce photo."
        w, h = img.size
        if w < 150 or h < 150:
            return False, "Image resolution too low. Minimum allowed size is 150x150 pixels."
        return True, "Valid farm photo"
    except Exception:
        return False, "Invalid image format."

def upload_product_photo(file_bytes, filename):
    try:
        clean_name = "".join([c for c in filename if c.isalnum() or c in (".", "_", "-")]).lower()
        path = f"farm_{random.randint(10000, 99999)}_{clean_name}"
        supabase.storage.from_("farm-photos").upload(
            path, file_bytes, file_options={"content-type": "image/jpeg", "upsert": "true"}
        )
        return f"{SUPABASE_URL}/storage/v1/object/public/farm-photos/{path}"
    except Exception as e:
        st.error(f"Storage upload error: {e}")
        return None

def render_product_image(url_or_path, height=180):
    if url_or_path and str(url_or_path).strip():
        img_url = str(url_or_path).strip()
        if not img_url.startswith("http"):
            img_url = f"{SUPABASE_URL}/storage/v1/object/public/farm-photos/{img_url}"
        try:
            st.image(img_url, use_container_width=True)
            return
        except Exception:
            pass
    st.info("📷 Photo Verified")

def initialize_paystack_payment(email, amount_ngn, reference):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
    data = {
        "email": email,
        "amount": int(amount_ngn * 100),
        "reference": reference,
        "callback_url": PAYSTACK_CALLBACK_URL,
    }
    return requests.post(url, json=data, headers=headers).json()

def verify_paystack_payment(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    try:
        res = requests.get(url, headers=headers).json()
        if res.get("status") and res.get("data", {}).get("status") == "success":
            return True, res["data"]
        return False, "Pending or failed."
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 3. AI HELP DESK
# ==============================================================================
def generate_ai_support_response(user_name: str, user_role: str, message: str) -> str:
    name = user_name if user_name else "Valued User"
    
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt_text = (
                f"You are the AI Helpdesk Agent for FEED THE NATIONS, an agricultural marketplace & escrow platform.\n"
                f"User Name: {name}\nUser Role: {user_role}\nUser Message: {message}\n\n"
                f"Provide a helpful, professional, and concise response assisting them with their inquiry, escrow, or freight delivery."
            )
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    msg = message.lower().strip()
    if any(k in msg for k in ["buyer", "customer", "client"]):
        return (
            f"Hello **{name}**! Regarding your buyer transaction:\n"
            "• Escrow funds are secured safely by the platform.\n"
            "• Both Farmer and Buyer must sign off before funds unlock to prevent fraud."
        )
    elif any(k in msg for k in ["escrow", "payment", "fund", "money", "pay", "withdraw"]):
        return (
            f"Hello **{name}**! Regarding your escrow status:\n"
            "• Farmer signs off when produce is dispatched.\n"
            "• Buyer signs off upon inspecting delivered goods.\n"
            "• Funds unlock automatically to the Farmer Wallet once both confirmations are complete."
        )
    else:
        return f"Hello **{name}**! Re: *\"{message}\"*\nOur support team is reviewing your ticket."

# ==============================================================================
# 4. SESSION STATE & PAYSTACK CALLBACK
# ==============================================================================
for key, default in [
    ("authenticated", False),
    ("user_role", None),
    ("username", ""),
    ("email", ""),
    ("phone", ""),
    ("selected_product_id", None),
    ("editing_listing_id", None),
    ("deleted_msg", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

query_params = st.query_params
if "reference" in query_params or "trxref" in query_params:
    pay_ref = query_params.get("reference") or query_params.get("trxref")
    is_success, _ = verify_paystack_payment(pay_ref)
    if is_success:
        existing_tx = supabase.table("transactions").select("*").eq("paystack_ref", pay_ref).execute().data
        if existing_tx and existing_tx[0].get("status") not in ["PAID_VERIFIED", "FARMER_DISPATCHED", "DELIVERED_VERIFIED"]:
            tx_item = existing_tx[0]
            supabase.table("transactions").update({
                "status": "PAID_VERIFIED",
                "farmer_signoff": False,
                "buyer_signoff": False
            }).eq("paystack_ref", pay_ref).execute()
            
            listing_res = supabase.table("listings").select("quantity").eq("id", tx_item["listing_id"]).execute().data
            if listing_res:
                cur_qty = int(listing_res[0].get("quantity", 0))
                bought_qty = int(tx_item.get("quantity_bought", 1))
                supabase.table("listings").update({"quantity": max(0, cur_qty - bought_qty)}).eq("id", tx_item["listing_id"]).execute()
            st.success("🎉 Payment verified! Escrow funds locked safely until dual sign-off.")
        st.query_params.clear()

# ==============================================================================
# 5. BRAND HEADER
# ==============================================================================
st.markdown(
    """
<div class="brand-header-container">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <div class="header-emojis">🌾 🌽 🐂 🐓</div>
    <p class="brand-subtext">Direct Farm-to-Buyer Marketplace • Verified Produce • Instant Logistics Freight</p>
    <div class="brand-badge">🌾 Official Agricultural Escrow Platform</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 6. AUTHENTICATION PORTAL
# ==============================================================================
if not st.session_state.authenticated:
    c_auth, _ = st.columns([1, 0.1])
    with c_auth:
        st.subheader("🔑 Access Account")
        auth_mode = st.radio("Choose Action", ["Login", "Register Account"], horizontal=True)

        email_input = st.text_input("Email Address").strip().lower()
        password_input = st.text_input("Password", type="password")

        if auth_mode == "Register Account":
            selected_role = st.selectbox("Account Role", ["Buyer (Wholesaler/Processor)", "Farmer / Producer", "Platform Admin"])
            full_name = st.text_input("Full Name / Business Name")
            phone_input = st.text_input("Phone Number (WhatsApp Enabled)", placeholder="+2348000000000").strip()
            farming_cat = st.selectbox("Primary Category", AGRI_CATEGORIES) if "Farmer" in selected_role else "All Categories"

            if st.button("CREATE ACCOUNT 🚀"):
                if email_input and password_input and full_name and phone_input:
                    try:
                        role_str = "Farmer" if "Farmer" in selected_role else ("Admin" if "Admin" in selected_role else "Buyer")
                        res = supabase.auth.sign_up({
                            "email": email_input,
                            "password": password_input,
                            "options": {"data": {"full_name": full_name, "phone": phone_input, "role": role_str, "category": farming_cat}},
                        })
                        if res.user:
                            supabase.table("profiles").upsert({
                                "id": res.user.id, "email": email_input, "full_name": full_name, "phone": phone_input, "role": role_str, "category": farming_cat
                            }).execute()
                        st.success("🎉 Account created successfully! You can now log in.")
                    except Exception as e:
                        st.error(f"Registration error: {e}")
                else:
                    st.error("Please complete all required fields.")
        else:
            if st.button("LOG IN ➔"):
                if email_input and password_input:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email_input, "password": password_input})
                        if res.user:
                            meta = res.user.user_metadata or {}
                            prof_data = supabase.table("profiles").select("*").eq("email", email_input).execute().data
                            profile = prof_data[0] if prof_data else {}

                            st.session_state.authenticated = True
                            st.session_state.user_role = meta.get("role") or profile.get("role", "Buyer")
                            st.session_state.username = meta.get("full_name") or profile.get("full_name", email_input)
                            st.session_state.phone = meta.get("phone") or profile.get("phone", "")
                            st.session_state.email = email_input
                            st.rerun()
                    except Exception as e:
                        st.error(f"Login error: {e}")
                else:
                    st.error("Please enter email and password.")
    st.stop()

# ==============================================================================
# 7. SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown(
        f"""
        <div class="user-profile-badge">
            <div style="font-weight: 800; font-size: 1.05rem; color: #1E293B;">👤 {st.session_state.username}</div>
            <div style="font-size: 0.85rem; color: #64748B;">Role: <b>{st.session_state.user_role}</b></div>
            <div style="font-size: 0.8rem; color: #94A3B8;">📞 {st.session_state.phone or 'N/A'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔒 Sign Out"):
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

    st.divider()

    if st.session_state.user_role == "Farmer":
        nav_options = ["🛒 Produce Marketplace", "💰 Farmer Sales & Escrow", "📦 Manage Farm Listings", "💬 Support & AI Helpdesk"]
    elif st.session_state.user_role == "Buyer":
        nav_options = ["🛒 Produce Marketplace", "📦 My Orders & Escrow", "💬 Support & AI Helpdesk"]
    else:
        nav_options = ["📈 Revenue Dashboard", "🛒 Produce Marketplace", "💬 Support & AI Helpdesk"]

    navigation = st.radio("Navigation Menu", nav_options)

# ==============================================================================
# 8. PRODUCT DETAIL & BUY MODAL
# ==============================================================================
@st.dialog("🌾 Produce Details & Escrow Purchase")
def show_product_detail_modal(product_id):
    try:
        res = supabase.table("listings").select("*").eq("id", product_id).execute().data
        if not res:
            st.error("Product not found.")
            return

        item = res[0]
        col1, col2 = st.columns([1, 1.2])

        with col1:
            render_product_image(item.get("image_url"))
            st.markdown(f"**Pickup State:** {item.get('location')}")
            st.markdown(f"**Exact Address / Landmark:** `{item.get('exact_farm_address', 'Contact seller upon purchase')}`")
            st.markdown(f"**Producer:** `{item.get('seller')}`")

        with col2:
            st.markdown(f"### {item['item']}")
            st.caption(f"Sector: {item.get('category')}")
            
            unit_price = float(item["price_ngn"])
            available_stock = int(item.get("quantity", 1))
            unit_weight = float(item.get("unit_weight_kg", 50.0))

            st.markdown(f"### ₦{unit_price:,.2f} <span style='font-size: 0.9rem; color: grey;'>/ unit</span>", unsafe_allow_html=True)
            st.markdown(f"🟢 Stock: **{available_stock} units** ({unit_weight} kg/unit)")

            desired_qty = st.number_input(
                "Order Quantity", min_value=1, max_value=max(available_stock, 1), value=1, step=1, key="modal_qty"
            )

            product_subtotal = unit_price * desired_qty
            platform_fee = product_subtotal * 0.10
            total_weight_kg = unit_weight * desired_qty

            st.markdown(f"**Subtotal ({total_weight_kg:,.1f} kg):** ₦{product_subtotal:,.2f}")
            st.markdown(f"**Platform Escrow Fee (10%):** ₦{platform_fee:,.2f}")

        st.divider()
        st.markdown("#### 🚚 Step 1: Delivery Destination & Freight Quote")

        d_col1, d_col2 = st.columns([1, 2])
        with d_col1:
            delivery_state = st.selectbox("Destination State", NIGERIAN_STATES, index=24, key="modal_state")
        with d_col2:
            delivery_street = st.text_input("Exact Delivery Address", placeholder="Street, City, Landmark", key="modal_street")

        full_address = f"{delivery_street.strip()}, {delivery_state}" if delivery_street.strip() else delivery_state

        selected_partner = st.selectbox("Freight Carrier Partner", list(LOGISTICS_PARTNERS.keys()), key="modal_carrier")
        partner_info = LOGISTICS_PARTNERS[selected_partner]

        wa_msg_text = (
            f"Hello {selected_partner},\n\n"
            f"I am purchasing produce on FEED THE NATIONS:\n"
            f"• Produce: {item['item']}\n"
            f"• Quantity: {desired_qty} units ({total_weight_kg} kg)\n"
            f"• Farm Pickup Address: {item.get('exact_farm_address', 'N/A')}, {item['location']}\n"
            f"• Destination: {full_address}\n\n"
            f"Please provide an official freight quote."
        )
        wa_url = f"https://wa.me/{partner_info['whatsapp']}?text={urllib.parse.quote(wa_msg_text)}"
        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 Request Freight Quote on WhatsApp</a>', unsafe_allow_html=True)

        st.markdown("#### 🚚 Step 2: Agreed Freight & Checkout")
        agreed_freight = st.number_input("Enter Agreed Freight Fee (₦)", min_value=0, value=25000, step=5000, key="modal_freight")

        grand_total = product_subtotal + platform_fee + agreed_freight
        st.markdown(f"### **Total Amount: ₦{grand_total:,.2f}**")

        if st.button("PROCEED TO PAYSTACK CHECKOUT 💳", key="modal_checkout"):
            if not delivery_street.strip():
                st.error("⚠️ Please enter a delivery address.")
            else:
                ref = f"FTN-TX-{random.randint(100000, 999999)}"
                tx_record = {
                    "id": ref,
                    "listing_id": item["id"],
                    "category": item["category"],
                    "item": item["item"],
                    "quantity_bought": desired_qty,
                    "amount": product_subtotal,
                    "commission": platform_fee,
                    "freight": agreed_freight,
                    "total_paid": grand_total,
                    "buyer": st.session_state.username,
                    "delivery_address": full_address,
                    "status": "PAYMENT_INITIATED",
                    "paystack_ref": ref,
                    "farmer_signoff": False,
                    "buyer_signoff": False,
                }
                supabase.table("transactions").insert(tx_record).execute()
                pay_resp = initialize_paystack_payment(st.session_state.email, grand_total, ref)

                if pay_resp.get("status"):
                    auth_url = pay_resp["data"]["authorization_url"]
                    st.success("Checkout created! Click button below to complete payment.")
                    st.markdown(
                        f'<a href="{auth_url}" target="_blank" style="display:block; text-align:center; background: #1B4D3E; color:white; padding:12px; border-radius:8px; text-decoration:none; font-weight:bold;">Pay via Paystack ➔</a>',
                        unsafe_allow_html=True,
                    )

    except Exception as e:
        st.error(f"Error opening modal: {e}")

# ==============================================================================
# 9. MARKETPLACE VIEW
# ==============================================================================
if navigation == "🛒 Produce Marketplace":
    st.subheader("🛒 Farm Produce Marketplace")

    f1, f2 = st.columns([1, 1])
    with f1:
        category_filter = st.selectbox("Category Filter", ["All Categories"] + AGRI_CATEGORIES)
    with f2:
        scale_filter = st.selectbox("Scale Filter", ["All Scales", "Large Scale / Commercial Wholesale", "Small Scale / Retail"])

    st.divider()

    try:
        query = supabase.table("listings").select("*").gt("quantity", 0)
        if category_filter != "All Categories":
            query = query.eq("category", category_filter)
        if scale_filter != "All Scales":
            query = query.eq("scale", scale_filter)

        listings = query.execute().data

        if not listings:
            st.info("No active produce listings available.")
        else:
            cols_per_row = 3
            for i in range(0, len(listings), cols_per_row):
                row_items = listings[i:i + cols_per_row]
                grid_cols = st.columns(cols_per_row)

                for idx, item in enumerate(row_items):
                    with grid_cols[idx]:
                        with st.container():
                            st.markdown('<div class="product-grid-card">', unsafe_allow_html=True)
                            render_product_image(item.get("image_url"))
                            
                            st.markdown(f"#### {item['item']}")
                            st.caption(f"📍 {item.get('location')} | Seller: {item['seller']}")
                            
                            unit_price = float(item["price_ngn"])
                            st.markdown(f"**₦{unit_price:,.2f}** / unit")
                            st.markdown(f"Stock: `{item.get('quantity', 0)} units` ({item.get('unit_weight_kg', 50)} kg)")

                            if st.button("View Details & Buy ➔", key=f"btn_view_{item['id']}"):
                                show_product_detail_modal(item["id"])

                            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Marketplace error: {e}")

# ==============================================================================
# 10. FARMER LISTINGS MANAGEMENT
# ==============================================================================
elif navigation == "📦 Manage Farm Listings":
    st.subheader("📦 Farm Produce Inventory")

    tab_active, tab_add = st.tabs(["🟢 Active Listings", "➕ Post New Produce"])

    with tab_active:
        try:
            my_items = supabase.table("listings").select("*").eq("seller", st.session_state.username).execute().data
            if not my_items:
                st.info("You haven't listed any produce yet.")
            else:
                for item in my_items:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c1:
                            render_product_image(item.get("image_url"))
                        with c2:
                            st.markdown(f"### {item['item']}")
                            st.write(f"**Category:** {item.get('category')}")
                            st.write(f"**Price:** ₦{float(item['price_ngn']):,.2f} | **Stock:** {item.get('quantity')} units")
                            st.write(f"**Location:** {item.get('location')} ({item.get('exact_farm_address', 'N/A')})")
                        with c3:
                            if st.button("🗑️ Delete Listing", key=f"del_{item['id']}"):
                                supabase.table("transactions").delete().eq("listing_id", item["id"]).execute()
                                supabase.table("listings").delete().eq("id", item["id"]).execute()
                                st.success("Listing removed.")
                                st.rerun()
        except Exception as e:
            st.error(f"Error loading listings: {e}")

    with tab_add:
        st.markdown(
            """
            <div class="warning-box">
                <h4>⚠️ IMPORTANT LOGISTICS & DATA ACCURACY NOTICE</h4>
                Please ensure you input the <b>exact price, location address, unit count, and weight (in KG)</b> for your produce.
                Inaccurate details will cause transport delays or order cancellations.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("add_product_form", clear_on_submit=True):
            farming_cat = st.selectbox("Category", AGRI_CATEGORIES)
            prod_scale = st.selectbox("Supply Scale", ["Large Scale / Commercial Wholesale", "Small Scale / Retail"])
            title = st.text_input("Product Title (e.g., 50kg Bags of White Maize)")

            c1, c2, c3 = st.columns(3)
            with c1:
                price = st.number_input("Exact Unit Price (₦)", min_value=1000, value=50000, step=1000)
            with c2:
                quantity = st.number_input("Exact Available Stock Quantity (Units)", min_value=1, value=50)
            with c3:
                unit_weight = st.number_input("Exact Weight per Unit (KG)", min_value=0.5, value=50.0, step=1.0)

            loc_col1, loc_col2 = st.columns([1, 2])
            with loc_col1:
                location = st.selectbox("Farm Region / State", NIGERIAN_STATES, index=24)
            with loc_col2:
                exact_address = st.text_input("Exact Farm Pickup Location / Landmark", placeholder="e.g. Km 12 Farm Settlement Road, Owode Egba, Ogun State")

            uploaded_file = st.file_uploader("Upload Produce Photo", type=["jpg", "jpeg", "png"])
            submit_product = st.form_submit_button("PUBLISH PRODUCT TO MARKETPLACE 🚀")

            if submit_product:
                if not uploaded_file:
                    st.error("Please attach a produce photo.")
                elif not title:
                    st.error("Please enter a title.")
                elif not exact_address.strip():
                    st.error("Please specify the exact farm pickup address so logistics partners can locate your farm easily.")
                else:
                    img_bytes = uploaded_file.read()
                    img = Image.open(io.BytesIO(img_bytes))
                    is_valid, msg = verify_farm_photo(img)

                    if not is_valid:
                        st.error(f"Image issue: {msg}")
                    else:
                        img_url = upload_product_photo(img_bytes, uploaded_file.name)
                        new_id = f"FTN-{random.randint(1000, 9999)}"
                        product_data = {
                            "id": new_id,
                            "seller": st.session_state.username,
                            "category": farming_cat,
                            "scale": prod_scale,
                            "item": title,
                            "location": location,
                            "exact_farm_address": exact_address.strip(),
                            "price_ngn": price,
                            "quantity": quantity,
                            "unit_weight_kg": unit_weight,
                            "image_url": img_url,
                        }
                        supabase.table("listings").insert(product_data).execute()
                        st.success("🎉 Produce listed successfully with verified logistics location!")

# ==============================================================================
# 11. FARMER SALES & ESCROW LEDGER WITH DUAL SIGN-OFF & PAYSTACK WITHDRAWAL
# ==============================================================================
elif navigation == "💰 Farmer Sales & Escrow":
    st.subheader("💰 Confirmed Sales & Escrow Ledger")

    tab_sales, tab_payout = st.tabs(["📊 Sales Orders & Sign-Off Status", "💼 Farmer Wallet & Bank Payouts"])

    with tab_sales:
        try:
            farmer_listings = supabase.table("listings").select("id").eq("seller", st.session_state.username).execute().data
            if farmer_listings:
                f_ids = [l["id"] for l in farmer_listings]
                tx_res = supabase.table("transactions").select("*").in_("listing_id", f_ids).execute().data

                if tx_res:
                    df_tx = pd.DataFrame(tx_res)
                    paid_df = df_tx[df_tx["status"].isin(["PAID_VERIFIED", "FARMER_DISPATCHED", "DELIVERED_VERIFIED"])]
                    total_sales = paid_df["amount"].sum() if not paid_df.empty else 0.0

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Total Confirmed Sales", f"₦{total_sales:,.2f}")
                    with m2:
                        st.metric("Active Escrow Orders", len(paid_df))
                    with m3:
                        st.metric("Total Transactions", len(tx_res))

                    st.divider()

                    for tx in tx_res:
                        with st.container(border=True):
                            tc1, tc2, tc3 = st.columns([2, 2, 1.5])
                            with tc1:
                                st.markdown(f"**Order ID:** `{tx['id']}`")
                                st.markdown(f"**Item:** {tx['item']} ({tx.get('quantity_bought', 1)} units)")
                                st.markdown(f"**Buyer Name:** {tx['buyer']}")
                            with tc2:
                                st.markdown(f"**Subtotal:** ₦{float(tx['amount']):,.2f}")
                                st.markdown(f"**Delivery Destination:** {tx.get('delivery_address', 'N/A')}")
                                
                                f_sign = tx.get("farmer_signoff", False)
                                b_sign = tx.get("buyer_signoff", False)
                                
                                st.markdown(f"**Farmer Dispatch Sign-Off:** {'🟢 Complete' if f_sign else '⏳ Pending'}")
                                st.markdown(f"**Buyer Delivery Sign-Off:** {'🟢 Complete' if b_sign else '⏳ Pending'}")

                            with tc3:
                                status_str = tx.get("status", "PENDING")
                                
                                # FARMER MANUAL SIGN-OFF BUTTON IN BROWN
                                if not f_sign and status_str in ["PAID_VERIFIED", "PAYMENT_INITIATED"]:
                                    st.markdown(
                                        '<div class="warning-box" style="padding:8px; font-size:0.8rem; margin-bottom:8px;">'
                                        '<b>Farmer Action Required:</b> Click below only when produce is handed over to logistics carrier.'
                                        '</div>',
                                        unsafe_allow_html=True
                                    )
                                    if st.button("🚚 CONFIRM DISPATCH TO CARRIER", key=f"f_sign_{tx['id']}"):
                                        supabase.table("transactions").update({
                                            "farmer_signoff": True,
                                            "status": "FARMER_DISPATCHED" if not b_sign else "DELIVERED_VERIFIED"
                                        }).eq("id", tx["id"]).execute()
                                        st.success("Dispatch confirmed! Awaiting buyer receipt sign-off.")
                                        st.rerun()

                                elif f_sign and not b_sign:
                                    st.info("🚚 Dispatched to carrier. Awaiting buyer inspection & sign-off.")
                                
                                elif f_sign and b_sign:
                                    st.markdown(
                                        '<div class="alert-success-box" style="padding:10px; font-size:0.85rem;">'
                                        '🎉 <b>Buyer Confirmed Receipt!</b><br>Funds fully unlocked in your wallet.'
                                        '</div>',
                                        unsafe_allow_html=True
                                    )

                else:
                    st.info("No sales records found.")
            else:
                st.info("No active listings found.")
        except Exception as e:
            st.error(f"Error loading sales: {e}")

    with tab_payout:
        st.markdown("### 🏦 Withdraw Unlocked Earnings to Bank (Paystack)")
        
        try:
            farmer_listings = supabase.table("listings").select("id").eq("seller", st.session_state.username).execute().data
            unlocked_balance = 0.0
            pending_balance = 0.0

            if farmer_listings:
                f_ids = [l["id"] for l in farmer_listings]
                all_tx = supabase.table("transactions").select("*").in_("listing_id", f_ids).execute().data
                
                for tx in all_tx:
                    amt = float(tx.get("amount", 0.0))
                    f_sign = tx.get("farmer_signoff", False)
                    b_sign = tx.get("buyer_signoff", False)
                    
                    if f_sign and b_sign:
                        unlocked_balance += amt
                    elif tx.get("status") in ["PAID_VERIFIED", "FARMER_DISPATCHED"]:
                        pending_balance += amt

            b1, b2 = st.columns(2)
            with b1:
                st.metric("🟢 Unlocked & Available to Withdraw", f"₦{unlocked_balance:,.2f}")
            with b2:
                st.metric("⏳ Locked in Dual-Signoff Escrow", f"₦{pending_balance:,.2f}")

            if unlocked_balance > 0:
                st.markdown(
                    """
                    <div class="alert-success-box">
                        <b>✅ NOTIFICATION TO FARMER:</b> The buyer has received and confirmed your produce delivery! Your escrow earnings are now fully unlocked. You may request your Paystack bank transfer below.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.caption("🔒 Funds unlock automatically as soon as the buyer clicks their confirmation sign-off upon receiving produce.")

            st.divider()
            
            with st.form("withdrawal_form"):
                st.markdown("#### Enter Payout Bank Details")
                p_bank = st.selectbox("Select Bank Name", NIGERIAN_BANKS)
                p_acc_num = st.text_input("Account Number (10 Digits)", max_chars=10)
                p_acc_name = st.text_input("Account Name")
                p_amount = st.number_input("Withdrawal Amount (₦)", min_value=1000.0, max_value=max(unlocked_balance, 1000.0), value=max(unlocked_balance, 1000.0))

                submit_withdraw = st.form_submit_button("REQUEST PAYSTACK BANK WITHDRAWAL 🏦")

                if submit_withdraw:
                    if unlocked_balance < p_amount:
                        st.error("Insufficient unlocked balance. Earnings unlock once buyer signs off delivery.")
                    elif len(p_acc_num) != 10 or not p_acc_num.isdigit():
                        st.error("Please enter a valid 10-digit account number.")
                    elif not p_acc_name.strip():
                        st.error("Please enter account holder name.")
                    else:
                        payout_ref = f"FTN-PO-{random.randint(100000, 999999)}"
                        payout_record = {
                            "id": payout_ref,
                            "farmer": st.session_state.username,
                            "bank_name": p_bank,
                            "account_number": p_acc_num,
                            "account_name": p_acc_name,
                            "amount": p_amount,
                            "status": "PROCESSING_PAYSTACK_TRANSFER",
                        }
                        supabase.table("payouts").insert(payout_record).execute()
                        st.success(f"🎉 Payout request of ₦{p_amount:,.2f} submitted! Paystack transfer processing to {p_bank} ({p_acc_num}).")

        except Exception as e:
            st.error(f"Error processing payouts: {e}")

# ==============================================================================
# 12. BUYER ORDERS VIEW WITH DUAL SIGN-OFF & WARNING BANNER
# ==============================================================================
elif navigation == "📦 My Orders & Escrow":
    st.subheader("📦 My Purchased Orders & Delivery Sign-Off")

    st.markdown(
        """
        <div class="alert-danger-box">
            <h4>🛑 CRITICAL SECURITY WARNING TO BUYERS</h4>
            <b>DO NOT CLICK</b> the delivery confirmation sign-off button below until you have <b>physically received and inspected</b> your farm produce from the freight carrier.
            <br>Clicking sign-off immediately unlocks escrow funds to the farmer and completes the contract.
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        orders = supabase.table("transactions").select("*").eq("buyer", st.session_state.username).execute().data
        if not orders:
            st.info("No orders found.")
        else:
            for ord_item in orders:
                with st.container(border=True):
                    oc1, oc2, oc3 = st.columns([2, 2, 1.5])
                    with oc1:
                        st.markdown(f"**Order ID:** `{ord_item['id']}`")
                        st.markdown(f"**Item:** {ord_item['item']} ({ord_item.get('quantity_bought', 1)} units)")
                        st.markdown(f"**Delivery Address:** {ord_item.get('delivery_address', 'N/A')}")
                    with oc2:
                        st.markdown(f"**Total Amount Paid:** ₦{float(ord_item.get('total_paid', ord_item['amount'])):,.2f}")
                        
                        f_sign = ord_item.get("farmer_signoff", False)
                        b_sign = ord_item.get("buyer_signoff", False)
                        
                        st.markdown(f"**Farmer Dispatch:** {'🟢 Complete' if f_sign else '⏳ Awaiting Farmer Dispatch'}")
                        st.markdown(f"**Buyer Sign-Off:** {'🟢 Verified Received' if b_sign else '⏳ Pending Buyer Sign-Off'}")

                    with oc3:
                        if not b_sign:
                            # DISTINCT BROWN SIGN-OFF BUTTON FOR BUYER
                            if st.button("✅ CONFIRM DELIVERY RECEIVED", key=f"b_sign_{ord_item['id']}"):
                                new_status = "DELIVERED_VERIFIED" if f_sign else "BUYER_RECEIVED_PENDING_FARMER"
                                supabase.table("transactions").update({
                                    "buyer_signoff": True,
                                    "status": new_status
                                }).eq("id", ord_item["id"]).execute()
                                st.success("🎉 Delivery verified! Escrow funds unlocked for the farmer.")
                                st.rerun()
                        else:
                            st.markdown(
                                '<div class="alert-success-box" style="padding:10px; text-align:center;">'
                                '✅ <b>Order Completed & Signed Off</b>'
                                '</div>',
                                unsafe_allow_html=True
                            )

    except Exception as e:
        st.error(f"Error loading orders: {e}")

# ==============================================================================
# 13. REVENUE DASHBOARD (ADMIN)
# ==============================================================================
elif navigation == "📈 Revenue Dashboard":
    st.subheader("📈 Marketplace GMV & Platform Revenue")
    try:
        tx_data = supabase.table("transactions").select("*").in_("status", ["PAID_VERIFIED", "DELIVERED_VERIFIED", "FARMER_DISPATCHED"]).execute().data
        if tx_data:
            df_tx = pd.DataFrame(tx_data)
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Gross Volume (GMV)", f"₦{df_tx['amount'].sum():,.2f}")
            with m2:
                st.metric("Platform Revenue (10%)", f"₦{df_tx['commission'].sum():,.2f}")
            with m3:
                st.metric("Completed Transactions", len(df_tx))

            st.divider()
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("No completed verified transactions yet.")
    except Exception as e:
        st.error(f"Error loading revenue metrics: {e}")

# ==============================================================================
# 14. SUPPORT & AI HELPDESK MODULE
# ==============================================================================
elif navigation == "💬 Support & AI Helpdesk":
    st.subheader("💬 AI Dispute Support & Helpdesk")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📝 Submit Ticket")
        with st.form("support_ticket_form", clear_on_submit=True):
            msg_input = st.text_area("Describe your issue or order inquiry...", height=140)
            submit_ticket = st.form_submit_button("SEND TO AI SUPPORT 🚀")

        if submit_ticket:
            if msg_input.strip():
                ai_reply = generate_ai_support_response(st.session_state.username, st.session_state.user_role, msg_input)
                payload = {
                    "user_email": st.session_state.email,
                    "user_role": st.session_state.user_role,
                    "message": msg_input.strip(),
                    "response": ai_reply,
                    "status": "In Progress"
                }
                supabase.table("support_messages").insert(payload).execute()
                st.success("Ticket submitted! Check history for AI response.")
                st.rerun()

    with col2:
        st.markdown("### 📜 Support History")
        try:
            tickets = (
                supabase.table("support_messages")
                .select("*")
                .eq("user_email", st.session_state.email)
                .order("created_at", desc=True)
                .execute()
                .data
            )

            if not tickets:
                st.info("No previous support chats.")
            else:
                for t in tickets:
                    with st.expander(f"Ticket #{t['id']} | {t.get('created_at', '')[:10]}", expanded=True):
                        st.markdown(
                            f'<div class="user-msg-box"><b>👤 {st.session_state.username}:</b><br>{t["message"]}</div>',
                            unsafe_allow_html=True
                        )
                        if t.get("response"):
                            st.markdown(
                                f'<div class="ai-msg-box"><b>🤖 Feed The Nations AI:</b><br>{t["response"]}</div>',
                                unsafe_allow_html=True
                            )
        except Exception as e:
            st.error(f"Error loading history: {e}")
