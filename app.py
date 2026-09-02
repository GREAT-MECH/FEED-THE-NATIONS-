import streamlit as st
import pandas as pd
import datetime
import random
from PIL import Image

# ==========================================
# 1. PAGE CONFIG & ANIMATED CSS THEMING
# ==========================================
st.set_page_config(
    page_title="FEED THE NATIONS - Direct Agri Marketplace",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Animated White Light Sweeping Effect
st.markdown("""
<style>
    :root {
        --primary-green: #008751;   /* Agriculture Green */
        --accent-red: #D90429;      /* Escrow / Alerts */
        --earth-brown: #5C3D2E;     /* Soil / Earth */
        --light-bg: #F4F7F4;        /* Soft White / Light Grey */
        --dark-text: #1B2021;
    }

    /* Soft Light Background */
    .stApp {
        background-color: var(--light-bg);
        color: var(--dark-text);
    }

    h1, h2, h3 {
        color: var(--primary-green) !important;
        font-weight: 700;
    }

    /* ANIMATED HEADER WITH SWEEPING WHITE LIGHT BEAM */
    @keyframes sweepLight {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
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
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.4);
    }

    .brand-subtext {
        color: #F4F7F4;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 8px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }

    .brand-icons {
        font-size: 2rem;
        margin-top: 8px;
        word-spacing: 15px;
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

    .escrow-box {
        background-color: #FFF3F3;
        border-left: 5px solid var(--accent-red);
        padding: 12px;
        border-radius: 6px;
        margin-top: 10px;
    }

    .listing-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        border-top: 5px solid var(--earth-brown);
        margin-bottom: 25px;
    }
    
    .price-breakdown {
        background-color: #F9FBF9;
        border: 1px solid #E0E7E0;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
    }
    
    .scale-badge {
        background-color: #E2F0D9;
        color: #385723;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 8px;
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
            "weight_kg": 420,
            "location": "Kano State",
            "price_ngn": 6500000,
            "image_obj": None,
            "verified_health": True,
            "pre_order": False
        },
        {
            "id": "FTN-102",
            "seller": "Green Harvest Co-op",
            "category": "🌾 Crop Farming",
            "item": "Organic Yellow Maize (Bulk 500 Bags)",
            "scale": "Large Scale / Commercial Wholesale",
            "quantity": 500,
            "location": "Benue State",
            "price_ngn": 16000000,
            "image_obj": None,
            "verified_health": True,
            "pre_order": False
        },
        {
            "id": "FTN-103",
            "seller": "Smallholder Poultry Hub",
            "category": "🐓 Poultry Farming",
            "item": "Fresh Farm Eggs (20 Crate Batch)",
            "scale": "Small Scale / Retail",
            "quantity": 20,
            "location": "Oyo State",
            "price_ngn": 70000,
            "image_obj": None,
            "verified_health": True,
            "pre_order": False
        }
    ]

# Third-party logistics partners catalog
LOGISTICS_PARTNERS = {
    "GIG Logistics (Agri-Freight Division)": {"contact": "+234 813 000 1122", "est_rate": 15000},
    "Kwik Delivery (Heavy Haulage Trucks)": {"contact": "+234 809 222 3344", "est_rate": 20000},
    "Max.ng Freight & Inter-State Transit": {"contact": "+234 700 800 9000", "est_rate": 18000},
    "Local Community Farmers Union Transport": {"contact": "+234 802 333 4455", "est_rate": 8000}
}

# ==========================================
# 3. ANIMATED HEADER BANNER
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
    
    col_center, _ = st.columns([2, 1])
    
    with col_center:
        auth_mode = st.radio("Choose Action", ["Login", "Register Account"], horizontal=True)
        
        email = st.text_input("Email Address").strip().lower()
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Register Account":
            selected_role = st.selectbox("Account Type", ["Buyer (Wholesaler, Hotel, Processor)", "Farmer / Producer"])
            full_name = st.text_input("Full Name / Farm Name")
            
            farming_cat = None
            if "Farmer" in selected_role:
                farming_cat = st.selectbox("Select Your Farming Category", [
                    "🌾 Crop Farming",
                    "🐂 Livestock Farming",
                    "🐓 Poultry Farming",
                    "🐟 Fishery / Aquaculture",
                    "🍎 Horticulture (Fruits & Vegetables)",
                    "🥛 Dairy Farming"
                ])
                
            phone = st.text_input("Phone Number")
            
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

if st.session_state.user_role == "Farmer":
    nav_options = ["➕ My Active Products & Media", "➕ Add New Product", "🤝 Direct Buyer Requests"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "🤝 Pre-Order Forward Contracts", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["🛒 Browse Marketplace", "📈 Founder Revenue & Fee Analytics", "➕ Add New Product"]

navigation = st.sidebar.radio("Navigation", nav_options)

# --------------------------------------------------
# BUYER VIEW: MARKETPLACE, SCALE FILTER & LOGISTICS
# --------------------------------------------------
if navigation in ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]:
    st.subheader("🛒 Direct Farm Produce & Livestock Market")
    
    # 1. NEW FILTERS: SCALE & AGRICULTURE CATEGORY INTEREST
    st.markdown("#### 🎯 Sourcing & Buying Filters")
    c_filter1, c_filter2, c_filter3, c_filter4 = st.columns([1.2, 1.2, 1, 1.2])
    
    with c_filter1:
        buying_scale = st.selectbox("Buying Scale", [
            "All Scales", 
            "Large Scale / Commercial Wholesale", 
            "Small Scale / Retail"
        ])
        
    with c_filter2:
        category_filter = st.selectbox("Agricultural Interest Category", [
            "All Agriculture Types", 
            "🌾 Crop Farming", 
            "🐂 Livestock Farming", 
            "🐓 Poultry Farming", 
            "🐟 Fishery / Aquaculture", 
            "🍎 Horticulture (Fruits & Vegetables)", 
            "🥛 Dairy Farming"
        ])
        
    with c_filter3:
        dest_state = st.text_input("Delivery State", value="Lagos State")
        
    with c_filter4:
        partner_choice = st.selectbox("Logistics Partner", list(LOGISTICS_PARTNERS.keys()))
        
    selected_logistics = LOGISTICS_PARTNERS[partner_choice]
    logistics_fee = selected_logistics["est_rate"]
    
    st.info(f"🚚 **Logistics Contact for {partner_choice}:** Call/WhatsApp `{selected_logistics['contact']}` to arrange haulage to **{dest_state}**.")
    st.divider()

    matching_items = 0
    for item in st.session_state.listings:
        # Scale Filter Check
        if buying_scale != "All Scales" and item.get("scale") != buying_scale:
            continue
            
        # Agriculture Category Check
        if category_filter != "All Agriculture Types" and category_filter.split(" ")[1] not in item.get("category", ""):
            continue

        matching_items += 1
        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        col_media, col_details, col_pricing = st.columns([1.2, 1.8, 1.5])
        
        with col_media:
            if item.get("image_obj"):
                st.image(item["image_obj"], use_container_width=True, caption=f"Uploaded Product Photo")
            else:
                st.info("📷 Photo Pending Verification")
                
            if item.get("scale"):
                st.markdown(f'<div class="scale-badge">📦 {item["scale"]}</div>', unsafe_allow_html=True)
                
            if item.get("verified_health"):
                st.success("✅ Quality Inspected")

        with col_details:
            st.markdown(f"### {item['item']}")
            st.markdown(f"**Category:** `{item.get('category', 'Agri Produce')}`")
            st.markdown(f"**Farmer / Supplier:** {item['seller']}")
            st.markdown(f"📍 **Origin Farm Location:** {item['location']}")
            
            if "weight_kg" in item:
                st.write(f"⚖️ **Estimated Weight:** {item['weight_kg']} kg")
            if "quantity" in item:
                st.write(f"📦 **Available Quantity:** {item['quantity']} Units / Bags")
                
            if item.get("pre_order"):
                st.warning(f"⏳ Pre-Order Contract (Expected Harvest: {item['harvest_date']})")

        with col_pricing:
            raw_price = item['price_ngn']
            platform_fee = raw_price * 0.10  # 10% Platform Fee
            total_price = raw_price + platform_fee + logistics_fee
            
            st.markdown('<div class="price-breakdown">', unsafe_allow_html=True)
            st.markdown(f"**Base Farm Price:** ₦{raw_price:,.2f}")
            st.markdown(f"<span style='color:#008751;'>+ 10% Platform Fee: ₦{platform_fee:,.2f}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='color:#5C3D2E;'>+ 🚚 {partner_choice} Fee: ₦{logistics_fee:,.2f}</span>", unsafe_allow_html=True)
            st.divider()
            st.markdown(f"### **Total Payable: ₦{total_price:,.2f}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Pay via Paystack Escrow 💳", key=f"pay_{item['id']}"):
                st.markdown("""
                <div class="escrow-box">
                    <strong>🔒 Escrow Active:</strong><br>
                    Payment is safely locked in escrow. Funds are released to the farmer and transport provider only after physical delivery confirmation in your state!
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)

    if matching_items == 0:
        st.warning(f"No listings found matching scale: **{buying_scale}** in category **{category_filter}**. Try adjusting your filter settings.")

# --------------------------------------------------
# FARMER VIEW: ACTIVE INVENTORY & UPLOAD
# --------------------------------------------------
elif navigation == "➕ My Active Products & Media":
    st.subheader("🚜 Farmer Dashboard: My Inventory & Uploaded Photos")
    
    my_items = [i for i in st.session_state.listings if i["seller"] == st.session_state.username]
    
    if my_items:
        for item in my_items:
            st.markdown('<div class="listing-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                if item.get("image_obj"):
                    st.image(item["image_obj"], width=220, caption="Uploaded Photo")
                else:
                    st.warning("No photo uploaded")
            with c2:
                st.markdown(f"### {item['item']}")
                st.write(f"Category: `{item.get('category', 'General')}` | Scale: `{item.get('scale', 'General')}`")
                st.write(f"Base Price: **₦{item['price_ngn']:,.2f}** | 📍 Location: {item['location']}")
                if item.get("pre_order"):
                    st.caption(f"Pre-Harvest Date: {item['harvest_date']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("You haven't posted any produce listings yet. Click 'Add New Product' in the sidebar to publish your first item!")

elif navigation == "➕ Add New Product":
    st.subheader("🚜 Publish Product Listing")
    
    with st.form("new_listing_form"):
        farming_cat = st.selectbox("Select Agriculture Category", [
            "🌾 Crop Farming",
            "🐂 Livestock Farming",
            "🐓 Poultry Farming",
            "🐟 Fishery / Aquaculture",
            "🍎 Horticulture (Fruits & Vegetables)",
            "🥛 Dairy Farming"
        ])
        
        prod_scale = st.selectbox("Supply Scale Category", [
            "Large Scale / Commercial Wholesale",
            "Small Scale / Retail"
        ])
        
        title = st.text_input("Product Title (e.g., Commercial Herd of Cattle, 500 Bags Yellow Maize)")
        
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Base Farm Price (₦)", min_value=1000, value=100000, step=5000)
            location = st.text_input("Farm Location / State", value="Ogun State")
        with c2:
            quantity = st.number_input("Available Units / Bags / Crates / Animals", value=50)
            if "Livestock" in farming_cat or "Poultry" in farming_cat or "Dairy" in farming_cat:
                weight = st.number_input("Estimated Weight per Unit (kg)", value=50)
                
        pre_order_check = st.checkbox("List as Pre-Harvest Contract")
        harvest_date = st.date_input("Expected Harvest Date", datetime.date.today()) if pre_order_check else None
        
        st.markdown("#### 📷 Upload Product Photo")
        uploaded_file = st.file_uploader("Upload actual photo of livestock/crop", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Publish Product Listing")
        
        if submitted:
            img = Image.open(uploaded_file) if uploaded_file else None
            
            new_id = f"FTN-{random.randint(200, 999)}"
            new_item = {
                "id": new_id,
                "seller": st.session_state.username,
                "category": farming_cat,
                "scale": prod_scale,
                "item": title,
                "location": location,
                "price_ngn": price,
                "quantity": quantity,
                "image_obj": img,
                "verified_health": True,
                "pre_order": pre_order_check,
                "harvest_date": str(harvest_date) if harvest_date else None
            }
            if "weight" in locals():
                new_item["weight_kg"] = weight
                
            st.session_state.listings.append(new_item)
            st.success("🎉 Product listing with scale criteria successfully published!")

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
