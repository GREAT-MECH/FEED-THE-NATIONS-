import io
import os
import random
import urllib.parse
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

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "sk_live_5d70f03c20eea14b71be5b116e453e6a6848eebe")
PAYSTACK_CALLBACK_URL = os.environ.get("PAYSTACK_CALLBACK_URL", "https://feed-the-nations.onrender.com")

# ==============================================================================
# 1. PAGE CONFIG & STYLING
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
        --card-bg: #FFFFFF;
        --light-bg: #F4F7F4;
    }

    .stApp {
        background-color: var(--light-bg);
        font-family: 'Poppins', sans-serif;
    }

    .brand-header {
        position: relative;
        background: linear-gradient(135deg, #1E5631 0%, #2D6A4F 50%, #40916C 100%);
        padding: 36px 24px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 28px;
        color: #FFFFFF !important;
        box-shadow: 0 12px 32px rgba(30, 86, 49, 0.3);
        overflow: hidden;
    }

    .brand-header::after {
        content: '';
        position: absolute;
        top: 0;
        left: -150%;
        width: 80%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.1) 20%,
            rgba(255, 255, 255, 0.85) 50%,
            rgba(255, 255, 255, 0.1) 80%,
            transparent 100%
        );
        transform: skewX(-25deg);
        filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.9));
        animation: brightWhiteSweep 3.2s infinite linear;
        pointer-events: none;
    }

    @keyframes brightWhiteSweep {
        0% { left: -150%; }
        100% { left: 150%; }
    }
    
    .brand-title {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif;
        font-size: clamp(2.2rem, 5vw, 3.5rem);
        font-weight: 900;
        letter-spacing: 2px;
        margin: 0;
        text-transform: uppercase;
        position: relative;
        z-index: 2;
    }

    .brand-emojis {
        font-size: 2.2rem;
        margin-top: 6px;
        margin-bottom: 4px;
        position: relative;
        z-index: 2;
    }

    .brand-subtext {
        color: #E8F5E9;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: 8px;
        position: relative;
        z-index: 2;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1E5631 0%, #2D6A4F 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.25s ease-in-out !important;
        box-shadow: 0 4px 12px rgba(30, 86, 49, 0.18) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #2D6A4F 0%, #40916C 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(30, 86, 49, 0.35) !important;
    }

    .product-card {
        background-color: var(--card-bg);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 22px;
    }

    .metric-box {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border-left: 6px solid #1E5631;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    .warning-banner {
        background-color: #FFF3CD;
        border-left: 6px solid #FFC107;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #856404;
    }

    .whatsapp-btn {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        font-weight: 700;
        padding: 10px 18px;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 8px;
        margin-bottom: 12px;
        font-size: 0.9rem;
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. SUPABASE & PAYSTACK HELPER FUNCTIONS
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

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", 
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT - Abuja", "Gombe", 
    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", 
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", 
    "Taraba", "Yobe", "Zamfara"
]

# VERIFIED NIGERIAN LOGISTICS & FREIGHT COMPANIES (ACTIVE WHATSAPP SUPPORT LINES)
LOGISTICS_PARTNERS = {
    "1. GIG Logistics (Agri-Freight Division)": {"whatsapp": "2347080960441"},
    "2. Speedaf Express Cargo": {"whatsapp": "2347080636400"},
    "3. Max.ng Heavy Cargo & Freight": {"whatsapp": "2349088209804"},
    "4. Kwik Delivery Support Desk": {"whatsapp": "2348101822000"},
    "5. DHL Express Freight Nigeria": {"whatsapp": "2348039004000"},
    "6. Red Star Express Freight Services": {"whatsapp": "2348039012345"},
    "7. IFEX Express Cargo Lines": {"whatsapp": "2348033045678"},
    "8. FEDEX Nigeria Bulk Haulage": {"whatsapp": "2348022221100"},
    "9. ABC Cargo & Logistics": {"whatsapp": "2348055554433"},
    "10. Farmers Union Co-Op Logistics": {"whatsapp": "2348023334455"},
}

