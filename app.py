import streamlit as st
import pandas as pd
import datetime
import random

# ==========================================
# 1. PAGE CONFIG & CUSTOM THEMING (UI/UX)
# Green White Green, Rich Earth Brown, Crimson Red
# ==========================================
st.set_page_config(
    page_title="FEED THE NATIONS - Direct Agri Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS for the specified color palette
st.markdown("""
<style>
    /* Theme Palette */
    :root {
        --primary-green: #008751;   /* Nigerian Flag Green / Agriculture */
        --accent-red: #D90429;      /* Action / Highlight / Escrow Alert */
        --earth-brown: #5C3D2E;     /* Soil / Livestock Earthiness */
        --light-bg: #F4F7F4;        /* Soft White / Light Grey */
        --dark-text: #1B2021;
    }

    /* Main background & Headers */
    .stApp {
        background-color: var(--light-bg);
        color: var(--dark-text);
    }

    h1, h2, h3 {
        color: var(--primary-green) !important;
        font-weight: 700;
    }

    /* Custom Header Bar */
    .brand-header {
        background: linear-gradient(90deg, #008751 0%, #FFFFFF 50%, #008751 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid var(--earth-brown);
    }
    
    .brand-title {
        color: #008751;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: 1.5px;
        margin: 0;
        text-shadow: 1px 1px 2px #5C3D2E;
    }

    /* Buttons Styling */
    .stButton > button {
        background-color: var(--primary-green);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: var(--earth-brown);
        color: white;
    }

    /* Escrow & Fee Callout Box */
    .escrow-box {
        background-color: #FFF3F3;
        border-left: 5px solid var(--accent-red);
        padding: 12px;
        border-radius: 6px;
        margin-top: 10px;
    }

    /* Card styling */
    .listing-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid var(--earth-brown);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # "Farmer" or "Buyer"
if "username" not in st.session_state:
    st.session_state.username = ""
if "listings" not in st.session_state:
    # Seed data showcasing superior African agricultural offerings
    st.session_state.listings = [
        {
            "id": "FTN-101",
            "seller": "Musa Adamu Farms",
            "category": "Livestock",
            "item": "Boran Cattle (Bull)",
            "weight_kg": 420,
            "location": "Kano, Nigeria",
            "price_ngn": 650000,
            "verified_health": True,
            "video_url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
            "pre_order": False
        },
        {
            "id": "FTN-102",
            "seller": "Green Harvest Co-op",
            "category": "Crop Produce",
            "item": "Organic Yellow Maize (50kg Bags)",
            "quantity": 100,
            "location": "Benue, Nigeria",
            "price_ngn": 32000,
            "verified_health": True,
            "pre_order": False
        },
        {
            "id": "FTN-103",
            "seller": "Agro-Vision Estates",
            "category": "Crop Produce",
            "item": "Fresh Plum Tomatoes (Pre-Harvest)",
            "quantity": 500,
            "location": "Oyo, Nigeria",
            "price_ngn": 18000,
            "verified_health": True,
            "pre_order": True,
            "harvest_date": "2026-10-15"
        }
    ]

# ==========================================
# 3. HEADER BANNER
# ==========================================
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">🇳🇬 FEED THE NATIONS</h1>
    <p style="color: #5C3D2E; font-weight: 600; margin:0;">
        Direct Farm-to-Buyer Marketplace • Zero Middlemen • Escrow Protection
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. AUTHENTICATION / LOGIN PORTAL
# ==========================================
def render_login_portal():
    st.subheader("🔑 Welcome to Feed The Nations")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Access Your Portal")
        auth_mode = st.radio("Choose Action", ["Login", "Register New Account"], horizontal=True)
        role = st.selectbox("Select Role", ["Buyer (Hotel, Processor, Wholesaler)", "Farmer / Livestock Producer"])
        
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Register New Account":
            phone = st.text_input("Phone Number (for SMS/USSD alerts)")
            location = st.text_input("State / City (e.g. Ogun State)")
            
        if st.button("Proceed", use_container_width=True):
            if email and password:
                # -----------------------------------------------------------
                # SUPABASE INTEGRATION PLACEHOLDER:
                # supabase.auth.sign_in_with_password({"email": email, "password": password})
                # -----------------------------------------------------------
                st.session_state.authenticated = True
                st.session_state.user_role = "Farmer" if "Farmer" in role else "Buyer"
                st.session_state.username = email.split('@')[0].capitalize()
                st.success(f"Welcome back, {st.session_state.username}!")
                st.rerun()
            else:
                st.error("Please fill in required login details.")

    with col2:
        st.info("### Why FEED THE NATIONS beats traditional markets?")
        st.markdown("""
        * 🛡️ **Escrow Guaranteed:** Payments released only after verified delivery.
        * 🐄 **Livestock Smart-Tagging:** Veterinary health status & video proof before purchase.
        * 💰 **Direct Pricing:** Farmers earn up to **35% more**; buyers pay less by eliminating middlemen.
        * 🤝 **Forward Contracting:** Lock in future harvests at fixed prices today.
        """)

if not st.session_state.authenticated:
    render_login_portal()
    st.stop()

# ==========================================
# 5. AUTHENTICATED USER DASHBOARD
# ==========================================

# Sidebar Controls
st.sidebar.markdown(f"### 👤 Logged in as: **{st.session_state.username}**")
st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.divider()
navigation = st.sidebar.radio("Navigate App", [
    "🛒 Direct Marketplace", 
    "➕ List Produce / Livestock (Farmers)", 
    "📈 Revenue & Fee Calculator",
    "🤝 Pre-Order Forward Contracts"
])

# --------------------------------------------------
# MODULE A: MARKETPLACE (BUYERS & ALL USERS)
# --------------------------------------------------
if navigation == "🛒 Direct Marketplace":
    st.subheader("🌾 Direct Farm Produce & Livestock Market")
    
    category_filter = st.selectbox("Filter Category", ["All", "Livestock", "Crop Produce"])
    
    for item in st.session_state.listings:
        if category_filter != "All" and item["category"] != category_filter:
            continue
            
        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        col_img, col_info, col_pay = st.columns([1, 2, 1.5])
        
        with col_img:
            if item["category"] == "Livestock":
                st.markdown("### 🐂 Live Animal")
                st.caption(f"Estimated Wt: **{item.get('weight_kg', 'N/A')} kg**")
            else:
                st.markdown("### 🌽 Fresh Crop")
                st.caption(f"Qty Available: **{item.get('quantity', 'N/A')} Units**")
            
            if item.get("verified_health"):
                st.success("✅ Vet Checked")

        with col_info:
            st.markdown(f"### {item['item']}")
            st.write(f"**Seller:** {item['seller']} | 📍 **Location:** {item['location']}")
            if item.get("pre_order"):
                st.warning(f"⏳ Pre-Order (Expected Harvest: {item['harvest_date']})")
                
        with col_pay:
            raw_price = item['price_ngn']
            platform_fee = raw_price * 0.10  # 10% Platform Revenue
            total_price = raw_price + platform_fee
            
            st.markdown(f"**Item Price:** ₦{raw_price:,.2f}")
            st.markdown(f"<span style='color:#D90429;'>+ 10% Escrow Fee: ₦{platform_fee:,.2f}</span>", unsafe_allow_javascript=True)
            st.markdown(f"### **Total: ₦{total_price:,.2f}**")
            
            if st.button(f"Pay with Paystack 💳", key=f"pay_{item['id']}"):
                st.markdown("""
                <div class="escrow-box">
                    <strong>🔒 Paystack Escrow Activated:</strong><br>
                    Funds held safely until produce is inspected on delivery. 
                    <i>(Paystack API integration placeholder)</i>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# MODULE B: FARMER LISTING PORTAL
# --------------------------------------------------
elif navigation == "➕ List Produce / Livestock (Farmers)":
    st.subheader("🚜 Farmer Dashboard: List Your Products Direct")
    
    with st.form("new_listing_form"):
        prod_type = st.selectbox("Product Category", ["Crop Produce", "Livestock"])
        title = st.text_input("Product Title (e.g., Red Sokoto Goats, Cassava Tuber)")
        
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Selling Price (₦)", min_value=1000, value=50000, step=1000)
            location = st.text_input("Farm Location / State", value="Ogun State, Nigeria")
        with c2:
            if prod_type == "Livestock":
                weight = st.number_input("Estimated Weight per Animal (kg)", value=50)
            else:
                quantity = st.number_input("Available Bags/Tons", value=10)
                
        pre_order_check = st.checkbox("List as Pre-Harvest Forward Contract (Pre-Sell)")
        harvest_date = st.date_input("Expected Harvest/Supply Date", datetime.date.today()) if pre_order_check else None
        
        st.markdown("#### 📹 Digital Trust & Health Audit")
        uploaded_file = st.file_uploader("Upload Inspection Video / Photo (Helps buyers bypass physical visits)")
        
        submitted = st.form_submit_button("Publish Direct Listing")
        
        if submitted:
            new_id = f"FTN-{random.randint(200, 999)}"
            new_item = {
                "id": new_id,
                "seller": st.session_state.username,
                "category": prod_type,
                "item": title,
                "location": location,
                "price_ngn": price,
                "verified_health": True,
                "pre_order": pre_order_check,
                "harvest_date": str(harvest_date) if harvest_date else None
            }
            if prod_type == "Livestock":
                new_item["weight_kg"] = weight
            else:
                new_item["quantity"] = quantity
                
            st.session_state.listings.append(new_item)
            st.success("🎉 Product successfully published directly to all buyers nationwide!")

# --------------------------------------------------
# MODULE C: REVENUE & FEE TRANSPARENCY (YOUR 10% COMMISSION)
# --------------------------------------------------
elif navigation == "📈 Revenue & Fee Calculator":
    st.subheader("💰 Feed The Nations Economics (Your 10% Moat)")
    
    st.write("This tool calculates the automated **10% platform commission** applied to direct transactions.")
    
    gmv = st.number_input("Simulate Gross Merchandise Value (Total Farm Sales in ₦)", value=5000000, step=500000)
    
    comm = gmv * 0.10
    farmer_payout = gmv
    buyer_cost = gmv + comm
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Buyer Payment", f"₦{buyer_cost:,.2f}")
    c2.metric("Farmer Payout (100% Intact)", f"₦{farmer_payout:,.2f}")
    c3.metric("FEED THE NATIONS Revenue (10%)", f"₦{comm:,.2f}", delta="Platform Profit")
    
    st.info("💡 **Why Buyers Accept This:** Traditional middlemen mark up produce prices by **30% - 60%**. A 10% fee for guaranteed logistics and escrow still saves buyers money!")

# --------------------------------------------------
# MODULE D: PRE-ORDER FORWARD CONTRACTS
# --------------------------------------------------
elif navigation == "🤝 Pre-Order Forward Contracts":
    st.subheader("📅 Future Harvest & Supply Contracts")
    st.write("Pre-buy harvests or livestock rearing batches before market day. Protects buyers against inflation and guarantees sales for farmers.")
    
    pre_orders = [item for item in st.session_state.listings if item.get("pre_order")]
    
    if pre_orders:
        for po in pre_orders:
            st.warning(f"🌾 **Contract:** {po['item']} | **Harvest Target:** {po['harvest_date']}")
            st.write(f"Farmer: {po['seller']} | Base Price: ₦{po['price_ngn']:,.2f}")
            st.button("Lock-in Contract via Escrow", key=f"contract_{po['id']}")
    else:
        st.write("No active forward contracts currently open.")
