import streamlit as st
import pandas as pd
import datetime
import random
from PIL import Image, ImageStat

# ==========================================
# 1. PAGE CONFIG & MOBILE-RESPONSIVE STYLING
# ==========================================
st.set_page_config(
    page_title="FEED THE NATIONS - Direct Agri Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive Mobile & Desktop CSS styling
st.markdown("""
<style>
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
    }

    h1, h2, h3 {
        color: var(--primary-green) !important;
        font-weight: 700;
    }

    /* RESPONSIVE ANIMATED HEADER */
    @keyframes sweepLight {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

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
        padding: clamp(12px, 3vw, 24px);
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-size: clamp(1.4rem, 5vw, 2.5rem);
        font-weight: 900;
        letter-spacing: 1px;
        margin: 0;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4);
    }

    .brand-subtext {
        color: #F4F7F4;
        font-size: clamp(0.8rem, 2.5vw, 1.05rem);
        font-weight: 600;
        margin-top: 6px;
    }

    /* CARD CONTAINERS FOR MOBILE & DESKTOP */
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

    /* Mobile media query tweaks */
    @media only screen and (max-width: 600px) {
        .stButton > button {
            width: 100% !important;
        }
        .listing-card {
            padding: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Shared Categories
AGRI_CATEGORIES = [
    "🌾 Crop Farming (Rice, Beans, Maize, Raw Grains)",
    "🏭 Agro-Processing & Packaged Goods (Flour, Oils, Branded Foods)",
    "🐂 Livestock Farming",
    "🐓 Poultry Farming",
    "🐟 Fishery / Aquaculture",
    "🍎 Horticulture (Fruits & Vegetables)",
    "🥛 Dairy Farming"
]

LOGISTICS_PARTNERS = {
    "GIG Logistics (Agri-Freight Division)": {"phone": "+2348130001122", "display": "+234 813 000 1122"},
    "Kwik Delivery (Heavy Haulage)": {"phone": "+2348092223344", "display": "+234 809 222 3344"},
    "Max.ng Freight & Inter-State": {"phone": "+2347008009000", "display": "+234 700 800 9000"},
    "Farmers Union Local Transport": {"phone": "+2348023334455", "display": "+234 802 333 4455"}
}

# ==========================================
# 2. PERSISTENT SESSION STATE & DATABASE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""

if "user_db" not in st.session_state:
    st.session_state.user_db = {
        "farmer@ftn.com": {"password": "password123", "role": "Farmer", "name": "Musa Adamu", "category": "🐂 Livestock Farming"},
        "buyer@ftn.com": {"password": "password123", "role": "Buyer", "name": "Bisi Akande (Wholesalers)"},
        "admin@ftn.com": {"password": "adminsecret", "role": "Admin", "name": "Founder / Admin"}
    }

if "listings" not in st.session_state:
    st.session_state.listings = [
        {
            "id": "FTN-101",
            "seller": "Musa Adamu",
            "category": "🐂 Livestock Farming",
            "item": "Boran Bull Cattle Herd (Bulk)",
            "scale": "Large Scale / Commercial Wholesale",
            "quantity": 25,
            "location": "Kano State",
            "price_ngn": 6500000,
            "image_obj": None,
            "pre_order": False
        },
        {
            "id": "FTN-102",
            "seller": "Green Harvest Co-op",
            "category": "🌾 Crop Farming (Rice, Beans, Maize, Raw Grains)",
            "item": "Raw Harvested Brown Beans (500 Bags)",
            "scale": "Large Scale / Commercial Wholesale",
            "quantity": 500,
            "location": "Benue State",
            "price_ngn": 18000000,
            "image_obj": None,
            "pre_order": False
        },
        {
            "id": "FTN-103",
            "seller": "Golden Grain Mills",
            "category": "🏭 Agro-Processing & Packaged Goods (Flour, Oils, Branded Foods)",
            "item": "Packaged Parboiled Rice (50kg Bags)",
            "scale": "Large Scale / Commercial Wholesale",
            "quantity": 200,
            "location": "Kebbi State",
            "price_ngn": 10400000,
            "image_obj": None,
            "pre_order": False
        }
    ]

# Transactions Log for Founder Revenue Tracking
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"id": "TX-901", "category": "🐂 Livestock Farming", "item": "Boran Bull Cattle Herd", "amount": 6500000, "commission": 650000, "date": "2026-08-15", "buyer": "Lagos Meat Processing Co."},
        {"id": "TX-902", "category": "🌾 Crop Farming (Rice, Beans, Maize, Raw Grains)", "item": "White Maize (200 Bags)", "amount": 7200000, "commission": 720000, "date": "2026-08-20", "buyer": "Bisi Akande"},
        {"id": "TX-903", "category": "🏭 Agro-Processing & Packaged Goods (Flour, Oils, Branded Foods)", "item": "Groundnut Oil Cans (100 Drums)", "amount": 4800000, "commission": 480000, "date": "2026-08-28", "buyer": "Supermart Superstores"},
        {"id": "TX-904", "category": "🐓 Poultry Farming", "item": "Day-Old Chicks (1,000 Batch)", "amount": 850000, "commission": 85000, "date": "2026-09-01", "buyer": "Sunrise Poultry"}
    ]

# Helper function: Basic image verification
def verify_farm_photo(image):
    try:
        img = image.convert("RGB")
        stat = ImageStat.Stat(img)
        # Check standard deviation to prevent completely blank or plain monochromatic images
        if sum(stat.stddev) / len(stat.stddev) < 12:
            return False, "Image appears blank or featureless. PLEASE UPLOAD REAL PICTURE OF FARM PRODUCTS."
        return True, "Valid photo"
    except Exception:
        return False, "Invalid image format. PLEASE UPLOAD REAL PICTURE OF FARM PRODUCTS."

# ==========================================
# 3. HEADER BANNER
# ==========================================
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <p class="brand-subtext">Direct Farm-to-Buyer Marketplace • Zero Middlemen • Escrow Protection</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTHENTICATION / LOGIN PORTAL
# ==========================================
if not st.session_state.authenticated:
    st.subheader("🔑 Access Portal")
    auth_mode = st.radio("Choose Action", ["Login", "Register Account"], horizontal=True)
    
    email = st.text_input("Email Address").strip().lower()
    password = st.text_input("Password", type="password")
    
    if auth_mode == "Register Account":
        selected_role = st.selectbox("Account Type", ["Buyer (Wholesaler, Hotel, Processor)", "Farmer / Producer"])
        full_name = st.text_input("Full Name / Farm Name")
        farming_cat = st.selectbox("Primary Agricultural Category", AGRI_CATEGORIES) if "Farmer" in selected_role else None
        
        if st.button("Create Account", use_container_width=True):
            if email and password and full_name:
                if email in st.session_state.user_db:
                    st.error("Account already exists with this email! Please log in.")
                else:
                    assigned_role = "Farmer" if "Farmer" in selected_role else "Buyer"
                    st.session_state.user_db[email] = {
                        "password": password,
                        "role": assigned_role,
                        "name": full_name,
                        "category": farming_cat if assigned_role == "Farmer" else "Buyer"
                    }
                    st.success(f"Account created as {assigned_role}! Please log in.")
            else:
                st.error("Please fill out all required fields.")
    else:
        if st.button("Log In", use_container_width=True):
            if email in st.session_state.user_db and st.session_state.user_db[email]["password"] == password:
                user_data = st.session_state.user_db[email]
                st.session_state.authenticated = True
                st.session_state.user_role = user_data["role"]
                st.session_state.username = user_data["name"]
                st.rerun()
            else:
                st.error("Invalid email or password.")
    st.stop()

# ==========================================
# 5. NAVIGATION & ROLE-BASED DASHBOARDS
# ==========================================
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
st.sidebar.markdown(f"**Account Role:** `{st.session_state.user_role}`")

if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.rerun()

st.sidebar.divider()

if st.session_state.user_role == "Farmer":
    nav_options = ["📦 My Active Products", "➕ Add New Product"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["📈 Founder Revenue Dashboard", "🛒 Browse Marketplace"]

navigation = st.sidebar.radio("Navigation", nav_options)

# --------------------------------------------------
# FOUNDER / ADMIN DASHBOARD: REVENUE BY CATEGORY
# --------------------------------------------------
if navigation == "📈 Founder Revenue Dashboard":
    st.subheader("📊 Founder Revenue & Category Growth Analytics")
    st.caption("Track total platform revenue, transaction volumes, and performance across every agricultural category.")
    
    df_tx = pd.DataFrame(st.session_state.transactions)
    
    # Overview Metrics
    total_gmv = df_tx["amount"].sum()
    total_commission = df_tx["commission"].sum()
    total_orders = len(df_tx)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Gross Merchandise Value (GMV)", f"₦{total_gmv:,.2f}")
    m2.metric("Total Founder Revenue (10%)", f"₦{total_commission:,.2f}")
    m3.metric("Completed Transactions", total_orders)
    
    st.divider()
    st.markdown("### 📂 Revenue Breakdown by Agricultural Category")
    
    # Calculate performance per category
    category_summary = []
    for cat in AGRI_CATEGORIES:
        cat_txs = df_tx[df_tx["category"] == cat]
        cat_gmv = cat_txs["amount"].sum() if not cat_txs.empty else 0
        cat_comm = cat_txs["commission"].sum() if not cat_txs.empty else 0
        cat_count = len(cat_txs)
        
        category_summary.append({
            "Category": cat,
            "Total Sales (GMV)": f"₦{cat_gmv:,.2f}",
            "Platform Revenue (10%)": f"₦{cat_comm:,.2f}",
            "Orders Count": cat_count
        })
        
    st.table(pd.DataFrame(category_summary))
    
    st.markdown("### 📜 Recent Transaction History")
    st.dataframe(df_tx[["id", "date", "category", "item", "amount", "commission", "buyer"]], use_container_width=True)

# --------------------------------------------------
# BUYER VIEW: MARKETPLACE & LOGISTICS BARGAINING
# --------------------------------------------------
elif navigation in ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]:
    st.subheader("🛒 Direct Farm Produce Marketplace")
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        buying_scale = st.selectbox("Buying Scale", ["All Scales", "Large Scale / Commercial Wholesale", "Small Scale / Retail"])
    with c_f2:
        category_filter = st.selectbox("Agricultural Category", ["All Categories"] + AGRI_CATEGORIES)
        
    st.divider()

    for item in st.session_state.listings:
        if buying_scale != "All Scales" and item.get("scale") != buying_scale:
            continue
        if category_filter != "All Categories" and category_filter != item.get("category"):
            continue

        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if item.get("image_obj"):
                st.image(item["image_obj"], use_container_width=True)
            else:
                st.info("📷 Photo Verified")
            st.caption(f"Scale: **{item.get('scale', 'General')}**")

        with col2:
            st.markdown(f"### {item['item']}")
            st.write(f"**Category:** `{item.get('category')}`")
            st.write(f"**Farmer:** {item['seller']} | 📍 **Location:** {item['location']}")
            
            raw_price = item['price_ngn']
            platform_fee = raw_price * 0.10
            
            st.markdown(f"**Base Produce Price:** ₦{raw_price:,.2f}")
            st.markdown(f"**Platform Fee (10%):** ₦{platform_fee:,.2f}")
            
            st.markdown("#### 🚚 Direct Logistics Bargaining & Delivery")
            selected_partner = st.selectbox(f"Select Partner for {item['id']}", list(LOGISTICS_PARTNERS.keys()))
            partner_info = LOGISTICS_PARTNERS[selected_partner]
            
            agreed_freight = st.number_input(f"Agreed Delivery Fee (₦) after bargaining with {selected_partner}", min_value=0, value=25000, step=5000, key=f"freight_{item['id']}")
            
            st.markdown(f"""
            <div class="negotiate-box">
                <strong>🤝 Bargain Directly with {selected_partner}:</strong><br>
                Contact via WhatsApp/Call: <code>{partner_info['display']}</code> to negotiate exact freight cost to your location.<br>
                <a href="https://wa.me/{partner_info['phone']}" target="_blank" style="color:#008751; font-weight:bold;">💬 Click to Chat & Bargain Freight Rate</a>
            </div>
            """, unsafe_allow_html=True)
            
            final_total = raw_price + platform_fee + agreed_freight
            st.markdown(f"### **Total Payable: ₦{final_total:,.2f}**")
            
            if st.button("Pay via Paystack Escrow 💳", key=f"pay_{item['id']}"):
                st.markdown("""
                <div class="escrow-box">
                    <strong>🔒 Escrow Activated:</strong> Funds are securely held and will only be released to the farmer and logistics company after you receive and confirm the delivery!
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# FARMER VIEW: PRODUCT UPLOAD & IMAGE VALIDATION
# --------------------------------------------------
elif navigation == "➕ Add New Product":
    st.subheader("🚜 Publish Product Listing")
    
    with st.form("add_product_form"):
        farming_cat = st.selectbox("Select Agriculture Category", AGRI_CATEGORIES)
        prod_scale = st.selectbox("Supply Scale Category", ["Large Scale / Commercial Wholesale", "Small Scale / Retail"])
        title = st.text_input("Product Title")
        
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Base Farm Price (₦)", min_value=1000, value=500000, step=10000)
            location = st.text_input("Farm Location / State", value="Ogun State")
        with c2:
            quantity = st.number_input("Available Units / Bags / Crates / Animals", value=50)
            
        st.markdown("#### 📷 Upload Product Photo")
        uploaded_file = st.file_uploader("Upload actual photo of livestock/crop/packaged product", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Publish Product Listing")
        
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
                    new_item = {
                        "id": f"FTN-{random.randint(200, 999)}",
                        "seller": st.session_state.username,
                        "category": farming_cat,
                        "scale": prod_scale,
                        "item": title,
                        "location": location,
                        "price_ngn": price,
                        "quantity": quantity,
                        "image_obj": img,
                        "pre_order": False
                    }
                    st.session_state.listings.append(new_item)
                    st.success("🎉 Product listing verified & successfully published!")

elif navigation == "📦 My Active Products":
    st.subheader("🚜 My Active Listings")
    my_items = [i for i in st.session_state.listings if i["seller"] == st.session_state.username]
    if my_items:
        for item in my_items:
            st.markdown('<div class="listing-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                if item.get("image_obj"):
                    st.image(item["image_obj"], width=200)
            with c2:
                st.markdown(f"### {item['item']}")
                st.write(f"Category: `{item.get('category')}` | Price: **₦{item['price_ngn']:,.2f}**")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No active listings found. Click 'Add New Product' to get started!")