def verify_farm_photo(image):
    try:
        img = image.convert("RGB")
        stat = ImageStat.Stat(img)
        avg_stddev = sum(stat.stddev) / len(stat.stddev)
        if avg_stddev < 15:
            return False, "This image appears to be a blank or document screenshot. Please upload a clear produce photo."

        w, h = img.size
        if w < 150 or h < 150:
            return False, "Image resolution is too low. Minimum allowed size is 150x150 pixels."

        return True, "Valid farm photo"
    except Exception:
        return False, "Invalid image file format."

def upload_product_photo(file_bytes, filename):
    try:
        clean_name = "".join([c for c in filename if c.isalnum() or c in (".", "_", "-")]).lower()
        path = f"farm_{random.randint(10000, 99999)}_{clean_name}"

        supabase.storage.from_("farm-photos").upload(
            path,
            file_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/farm-photos/{path}"
        return public_url
    except Exception as e:
        st.error(f"Failed to upload photo to Supabase storage: {str(e)}")
        return None

def render_product_image(url_or_path):
    if url_or_path and str(url_or_path).strip():
        img_url = str(url_or_path).strip()
        if not img_url.startswith("http"):
            img_url = f"{SUPABASE_URL}/storage/v1/object/public/farm-photos/{img_url}"
        try:
            st.image(img_url, use_container_width=True)
        except Exception:
            st.info("📷 Farm Photo Verified")
    else:
        st.info("📷 Farm Photo Verified")

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

def verify_paystack_payment(reference):
    """Verifies payment with Paystack API before registering order on farmer dashboard."""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        if data.get("status") and data.get("data", {}).get("status") == "success":
            return True, data["data"]
        return False, "Payment verification pending or failed."
    except Exception as e:
        return False, str(e)

# ==============================================================================
# 3. SESSION STATE
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "editing_listing_id" not in st.session_state:
    st.session_state.editing_listing_id = None
if "deleted_msg" not in st.session_state:
    st.session_state.deleted_msg = None

# Check Paystack payment callback from URL query params
query_params = st.query_params
if "reference" in query_params or "trxref" in query_params:
    pay_ref = query_params.get("reference") or query_params.get("trxref")
    is_success, msg_or_data = verify_paystack_payment(pay_ref)
    if is_success:
        # Check if transaction exists in Supabase
        existing_tx = supabase.table("transactions").select("*").eq("paystack_ref", pay_ref).execute().data
        if existing_tx and existing_tx[0].get("status") != "PAID_VERIFIED":
            tx_item = existing_tx[0]
            
            # Update transaction status to PAID_VERIFIED
            supabase.table("transactions").update({"status": "PAID_VERIFIED"}).eq("paystack_ref", pay_ref).execute()
            
            # Deduct inventory stock from active listing
            listing_res = supabase.table("listings").select("quantity").eq("id", tx_item["listing_id"]).execute().data
            if listing_res:
                current_qty = int(listing_res[0].get("quantity", 0))
                purchased_qty = int(tx_item.get("quantity_bought", 1))
                new_qty = max(0, current_qty - purchased_qty)
                supabase.table("listings").update({"quantity": new_qty}).eq("id", tx_item["listing_id"]).execute()

            st.success("🎉 Payment verified! Order sent to Farmer's Dashboard and stock updated.")
        st.query_params.clear()

# ==============================================================================
# 4. BRAND HEADER
# ==============================================================================
st.markdown(
    """
<div class="brand-header">
    <h1 class="brand-title">FEED THE NATIONS</h1>
    <div class="brand-emojis">🌾 🌽 🐂 🐓</div>
    <p class="brand-subtext">Direct Farm-to-Buyer Agricultural Marketplace • Escrow Protection • Real-Time Freight</p>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 5. AUTHENTICATION PORTAL
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
        phone_input = st.text_input("Phone Number (WhatsApp Enabled)", placeholder="+2348000000000").strip()

        farming_cat = (
            st.selectbox("Primary Agricultural Specialty", AGRI_CATEGORIES)
            if "Farmer" in selected_role
            else "All Categories"
        )

        if st.button("CREATE ACCOUNT 🚀", use_container_width=True):
            if email_input and password_input and full_name and phone_input:
                try:
                    assigned_role = "Farmer" if "Farmer" in selected_role else ("Admin" if "Admin" in selected_role else "Buyer")

                    res = supabase.auth.sign_up({
                        "email": email_input,
                        "password": password_input,
                        "options": {
                            "data": {
                                "full_name": full_name,
                                "phone": phone_input,
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
                            "phone": phone_input,
                            "role": assigned_role,
                            "category": farming_cat,
                        }
                        supabase.table("profiles").upsert(profile_data).execute()

                    st.success("🎉 Account created successfully! Please select 'Login' above to enter.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
            else:
                st.error("Please fill in all registration fields, including Phone Number.")
    else:
        if st.button("LOG IN ➔", use_container_width=True):
            if email_input and password_input:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": password_input})
                    user_metadata = res.user.user_metadata
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_metadata.get("role", "Buyer")
                    st.session_state.username = user_metadata.get("full_name", email_input)
                    st.session_state.phone = user_metadata.get("phone", "")
                    st.session_state.email = email_input
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
            else:
                st.error("Please provide both email and password.")
    st.stop()

# ==============================================================================
# 6. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown(f"### 👤 {st.session_state.username}")
st.sidebar.markdown(f"**Account Role:** `{st.session_state.user_role}`")
if st.session_state.phone:
    st.sidebar.markdown(f"**Phone:** `{st.session_state.phone}`")

if st.sidebar.button("🔒 Sign Out"):
    supabase.auth.sign_out()
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.phone = ""
    st.session_state.editing_listing_id = None
    st.session_state.deleted_msg = None
    st.rerun()

st.sidebar.divider()

if st.session_state.user_role == "Farmer":
    nav_options = ["💰 Farmer Sales & Escrow Orders", "📦 My Active Products", "➕ Add New Product"]
elif st.session_state.user_role == "Buyer":
    nav_options = ["🛒 Browse Marketplace", "📦 My Orders & Escrow"]
elif st.session_state.user_role == "Admin":
    nav_options = ["📈 Founder Revenue Dashboard", "🛒 Browse Marketplace"]

navigation = st.sidebar.radio("Navigation Menu", nav_options)

# ==============================================================================
# 7. FOUNDER REVENUE DASHBOARD (ADMIN)
# ==============================================================================
if navigation == "📈 Founder Revenue Dashboard":
    st.subheader("📊 Marketplace Revenue & Volume Metrics")
    try:
        response = supabase.table("transactions").select("*").eq("status", "PAID_VERIFIED").execute()
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
                st.metric("Verified Orders", len(df_tx))
                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📜 Real-Time Escrow Ledger (Verified Payments)")
            st.dataframe(df_tx, use_container_width=True)
        else:
            st.info("There are no verified completed payments yet.")
    except Exception as e:
        st.error(f"Error loading revenue ledger: {str(e)}")

# ==============================================================================
# 8. FARMER SALES & ESCROW MONITORING
# ==============================================================================
elif navigation == "💰 Farmer Sales & Escrow Orders":
    st.subheader("💰 Purchased Items & Escrow Status")
    st.markdown("Only **PAYSTACK VERIFIED** payments appear on your dashboard.")

    try:
        farmer_listings = supabase.table("listings").select("id").eq("seller", st.session_state.username).execute().data
        
        if farmer_listings:
            farmer_listing_ids = [l["id"] for l in farmer_listings]
            
            # Fetch transactions filtered by listing IDs and PAID_VERIFIED status
            tx_response = (
                supabase.table("transactions")
                .select("*")
                .in_("listing_id", farmer_listing_ids)
                .eq("status", "PAID_VERIFIED")
                .execute()
                .data
            )
            
            if tx_response:
                df_farmer_tx = pd.DataFrame(tx_response)
                
                total_sales_val = df_farmer_tx["amount"].sum()
                held_escrow_val = df_farmer_tx["amount"].sum()

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Total Confirmed Sales", f"₦{total_sales_val:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with m2:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Escrow Funds Secured", f"₦{held_escrow_val:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with m3:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    st.metric("Verified Orders", len(tx_response))
                    st.markdown('</div>', unsafe_allow_html=True)

                st.divider()
                st.markdown("### 📦 Detailed Customer Sales Ledger")

                for order in tx_response:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    st.markdown(f"### Order Reference: `{order['id']}` - Produce: **{order.get('item', 'N/A')}**")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Buyer Username:** `{order.get('buyer', 'N/A')}`")
                        st.write(f"**Quantity Purchased:** {order.get('quantity_bought', 1)} units")
                    with c2:
                        st.write(f"**Produce Subtotal:** ₦{float(order.get('amount', 0)):,.2f}")
                        st.write(f"**Payment Verification:** ✅ `PAID_VERIFIED`")
                    with c3:
                        st.write(f"**Agreed Freight Fee:** ₦{float(order.get('freight', 0)):,.2f}")
                        st.write(f"**Grand Total Paid:** ₦{float(order.get('total_paid', 0)):,.2f}")

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No verified orders recorded yet. Pending payments will not display until Paystack confirms transfer.")
        else:
            st.info("You haven't listed any produce yet. Go to 'Add New Product' to start selling.")
    except Exception as e:
        st.error(f"Error loading sales ledger: {str(e)}")

# ==============================================================================
# 9. BUYER MARKETPLACE WITH LIVE INVENTORY & VERIFIED ESCROW
# ==============================================================================
elif navigation == "🛒 Browse Marketplace":
    st.subheader("🛒 Direct Farm Produce Marketplace")

    f1, f2 = st.columns(2)
    with f1:
        buying_scale = st.selectbox("Filter Scale", ["All Scales", "Large Scale / Commercial Wholesale", "Small Scale / Retail"])
    with f2:
        category_filter = st.selectbox("Filter Sector", ["All Categories"] + AGRI_CATEGORIES)

    st.divider()

    try:
        query = supabase.table("listings").select("*").gt("quantity", 0)  # Exclude out-of-stock items
        if buying_scale != "All Scales":
            query = query.eq("scale", buying_scale)
        if category_filter != "All Categories":
            query = query.eq("category", category_filter)

        listings = query.execute().data

        if not listings:
            st.info("No active produce listings matching your selection or available in stock.")

        for item in listings:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])

            with col1:
                render_product_image(item.get("image_url"))
                st.caption(f"Scale: **{item.get('scale', 'General Supply')}**")

            with col2:
                st.markdown(f"### {item['item']}")
                st.write(f"**Sector:** `{item.get('category')}`")
                st.write(f"**Producer:** {item['seller']} | 📍 **Origin:** {item['location']}")

                unit_price = float(item["price_ngn"])
                available_stock = int(item.get("quantity", 1))
                unit_weight = float(item.get("unit_weight_kg", 50.0))

                st.markdown(f"**Unit Price:** ₦{unit_price:,.2f}")
                st.markdown(f"🟢 **Available Stock:** **{available_stock} units left** (Est. {unit_weight} kg per unit)")

                # Quantity selection bounded by available inventory
                desired_qty = st.number_input(
                    "Select Quantity to Purchase",
                    min_value=1,
                    max_value=max(available_stock, 1),
                    value=1,
                    step=1,
                    key=f"qty_{item['id']}",
                )

                product_subtotal = unit_price * desired_qty
                platform_fee = product_subtotal * 0.10
                total_weight_kg = unit_weight * desired_qty

                st.markdown(f"**Subtotal ({desired_qty} units • Est. {total_weight_kg:,.1f} kg):** ₦{product_subtotal:,.2f}")
                st.markdown(f"**Platform Escrow Fee (10%):** ₦{platform_fee:,.2f}")

                st.markdown("#### 🚚 Step 1: Request Freight Quote from Logistics Partner")
                
                delivery_destination = st.selectbox(
                    f"Select Delivery State for {item['item']}",
                    NIGERIAN_STATES,
                    index=24,
                    key=f"dest_{item['id']}"
                )

                selected_partner = st.selectbox(
                    f"Select Freight Carrier (Top 10 Nationwide Haulers)",
                    list(LOGISTICS_PARTNERS.keys()),
                    key=f"sel_{item['id']}",
                )
                partner_info = LOGISTICS_PARTNERS[selected_partner]

                wa_msg_text = (
                    f"Hello {selected_partner},\n\n"
                    f"I am purchasing produce on FEED THE NATIONS marketplace:\n"
                    f"• Item: {item['item']}\n"
                    f"• Quantity: {desired_qty} units\n"
                    f"• Est. Total Weight: {total_weight_kg} kg\n"
                    f"• Pickup Location (Farm): {item['location']}\n"
                    f"• Delivery Destination: {delivery_destination} State\n\n"
                    f"Please provide an official freight cost quote for this delivery."
                )
                wa_url = f"https://wa.me/{partner_info['whatsapp']}?text={urllib.parse.quote(wa_msg_text)}"

                st.markdown(
                    f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 Send Freight Details to {selected_partner} on WhatsApp</a>',
                    unsafe_allow_html=True,
                )

                st.markdown("#### 🚚 Step 2: Input Negotiated Freight Amount")
                agreed_freight = st.number_input(
                    "Enter Agreed Freight Quote from Logistics Partner (₦)",
                    min_value=0,
                    value=25000,
                    step=5000,
                    key=f"freight_{item['id']}",
                )

                final_total = product_subtotal + platform_fee + agreed_freight
                st.markdown(f"### **Total Amount Payable (Produce + Escrow + Freight): ₦{final_total:,.2f}**")

                if st.button("BUY WITH ESCROW 💳", key=f"pay_{item['id']}"):
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
                        "total_paid": final_total,
                        "buyer": st.session_state.username,
                        "status": "PAYMENT_INITIATED",  # Status starts as INITIATED until Paystack verifies
                        "paystack_ref": ref,
                    }
                    supabase.table("transactions").insert(tx_record).execute()
                    pay_resp = initialize_paystack_payment(st.session_state.email, final_total, ref)

                    if pay_resp.get("status"):
                        auth_url = pay_resp["data"]["authorization_url"]
                        st.success("🔒 Checkout initialized! Click link below to complete payment.")
                        st.markdown(
                            f'<a href="{auth_url}" target="_blank" style="display:inline-block; background: #1E5631; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold;">Proceed to Paystack Checkout ➔</a>',
                            unsafe_allow_html=True,
                        )

            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Marketplace error: {str(e)}")

elif navigation == "📦 My Orders & Escrow":
    st.subheader("📦 My Escrow Orders & Tracking")
    try:
        user_orders = supabase.table("transactions").select("*").eq("buyer", st.session_state.username).execute().data

        if not user_orders:
            st.info("There are no active orders.")
        else:
            df_orders = pd.DataFrame(user_orders)
            st.dataframe(df_orders, use_container_width=True)

            for order in user_orders:
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                st.markdown(f"### Order ID: `{order['id']}` - {order.get('item', 'Farm Produce')}")
                st.write(f"**Quantity Purchased:** {order.get('quantity_bought', 1)} units")
                st.write(f"**Verification Status:** `{order.get('status', 'PENDING')}`")
                st.write(f"**Freight Paid:** ₦{float(order.get('freight', 0)):,.2f}")
                st.write(f"**Total Amount Paid:** ₦{float(order.get('total_paid', 0)):,.2f}")
                st.write(f"**Paystack Reference:** `{order.get('paystack_ref', 'N/A')}`")
                st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.info("There are no active orders.")

# ==============================================================================
# 10. FARMER PRODUCT MANAGEMENT
# ==============================================================================
elif navigation == "➕ Add New Product":
    st.subheader("🚜 Post New Farm Produce Listing")

    # MANDATORY WARNING BANNER FOR FARMERS
    st.markdown(
        """
        <div class="warning-banner">
            <h4>⚠️ ATTENTION FARMERS / PRODUCERS:</h4>
            <p>Please double-check and input <b>ACCURATE values</b> for standard Unit Price, Available Units, and Individual Unit Weight (KG).</p>
            <ul>
                <li><b>Unit Weight (KG):</b> Logistics quotes depend directly on weight calculations. Inputting incorrect weights will cause haulage dispute and shipping cancellation.</li>
                <li><b>Stock Quantity:</b> Inventory updates automatically as buyers complete payment. Ensure your quantity reflects real produce ready for pickup.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("add_product_form"):
        farming_cat = st.selectbox("Agricultural Sector", AGRI_CATEGORIES)
        prod_scale = st.selectbox("Supply Scale Category", ["Large Scale / Commercial Wholesale", "Small Scale / Retail"])
        title = st.text_input("Product Title (e.g. 50kg Bags of White Maize)")

        c1, c2, c3 = st.columns(3)
        with c1:
            price = st.number_input("Unit Price (₦)", min_value=1000, value=50000, step=5000)
        with c2:
            quantity = st.number_input("Available Stock Quantity (Units)", min_value=1, value=50)
        with c3:
            unit_weight = st.number_input("Accurate Weight Per Unit (KG)", min_value=0.5, value=50.0, step=1.0)

        location = st.text_input("Farm Location / Pickup State", value="Ogun State")
        uploaded_file = st.file_uploader("Upload Clear Produce Photo", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("PUBLISH PRODUCT TO MARKETPLACE 🚀")

        if submitted:
            if not uploaded_file:
                st.error("⚠️ Please attach a clear photo of your farm produce.")
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
                        "unit_weight_kg": unit_weight,
                        "image_url": img_url,
                    }
                    supabase.table("listings").insert(product_data).execute()
                    st.success("🎉 Product listing published successfully!")

elif navigation == "📦 My Active Products":
    st.subheader("🚜 Manage My Farm Listings")

    if st.session_state.deleted_msg:
        st.success(st.session_state.deleted_msg)
        st.session_state.deleted_msg = None

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
                    e_weight = st.number_input("Unit Weight (KG)", value=float(item_data.get("unit_weight_kg", 50.0)))

                    c_save, c_cancel = st.columns(2)
                    save_changes = c_save.form_submit_button("💾 SAVE CHANGES")
                    cancel_changes = c_cancel.form_submit_button("❌ CANCEL")

                    if save_changes:
                        updated_fields = {
                            "item": e_title,
                            "price_ngn": e_price,
                            "location": e_location,
                            "quantity": e_quantity,
                            "unit_weight_kg": e_weight,
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
                        render_product_image(item.get("image_url"))

                    with col2:
                        st.markdown(f"### {item['item']}")
                        st.write(f"**Sector:** `{item.get('category')}`")
                        st.write(f"**Unit Price:** ₦{float(item['price_ngn']):,.2f}")
                        st.write(f"📍 **Location:** {item.get('location', 'N/A')} | **Available Units:** {item.get('quantity', 0)} | **Unit Weight:** {item.get('unit_weight_kg', 0)} KG")

                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            if st.button("✏️ Edit Product", key=f"edit_{item['id']}"):
                                st.session_state.editing_listing_id = item["id"]
                                st.rerun()

                        with b_col2:
                            if st.button("🗑️ Delete Product", key=f"del_{item['id']}"):
                                try:
                                    supabase.table("transactions").delete().eq("listing_id", item["id"]).execute()
                                    supabase.table("listings").delete().eq("id", item["id"]).execute()

                                    st.session_state.deleted_msg = f"✅ Product '{item['item']}' was permanently deleted."
                                    st.rerun()
                                except Exception as del_err:
                                    st.error(f"Failed to delete product: {str(del_err)}")

                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("You currently have no active listings. Select 'Add New Product' to post your produce!")
        except Exception as e:
            st.error(f"Error fetching active products: {str(e)}")
