import os
import random
import pandas as pd
from PIL import Image, ImageStat
import requests
import streamlit as st
from supabase import Client, create_client

# ==============================================================================
# 🗝️ CONFIGURATION & API KEYS
# ==============================================================================
SUPABASE_URL = "https://rewewstbknigolxiozwp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJld2V3c3Ria25pZ29seGlvendwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNDU5MTUsImV4cCI6MjEwMzkyMTkxNX0.s1reBkT9vmYSKGM0yPJTJiAWxT0xxdO446GVOI6ib3U"

PAYSTACK_SECRET_KEY = "sk_live_5d70f03c20eea14b71be5b116e453e6a6848eebe"
PAYSTACK_CALLBACK_URL = "https://feed-the-nations.onrender.com"

# ==============================================================================
# 1. PAGE CONFIG & MOBILE-RESPONSIVE STYLING
# ==============================================================================
st.set_page_config(
    page_title="FEED THE NATIONS - Direct Agri Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with Animated Brand Header & Distinct Colorful Custom Button Styling
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Poppins:wght@600;700;800&display=swap');

    :root {
        --primary-green: #008751;
        --accent-red: #D90429;
        --earth-brown: #5C3D2E;
        --light-bg: #F8FAF8;
        --dark-text: #1B2021;
    }

    .stApp {
        background-color: var(--light-bg);
        color: var(--dark-text);
        font-family: 'Poppins', sans-serif;
    }

    h1, h2, h3 {
        color: var(--primary-green) !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }

    /* ANIMATED SWEEPING LIGHT EFFECT FOR HEADER */
    @keyframes sweepLight {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* BRAND HEADER WITH SWEEPING ANIMATION */
    .brand-header {
        position: relative;
        background: linear-gradient(
            110deg, 
            #008751 0%, 
            #2A7B4C 35%, 
            #ffffff 50%, 
            #2A7B4C 65%, 
            #5C3D2E 100%
        );
        background-size: 200% 100%;
        animation: sweepLight 4s linear infinite;
        padding: clamp(14px, 3.5vw, 28px);
        border-radius: 12px;
        text-align: center;
        margin-bottom: 22px;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(1.5rem, 5.5vw, 2.7rem);
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4);
    }

    .brand-icons {
        font-size: clamp(1.2rem, 3.5vw, 2rem);
        margin-top: 6px;
        letter-spacing: 8px;
    }

    .brand-subtext {
        color: #F4F7F4;
        font-size: clamp(0.8rem, 2.5vw, 1.05rem);
        font-weight: 600;
        margin-top: 8px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }

    /* COLORFUL LOG IN & ACTION BUTTONS WITH SPECIAL FONT */
    div.stButton > button {
        background: linear-gradient(135deg, #008751 0%, #11998e 50%, #38ef7d 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        border: None !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 135, 81, 0.35) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #00b066 0%, #11998e 50%, #28c76f 100%) !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 6px 20px rgba(0, 135, 81, 0.45) !important;
        color: #FFFFFF !important;
    }

    div.stButton > button:active {
        transform: translateY(1px) scale(0.99) !important;
    }

    /* CARDS & UI CONTAINERS */
    .listing-card {
        background-color: white;
        border-radius: 12px;
        padding: clamp(12px, 2.5vw, 20px);
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        border-top: 4px solid var(--primary-green);
        margin-bottom: 20px;
    }

    .escrow-box {
        background-color: #FFF8F8;
        border-left: 4px solid var(--accent-red);
        padding: 10px 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 0.9rem;
    }

    .negotiate-box {
        background-color: #F0F7F2;
        border: 1px solid #C2E2C8;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. SUPABASE & PAYSTACK INITIALIZATION
# ==============================================================================
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

AGRI_CATEGORIES = [
    "🌾 Crop Farming (Rice, Beans, Maize, Raw Grains)",
    "🏭 Agro-Processing & Packaged Goods (Flour, Oils, Branded Foods)",
    "🐂 Livestock Farming",
    "🐓 Poultry Farming",
    "🐟 Fishery / Aquaculture",
    "🍎 Horticulture (Fruits & Vegetables)",
    "🥛 Dairy Farming",
]

LOGISTICS_PARTNERS = {
    "GIG Logistics (Agri-Freight Division)": {
        "phone": "+2348130001122",
        "display": "+234 813 000 1122",
    },
    "Kwik Delivery (Heavy Haulage)": {
        "phone": "+2348092223344",
        "display": "+234 809 222 3344",
    },
    "Max.ng Freight & Inter-State": {
        "phone": "+2347008009000",
        "display": "+234 700 800 9000",
    },
    "Farmers Union Local Transport": {
        "phone": "+2348023334455",
        "display": "+234 802 333 4455",
    },
}

def verify_farm_photo(image):
    try:
        img = image.convert("RGB")
        stat = ImageStat.Stat(img)
        if sum(stat.stddev) / len(stat.stddev) < 12:
            return (
                False,
                "Image appears blank or non-product graphic. PLEASE UPLOAD REAL PICTURE OF FARM PRODUCTS.",
            )
        return True, "Valid photo"
    except Exception:
        return (
            False,
            "Invalid image file format. PLEASE UPLOAD REAL PICTURE OF FARM PRODUCTS.",
        )

def initialize_paystack_payment(email, amount_ngn, reference):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": int(amount_ngn * 100),
        "reference": reference,
        "callback_url": PAYSTACK_CALLBACK_URL,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# ==============================================================================
# 3. SESSION STATE MANAGEMENT
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "email" not in st.session_state:
    st.session_state.email = ""

# ==============================================================================
# 4. ANIMATED BRAND HEADER (SWEEPING LIGHT EFFECT)
# ==============================================================================
st.markdown(
    """
<div class="brand-header">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <div class="brand-icons">🌾 🌽 🐂 🐟 🐓</div>
    <p class="brand-subtext">Direct Farm-to-Buyer Marketplace • Zero Middlemen • Escrow Protection</p>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. USER AUTHENTICATION & SUPABASE PROFILES SYNC
# ==============================================================================
if not st.session_state.authenticated:
    st.subheader("🔑 Access Portal")
    auth_mode = st.radio(
        "Choose Action", ["Login", "Register Account"], horizontal=True
    )

    email_input = st.text_input("Email Address").strip().lower()
    password_input = st.text_input("Password", type="password")

    if auth_mode == "Register Account":
        selected_role = st.selectbox(
            "Account Type",
            [
                "Buyer (Wholesaler, Hotel, Processor)",
                "Farmer / Producer",
                "Platform Admin",
            ],
        )
        full_name = st.text_input("Full Name / Farm Name")
        farming_cat = (
            st.selectbox("Primary Agricultural Category", AGRI_CATEGORIES)
            if "Farmer" in selected_role
            else "All Categories"
        )

        if st.button("Create Account", use_container_width=True):
            if email_input and password_input and full_name:
                try:
                    if "Farmer" in selected_role:
                        assigned_role = "Farmer"
                    elif "Admin" in selected_role:
                        assigned_role = "Admin"
                    else:
                        assigned_role = "Buyer"

                    # 1. Sign up user in Supabase Auth
                    res = supabase.auth.sign_up(
                        {
                            "email": email_input,
                            "password": password_input,
                            "options": {
                                "data": {
                                    "full_name": full_name,
                                    "role": assigned_role,
                                    "category": farming_cat,
                                }
                            },
                        }
                    )

                    # 2. Sync profile into custom 'profiles' table
                    if res.user:
                        profile_data = {
                            "id": res.user.id,
                            "email": email_input,
                            "full_name": full_name,
                            "role": assigned_role,
                            "category": farming_cat,
                        }
                        supabase.table("profiles").insert(
                            profile_data
                        ).execute()

                    st.success(
                        "🎉 Account created successfully! Please check your email address for complete registration setup before logging in."
                    )
                except Exception as e:
                    st.error(f"Error creating account: {str(e)}")
            else:
                st.error("Please fill out all required fields.")
    else:
        if st.button("LOG IN ➔", use_container_width=True):
            if email_input and password_input:
                try:
                    res = supabase.auth.sign_in_with_password(
                        {"email": email_input, "password": password_input}
                    )
                    user_metadata = res.user.user_metadata
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_metadata.get(
                        "role", "Buyer"
                    )
                    st.session_state.username = user_metadata.get(
                        "full_name", email_input
                    )
                    st.session_state.email = email_input
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
            else:
                st.error("Please enter email and password.")
    st.stop()

# ==============================================================================
# 6. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
st.sidebar.markdown(f"**Role:** `{st.session_state.user_role}`")

if st.sidebar.button("Log Out"):
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.rerun()

st.sidebar.divider()

if st.session_state.user_role == "Farmer":
    nav_options = ["📦 My Active Products", "➕ Add New Product"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["📈 Founder Revenue Dashboard", "🛒 Browse Marketplace"]

navigation = st.sidebar.radio("Navigation", nav_options)

# ==============================================================================
# 7. FOUNDER REVENUE DASHBOARD (ADMIN VIEW)
# ==============================================================================
if navigation == "📈 Founder Revenue Dashboard":
    st.subheader("📊 Founder Revenue & Category Growth Analytics")
    st.caption(
        "Live transaction volumes and 10% platform commissions pulled directly from Supabase."
    )

    try:
        response = supabase.table("transactions").select("*").execute()
        tx_data = response.data

        if tx_data:
            df_tx = pd.DataFrame(tx_data)
            total_gmv = df_tx["amount"].sum()
            total_commission = df_tx["commission"].sum()
            total_orders = len(df_tx)

            m1, m2, m3 = st.columns(3)
            m1.metric("Gross Merchandise Value (GMV)", f"₦{total_gmv:,.2f}")
            m2.metric("Founder Revenue (10%)", f"₦{total_commission:,.2f}")
            m3.metric("Completed Transactions", total_orders)

            st.divider()
            st.markdown("### 📂 Revenue Breakdown by Category")

            category_summary = []
            for cat in AGRI_CATEGORIES:
                cat_txs = df_tx[df_tx["category"] == cat]
                cat_gmv = cat_txs["amount"].sum() if not cat_txs.empty else 0
                cat_comm = (
                    cat_txs["commission"].sum() if not cat_txs.empty else 0
                )

                category_summary.append(
                    {
                        "Category": cat,
                        "Total Sales (GMV)": f"₦{cat_gmv:,.2f}",
                        "Platform Revenue (10%)": f"₦{cat_comm:,.2f}",
                        "Orders": len(cat_txs),
                    }
                )

            st.table(pd.DataFrame(category_summary))
            st.markdown("### 📜 Real-Time Transaction Logs")
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("No completed transactions recorded in Supabase yet.")
    except Exception as e:
        st.error(f"Error fetching revenue records: {str(e)}")

# ==============================================================================
# 8. BUYER MARKETPLACE & PAYSTACK ESCROW PAYMENT
# ==============================================================================
elif navigation in ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]:
    st.subheader("🛒 Direct Farm Produce Marketplace")

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        buying_scale = st.selectbox(
            "Buying Scale",
            [
                "All Scales",
                "Large Scale / Commercial Wholesale",
                "Small Scale / Retail",
            ],
        )
    with c_f2:
        category_filter = st.selectbox(
            "Agricultural Category", ["All Categories"] + AGRI_CATEGORIES
        )

    st.divider()

    try:
        query = supabase.table("listings").select("*")
        if buying_scale != "All Scales":
            query = query.eq("scale", buying_scale)
        if category_filter != "All Categories":
            query = query.eq("category", category_filter)

        listings = query.execute().data

        if not listings:
            st.info("No products currently listed matching your criteria.")

        for item in listings:
            st.markdown('<div class="listing-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])

            with col1:
                if item.get("image_url"):
                    st.image(item["image_url"], use_container_width=True)
                else:
                    st.info("📷 Photo Verified")
                st.caption(f"Scale: **{item.get('scale', 'General')}**")

            with col2:
                st.markdown(f"### {item['item']}")
                st.write(f"**Category:** `{item.get('category')}`")
                st.write(
                    f"**Farmer:** {item['seller']} | 📍 **Location:** {item['location']}"
                )

                raw_price = float(item["price_ngn"])
                platform_fee = raw_price * 0.10

                st.markdown(f"**Base Produce Price:** ₦{raw_price:,.2f}")
                st.markdown(
                    f"**Platform Commission (10%):** ₦{platform_fee:,.2f}"
                )

                st.markdown("#### 🚚 Direct Logistics Bargaining & Delivery")
                selected_partner = st.selectbox(
                    f"Logistics Partner for {item['id']}",
                    list(LOGISTICS_PARTNERS.keys()),
                )
                partner_info = LOGISTICS_PARTNERS[selected_partner]

                agreed_freight = st.number_input(
                    f"Agreed Delivery Fee (₦) after bargaining",
                    min_value=0,
                    value=25000,
                    step=5000,
                    key=f"freight_{item['id']}",
                )

                st.markdown(
                    f"""
                <div class="negotiate-box">
                    <strong>🤝 Bargain Directly with {selected_partner}:</strong><br>
                    Contact via WhatsApp/Call: <code>{partner_info['display']}</code><br>
                    <a href="https://wa.me/{partner_info['phone']}" target="_blank" style="color:#008751; font-weight:bold;">💬 Click to Negotiate Freight Rate</a>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                final_total = raw_price + platform_fee + agreed_freight
                st.markdown(f"### **Total Payable: ₦{final_total:,.2f}**")

                if st.button(
                    "PAY VIA PAYSTACK ESCROW 💳", key=f"pay_{item['id']}"
                ):
                    ref = f"FTN-TX-{random.randint(100000, 999999)}"

                    tx_record = {
                        "id": ref,
                        "listing_id": item["id"],
                        "category": item["category"],
                        "item": item["item"],
                        "amount": raw_price,
                        "commission": platform_fee,
                        "freight": agreed_freight,
                        "total_paid": final_total,
                        "buyer": st.session_state.username,
                        "status": "ESCROW_HELD",
                        "paystack_ref": ref,
                    }
                    supabase.table("transactions").insert(tx_record).execute()

                    pay_resp = initialize_paystack_payment(
                        st.session_state.email, final_total, ref
                    )

                    if pay_resp.get("status"):
                        auth_url = pay_resp["data"]["authorization_url"]
                        st.success(
                            "🔒 Escrow order initiated! Proceed below to complete payment."
                        )
                        st.markdown(
                            f'<a href="{auth_url}" target="_blank" style="display:inline-block; background: linear-gradient(135deg, #008751 0%, #11998e 100%); color:white; padding:12px 20px; border-radius:8px; text-decoration:none; font-family: Montserrat, sans-serif; font-weight:bold;">Open Paystack Gateway ➔</a>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(
                            "Failed to initialize Paystack gateway. Please check your API secret key at the top of the file."
                        )

            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Marketplace error: {str(e)}")

# ==============================================================================
# 9. FARMER PRODUCT UPLOAD & ACTIVE PRODUCTS
# ==============================================================================
elif navigation == "➕ Add New Product":
    st.subheader("🚜 Publish Product Listing")

    with st.form("add_product_form"):
        farming_cat = st.selectbox(
            "Select Agriculture Category", AGRI_CATEGORIES
        )
        prod_scale = st.selectbox(
            "Supply Scale Category",
            [
                "Large Scale / Commercial Wholesale",
                "Small Scale / Retail",
            ],
        )
        title = st.text_input("Product Title")

        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input(
                "Base Farm Price (₦)",
                min_value=1000,
                value=500000,
                step=10000,
            )
            location = st.text_input("Farm Location / State", value="Ogun State")
        with c2:
            quantity = st.number_input(
                "Available Units / Bags / Crates / Animals", value=50
            )

        st.markdown("#### 📷 Upload Product Photo")
        uploaded_file = st.file_uploader(
            "Upload actual photo of farm products",
            type=["jpg", "jpeg", "png"],
        )

        submitted = st.form_submit_button("PUBLISH PRODUCT LISTING 🚀")

        if submitted:
            if not uploaded_file:
                st.error("⚠️ PLEASE UPLOAD REAL PICTURE OF FARM PRODUCTS")
            else:
                img = Image.open(uploaded_file)
                is_valid, msg = verify_farm_photo(img)

                if not is_valid:
                    st.error(f"⚠️ {msg}")
                elif not title:
                    st.error("Please enter a product title.")
                else:
                    new_id = f"FTN-{random.randint(100, 999)}"
                    product_data = {
                        "id": new_id,
                        "seller": st.session_state.username,
                        "category": farming_cat,
                        "scale": prod_scale,
                        "item": title,
                        "location": location,
                        "price_ngn": price,
                        "quantity": quantity,
                    }
                    supabase.table("listings").insert(product_data).execute()
                    st.success(
                        "🎉 Product published and saved directly to your Supabase database!"
                    )

elif navigation == "📦 My Active Products":
    st.subheader("🚜 My Active Listings")
    try:
        my_items = (
            supabase.table("listings")
            .select("*")
            .eq("seller", st.session_state.username)
            .execute()
            .data
        )

        if my_items:
            for item in my_items:
                st.markdown('<div class="listing-card">', unsafe_allow_html=True)
                st.markdown(f"### {item['item']}")
                st.write(
                    f"Category: `{item.get('category')}` | Base Price: **₦{item['price_ngn']:,.2f}**"
                )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(
                "No active listings found in Supabase. Click 'Add New Product' to get started!"
            )
    except Exception as e:
        st.error(f"Error fetching active listings: {str(e)}")
