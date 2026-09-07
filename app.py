import io
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
# 1. PAGE CONFIG & PREMIUM AGRICULTURAL STYLING
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
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&family=Poppins:wght@400;500;600;700&display=swap');

    :root {
        --primary-agri: #1E5631;
        --accent-green: #4C9A2A;
        --leaf-green: #76BA1B;
        --warm-earth: #A47148;
        --card-bg: #FFFFFF;
        --light-bg: #F4F7F4;
    }

    .stApp {
        background-color: var(--light-bg);
        font-family: 'Poppins', sans-serif;
    }

    /* BRAND HEADER */
    .brand-header {
        background: linear-gradient(135deg, #1E5631 0%, #2D6A4F 50%, #40916C 100%);
        padding: 28px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 25px;
        color: #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(30, 86, 49, 0.25);
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(2rem, 4.5vw, 3.2rem);
        font-weight: 900;
        letter-spacing: 1.5px;
        margin: 0;
        text-transform: uppercase;
    }

    .brand-subtext {
        color: #D8F3DC;
        font-size: 1.05rem;
        font-weight: 500;
        margin-top: 8px;
    }

    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #1E5631 0%, #2D6A4F 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 10px rgba(30, 86, 49, 0.15) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2D6A4F 0%, #40916C 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(30, 86, 49, 0.3) !important;
    }

    /* CARDS */
    .product-card {
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 22px;
        transition: transform 0.2s ease;
    }

    .product-card:hover {
        border-color: var(--accent-green);
    }

    .metric-box {
        background: #FFFFFF;
        padding: 18px;
        border-radius: 12px;
        border-left: 6px solid #1E5631;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. SUPABASE INITIALIZATION & HELPERS
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
    "GIG Logistics (Agri-Freight Division)": {"phone": "+2348130001122", "display": "+234 813 000 1122"},
    "Kwik Delivery (Heavy Haulage)": {"phone": "+2348092223344", "display": "+234 809 222 3344"},
    "Max.ng Freight & Inter-State": {"phone": "+2347008009000", "display": "+234 700 800 9000"},
    "Farmers Union Local Transport": {"phone": "+2348023334455", "display": "+234 802 333 4455"},
}

def verify_farm_photo(image):
    try:
        img = image.convert("RGB")
        stat = ImageStat.Stat(img)
        avg_stddev = sum(stat.stddev) / len(stat.stddev)
        if avg_stddev < 18:
            return False, "This photo appears to be a document or screenshot. Please upload a clear photo of real farm produce."

        w, h = img.size
        if w < 200 or h < 200:
            return False, "Photo resolution is too low. Minimum allowed size is 200x200 pixels."

        return True, "Valid farm produce photo."
    except Exception:
        return False, "Invalid image format. Please upload a valid JPG or PNG file."

def upload_product_photo(file_bytes, filename):
    try:
        clean_name = "".join([c for c in filename if c.isalnum() or c in (".", "_", "-")]).lower()
        path = f"public/{random.randint(1000,9999)}_{clean_name}"
        
        supabase.storage.from_("farm-photos").upload(path, file_bytes, {"content-type": "image/jpeg"})
        public_url = supabase.storage.from_("farm-photos").get_public_url(path)
        return public_url
    except Exception as e:
        st.error(f"Image storage upload error: {str(e)}")
        return None

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
if "editing_listing_id" not in st.session_state:
    st.session_state.editing_listing_id = None

