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

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary-green: #008751;   /* Agriculture Green */
        --accent-red: #D90429;      /* Escrow / Alerts */
        --earth-brown: #5C3D2E;     /* Soil / Earth */
        --light-bg: #F4F7F4;        /* Soft White */
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

    /* Custom Brand Header */
    .brand-header {
        background: linear-gradient(135deg, #008751 0%, #2A7B4C 50%, #5C3D2E 100%);
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .brand-subtext {
        color: #F4F7F4;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 8px;
    }

    .brand-icons {
        font-size: 1.8rem;
        margin-top: 10px;
        word-spacing: 15px;
    }

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

    .escrow-box {
        background-color: #FFF3F3;
        border-left: 5px solid var(--accent-red);
        padding: 12px;
        border-radius: 6px;
        margin-top: 10px;
    }

    .listing-card {
        background-color: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid var(--earth-brown);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT & DB SIMULATION
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # "Farmer", "Buyer", or "Admin"
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_db" not in st.session_state:
    # Simulated Supabase User Table mapping email -> {password, role, name}
    st.session_state.user_db = {
        "farmer@ftn.com": {"password": "password123", "role": "Farmer", "name": "Musa Adamu"},
        "buyer@ftn.com": {"password": "password123", "role": "Buyer", "name": "Bisi Akande (Hotels)"},
        "admin@ftn.com": {"password": "adminsecret", "role": "Admin", "name": "Founder / Admin"}
    }

if "listings" not in st.session_state:
    st.session_state.listings = [
        {
            "id": "FTN-101",
            "seller": "Musa Adamu",
            "category": "Livestock",
            "item": "Boran Cattle (Bull)",
            "weight_kg": 420,
            "location": "Kano, Nigeria",
            "price_ngn": 650000,
            "verified_health": True,
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
            "seller": "Musa Adamu",
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
# 3. HEADER BANNER (NO NG FLAG + AGRI ICONS)
# ==========================================
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <div class="brand-icons">🌾 🌽 🐂 🌾 🌽 🐂</div>
    <p class="brand-subtext">
        Direct Farm-to-Buyer Marketplace • Zero Middlemen • Escrow Protection
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. SECURE AUTHENTICATION / LOGIN PORTAL
# ==========================================
def render_login_portal():
    st.subheader("🔑 Access Portal")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        auth_mode = st.radio("Choose Action", ["Login", "Register Account"], horizontal=True)
        
        email = st.text_input("Email Address").strip().lower()
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Register Account":
            selected_role = st.selectbox("Account Type", ["Buyer (Wholesaler, Hotel, Processor)", "Farmer / Livestock Producer"])
            full_name = st.text_input("Full Name / Farm Name")
            phone = st.text_input("Phone Number")
            
            if st.button("Create Account", use_container_width=True):
                if email and password and full_name:
                    if email in st.session_state.user_db:
                        st.error("Account already exists with this email! Please log in.")
                    else:
                        assigned_role = "Farmer" if "Farmer" in selected_role else "Buyer"
                        # Supabase Integration Point: supabase.auth.sign_up(...)
                        st.session_state.user_db[email] = {
                            "password": password,
                            "role": assigned_role,
                            "name": full_name
                        }
                        st.success(f"Account created successfully as {assigned_role}! Please log in.")
                else:
                    st.error("Please fill out all required registration fields.")
                    
        else:  # Login Flow
            if st.button("Log In", use_container_width=True):
                if email in st.session_state.user_db and st.session_state.user_db[email]["password"] == password:
                    user_data = st.session_state.user_db[email]
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_data["role"]
                    st.session_state.username = user_data["name"]
                    st.success(f"Welcome back, {user_data['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
        st.divider()
        st.caption("💡 **Demo Credentials:**")
        st.caption("• **Farmer:** `farmer@ftn.com` | Password: `password123`")
        st.caption("• **Buyer:** `buyer@ftn.com` | Password: `password123`")
        st.caption("• **Founder/Admin:** `admin@ftn.com` | Password: `adminsecret`")

    with col2:
        st.info("### Platform Value Proposition")
        st.markdown("""
        * 🛡️ **Escrow Protection:** Payment stays locked safely in escrow until quality is verified on arrival.
        * 🐂 **Livestock Health Proof:** Certified video & veterinary inspections before purchase.
        * 🌾 **Direct Farm Prices:** Eliminates market middleman markups.
        * 🤝 **Forward Contracting:** Reserve future harvests ahead of time.
        """)

if not st.session_state.authenticated:
    render_login_portal()
    st.stop()

# ==========================================
# 5. ROLE-BASED NAVIGATION & DASHBOARD
# ==========================================

st.sidebar.markdown(f"### 👤 {st.session_state.username}")
st.sidebar.markdown(f"**Account Role:** `{st.session_state.user_role}`")

if st.sidebar.button("Log Out"):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.rerun()

st.sidebar.divider()

# Role-Based Menu Options
if st.session_state.user_role == "Farmer":
    nav_options = ["➕ My Produce & Listings", "➕ Add New Product", "🤝 Direct Buyer Requests"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "🤝 Pre-Order Forward Contracts", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["🛒 Browse Marketplace", "📈 Founder Revenue & Fee Analytics", "➕ Add New Product"]

navigation = st.sidebar.radio("Navigation", nav_options)

# --------------------------------------------------
# BUYER VIEW: MARKETPLACE
# --------------------------------------------------
if navigation in ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]:
    st.subheader("🌾 Direct Farm Produce & Livestock Market")
    
    category_filter = st.selectbox("Filter Category", ["All", "Livestock", "Crop Produce"])
    
    for item in st.session_state.listings:
        if category_filter != "All" and item["category"] != category_filter:
            continue
            
        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        col_img, col_info, col_pay = st.columns([1, 2, 1.5])
        
        with col_img:
            if item["category"] == "Livestock":
                st.markdown("### 🐂 Livestock")
                st.caption(f"Estimated Wt: **{item.get('weight_kg', 'N/A')} kg**")
            else:
                st.markdown("### 🌽 Crop Produce")
                st.caption(f"Quantity: **{item.get('quantity', 'N/A')} Units**")
            
            if item.get("verified_health"):
                st.success("✅ Vet Checked")

        with col_info:
            st.markdown(f"### {item['item']}")
            st.write(f"**Seller:** {item['seller']} | 📍 **Location:** {item['location']}")
            if item.get("pre_order"):
                st.warning(f"⏳ Pre-Order (Expected Harvest: {item['harvest_date']})")
                
        with col_pay:
            raw_price = item['price_ngn']
            platform_fee = raw_price * 0.10  # 10% Platform Fee
            total_price = raw_price + platform_fee
            
            st.markdown(f"**Farm Price:** ₦{raw_price:,.2f}")
            st.markdown(f"<span style='color:#D90429; font-weight:bold;'>+ 10% Escrow & Delivery Fee: ₦{platform_fee:,.2f}</span>", unsafe_allow_html=True)
            st.markdown(f"### **Total: ₦{total_price:,.2f}**")
            
            if st.button("Pay with Paystack 💳", key=f"pay_{item['id']}"):
                st.markdown("""
                <div class="escrow-box">
                    <strong>🔒 Paystack Escrow Activated:</strong><br>
                    Payment locked safely. Funds are released to the farmer only upon physical delivery confirmation.
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# FARMER VIEW: LISTINGS MANAGEMENT
# --------------------------------------------------
elif navigation == "➕ My Produce & Listings":
    st.subheader("🚜 Farmer Dashboard: Active Inventory")
    
    my_items = [i for i in st.session_state.listings if i["seller"] == st.session_state.username]
    
    if my_items:
        for item in my_items:
            st.markdown(f"• **{item['item']}** | Price: ₦{item['price_ngn']:,.2f} | Location: {item['location']}")
    else:
        st.info("You haven't posted any produce listings yet. Click 'Add New Product' in the sidebar to publish your first item!")

elif navigation == "➕ Add New Product":
    st.subheader("🚜 Publish Direct Listing")
    
    with st.form("new_listing_form"):
        prod_type = st.selectbox("Product Category", ["Crop Produce", "Livestock"])
        title = st.text_input("Product Title (e.g., Sokoto Red Goats, Yellow Maize)")
        
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Base Farm Price (₦)", min_value=1000, value=50000, step=1000)
            location = st.text_input("Farm Location", value="Ogun State")
        with c2:
            if prod_type == "Livestock":
                weight = st.number_input("Estimated Weight (kg)", value=50)
            else:
                quantity = st.number_input("Available Units/Bags", value=10)
                
        pre_order_check = st.checkbox("List as Pre-Harvest Contract")
        harvest_date = st.date_input("Expected Harvest Date", datetime.date.today()) if pre_order_check else None
        
        st.markdown("#### 📹 Digital Health Audit")
        uploaded_file = st.file_uploader("Upload Inspection Photo / Video")
        
        submitted = st.form_submit_button("Publish Product")
        
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
            st.success("🎉 Listing successfully published!")

# --------------------------------------------------
# BUYER VIEW: PRE-ORDER CONTRACTS
# --------------------------------------------------
elif navigation == "🤝 Pre-Order Forward Contracts":
    st.subheader("📅 Future Harvest Contracts")
    st.write("Reserve crop yields or livestock batches prior to harvest to guarantee prices.")
    
    pre_orders = [item for item in st.session_state.listings if item.get("pre_order")]
    
    if pre_orders:
        for po in pre_orders:
            st.warning(f"🌾 **Contract:** {po['item']} | **Expected Harvest:** {po['harvest_date']}")
            st.write(f"Farmer: {po['seller']} | Price: ₦{po['price_ngn']:,.2f}")
            st.button("Lock Contract via Escrow", key=f"contract_{po['id']}")
    else:
        st.info("No forward contracts are currently available.")

# --------------------------------------------------
# FOUNDER / ADMIN VIEW: REVENUE CALCULATOR
# --------------------------------------------------
elif navigation == "📈 Founder Revenue & Fee Analytics":
    st.subheader("💰 Platform Commission & Financial Analytics")
    st.caption("🔒 Private View — Visible only to Admin/Founder accounts.")
    
    gmv = st.number_input("Simulate Gross Merchandise Value (₦)", value=10000000, step=1000000)
    
    comm = gmv * 0.10
    farmer_payout = gmv
    buyer_cost = gmv + comm
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Buyer Payments", f"₦{buyer_cost:,.2f}")
    c2.metric("Net Farmer Payout", f"₦{farmer_payout:,.2f}")
    c3.metric("10% Platform Revenue", f"₦{comm:,.2f}", delta="Net Revenue")