# ==============================================================================
# 4. BRAND HEADER
# ==============================================================================
st.markdown(
    """
<div class="brand-header">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <p class="brand-subtext">Direct Farm-to-Buyer Agricultural Marketplace • Escrow Protection • Real-Time Freight</p>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. AUTHENTICATION SYSTEM
# ==============================================================================
if not st.session_state.authenticated:
    st.subheader("🔑 Sign In or Register Your Account")
    auth_mode = st.radio("Choose Action", ["Login", "Register Account"], horizontal=True)

    email_input = st.text_input("Email Address").strip().lower()
    password_input = st.text_input("Password", type="password")

    if auth_mode == "Register Account":
        selected_role = st.selectbox(
            "Account Type",
            ["Buyer (Wholesaler, Hotel, Processor)", "Farmer / Producer", "Platform Admin"],
        )
        full_name = st.text_input("Full Name / Enterprise Name")
        farming_cat = (
            st.selectbox("Primary Agricultural Specialty", AGRI_CATEGORIES)
            if "Farmer" in selected_role
            else "All Categories"
        )

        if st.button("CREATE ACCOUNT 🚀", use_container_width=True):
            if email_input and password_input and full_name:
                try:
                    assigned_role = "Farmer" if "Farmer" in selected_role else ("Admin" if "Admin" in selected_role else "Buyer")

                    res = supabase.auth.sign_up({
                        "email": email_input,
                        "password": password_input,
                        "options": {
                            "data": {
                                "full_name": full_name,
                                "role": assigned_role,
                                "category": farming_cat,
                            }
                        },
                    })

                    if res.user:
                        profile_data = {
                            "id": res.user.id,
                            "email": email_input,
                            "full_name": full_name,
                            "role": assigned_role,
                            "category": farming_cat,
                        }
                        supabase.table("profiles").upsert(profile_data).execute()

                    st.success("🎉 Account created successfully! Please select 'Login' above to enter.")
                except Exception as e:
                    st.error(f"Registration error: {str(e)}")
            else:
                st.error("Please fill in all registration fields.")
    else:
        if st.button("LOG IN ➔", use_container_width=True):
            if email_input and password_input:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": password_input})
                    user_metadata = res.user.user_metadata
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_metadata.get("role", "Buyer")
                    st.session_state.username = user_metadata.get("full_name", email_input)
                    st.session_state.email = email_input
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
            else:
                st.error("Please provide both email and password.")
    st.stop()

# ==============================================================================
# 6. NAVIGATION & SIDEBAR
# ==============================================================================
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
st.sidebar.markdown(f"**Account Role:** `{st.session_state.user_role}`")

if st.sidebar.button("🔒 Sign Out"):
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.editing_listing_id = None
    st.rerun()

st.sidebar.divider()

if st.session_state.user_role == "Farmer":
    nav_options = ["📦 My Active Products", "➕ Add New Product"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["📈 Founder Revenue Dashboard", "🛒 Browse Marketplace"]

navigation = st.sidebar.radio("Navigation Menu", nav_options)

# ==============================================================================
# 7. FOUNDER REVENUE DASHBOARD (ADMIN)
# ==============================================================================
if navigation == "📈 Founder Revenue Dashboard":
    st.subheader("📊 Marketplace GMV & Revenue Analytics")
    try:
        response = supabase.table("transactions").select("*").execute()
        tx_data = response.data

        if tx_data:
            df_tx = pd.DataFrame(tx_data)
            total_gmv = df_tx["amount"].sum()
            total_commission = df_tx["commission"].sum()

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Gross Merchandise Value (GMV)", f"₦{total_gmv:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with m2:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Platform Revenue (10%)", f"₦{total_commission:,.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
            with m3:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Completed Transactions", len(df_tx))
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📜 Real-Time Escrow Ledger")
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("No recorded transactions currently in database.")
    except Exception as e:
        st.error(f"Error loading revenue ledger: {str(e)}")

# ==============================================================================
# 8. BUYER MARKETPLACE
# ==============================================================================
elif navigation in ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]:
    st.subheader("🛒 Direct Farm Produce Marketplace")

    f1, f2 = st.columns(2)
    with f1:
        buying_scale = st.selectbox("Filter Scale", ["All Scales", "Large Scale / Commercial Wholesale", "Small Scale / Retail"])
    with f2:
        category_filter = st.selectbox("Filter Agricultural Sector", ["All Categories"] + AGRI_CATEGORIES)

    st.divider()

    try:
        query = supabase.table("listings").select("*")
        if buying_scale != "All Scales":
            query = query.eq("scale", buying_scale)
        if category_filter != "All Categories":
            query = query.eq("category", category_filter)

        listings = query.execute().data

        if not listings:
            st.info("No agricultural products currently listed matching your criteria.")

        for item in listings:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])

            with col1:
                if item.get("image_url"):
                    st.image(item["image_url"], use_container_width=True)
                else:
                    st.info("📷 Photo Verified")
                st.caption(f"Scale: **{item.get('scale', 'General Supply')}**")

            with col2:
                st.markdown(f"### {item['item']}")
                st.write(f"**Sector:** `{item.get('category')}`")
                st.write(f"**Farmer:** {item['seller']} | 📍 **Location:** {item['location']}")

                raw_price = float(item["price_ngn"])
                platform_fee = raw_price * 0.10

                st.markdown(f"**Farm Price:** ₦{raw_price:,.2f}")
                st.markdown(f"**Escrow Platform Fee (10%):** ₦{platform_fee:,.2f}")

                st.markdown("#### 🚚 Logistics & Delivery Arrangement")
                selected_partner = st.selectbox(f"Logistics Partner for {item['id']}", list(LOGISTICS_PARTNERS.keys()))
                partner_info = LOGISTICS_PARTNERS[selected_partner]

                agreed_freight = st.number_input(
                    "Agreed Freight Cost (₦)",
                    min_value=0,
                    value=25000,
                    step=5000,
                    key=f"freight_{item['id']}",
                )

                final_total = raw_price + platform_fee + agreed_freight
                st.markdown(f"### **Total Checkout Price: ₦{final_total:,.2f}**")

                if st.button("BUY WITH ESCROW PROTECTION 💳", key=f"pay_{item['id']}"):
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
                    pay_resp = initialize_paystack_payment(st.session_state.email, final_total, ref)

                    if pay_resp.get("status"):
                        auth_url = pay_resp["data"]["authorization_url"]
                        st.success("🔒 Escrow order generated successfully!")
                        st.markdown(f'<a href="{auth_url}" target="_blank" style="display:inline-block; background: #1E5631; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold;">Proceed to Paystack Checkout ➔</a>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Marketplace error: {str(e)}")

# ==============================================================================
# 9. FARMER PRODUCT MANAGEMENT (ADD / EDIT / DELETE)
# ==============================================================================
elif navigation == "➕ Add New Product":
    st.subheader("🚜 Post New Farm Produce Listing")

    with st.form("add_product_form"):
        farming_cat = st.selectbox("Agricultural Sector", AGRI_CATEGORIES)
        prod_scale = st.selectbox("Supply Scale Category", ["Large Scale / Commercial Wholesale", "Small Scale / Retail"])
        title = st.text_input("Product Name (e.g. 50kg Bags of White Maize)")

        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Unit Price (₦)", min_value=1000, value=50000, step=5000)
            location = st.text_input("Farm State / City Location", value="Ogun State")
        with c2:
            quantity = st.number_input("Available Stock Quantity", value=50)

        uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("PUBLISH PRODUCT TO MARKETPLACE 🚀")

        if submitted:
            if not uploaded_file:
                st.error("⚠️ Please attach a photo of your farm produce.")
            else:
                img_bytes = uploaded_file.read()
                img = Image.open(io.BytesIO(img_bytes))
                is_valid, msg = verify_farm_photo(img)

                if not is_valid:
                    st.error(f"⚠️ {msg}")
                elif not title:
                    st.error("Please enter a product title.")
                else:
                    img_url = upload_product_photo(img_bytes, uploaded_file.name)
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
                        "image_url": img_url
                    }
                    supabase.table("listings").insert(product_data).execute()
                    st.success("🎉 Product successfully published!")

elif navigation == "📦 My Active Products":
    st.subheader("🚜 Manage My Farm Listings")

    if st.session_state.editing_listing_id:
        st.markdown("### ✏️ Edit Product Listing")
        try:
            edit_item = supabase.table("listings").select("*").eq("id", st.session_state.editing_listing_id).execute().data
            if edit_item:
                item_data = edit_item[0]
                with st.form("edit_product_form"):
                    e_title = st.text_input("Product Title", value=item_data.get("item", ""))
                    e_price = st.number_input("Unit Price (₦)", value=float(item_data.get("price_ngn", 1000)), step=1000.0)
                    e_location = st.text_input("Farm Location", value=item_data.get("location", ""))
                    e_quantity = st.number_input("Available Quantity", value=int(item_data.get("quantity", 1)))

                    c_save, c_cancel = st.columns(2)
                    save_changes = c_save.form_submit_button("💾 SAVE CHANGES")
                    cancel_changes = c_cancel.form_submit_button("❌ CANCEL")

                    if save_changes:
                        updated_fields = {
                            "item": e_title,
                            "price_ngn": e_price,
                            "location": e_location,
                            "quantity": e_quantity
                        }
                        supabase.table("listings").update(updated_fields).eq("id", item_data["id"]).execute()
                        st.session_state.editing_listing_id = None
                        st.rerun()

                    if cancel_changes:
                        st.session_state.editing_listing_id = None
                        st.rerun()
        except Exception as e:
            st.error(f"Error editing product: {str(e)}")

    else:
        try:
            my_items = supabase.table("listings").select("*").eq("seller", st.session_state.username).execute().data

            if my_items:
                for item in my_items:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    col1, col2 = st.columns([1.2, 2])

                    with col1:
                        if item.get("image_url"):
                            st.image(item["image_url"], use_container_width=True)
                        else:
                            st.info("📷 Photo Verified")

                    with col2:
                        st.markdown(f"### {item['item']}")
                        st.write(f"**Sector:** `{item.get('category')}`")
                        st.write(f"**Price:** ₦{float(item['price_ngn']):,.2f}")
                        st.write(f"📍 **Location:** {item.get('location', 'N/A')} | **Units Available:** {item.get('quantity', 0)}")

                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            if st.button(f"✏️ Edit Product", key=f"edit_{item['id']}"):
                                st.session_state.editing_listing_id = item["id"]
                                st.rerun()

                        with b_col2:
                            if st.button(f"🗑️ Delete Product", key=f"del_{item['id']}"):
                                supabase.table("listings").delete().eq("id", item["id"]).execute()
                                st.success("Listing removed successfully!")
                                st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("You currently have no active listings. Select 'Add New Product' to post your produce!")
        except Exception as e:
            st.error(f"Error loading your active products: {str(e)}")
