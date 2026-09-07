import os
import streamlit as st
from flask import Flask, jsonify, request

# Initialize Flask application for backend utilities/API
flask_app = Flask(__name__)


# -----------------------------------------------------------------------------
# FLASK BACKEND ROUTES (API / Authentication / Registration Setup)
# -----------------------------------------------------------------------------
@flask_app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "app": "FEED THE NATIONS"}), 200


@flask_app.route("/api/register", methods=["POST"])
def register_user():
    """Handles user registration and triggers confirmation setup."""
    data = request.get_json() or {}
    email = data.get("email")
    full_name = data.get("full_name")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # TODO: Connect with your database / auth provider (e.g., Supabase) here
    # to send the registration setup email.

    return (
        jsonify(
            {
                "message": f"Registration initiated for {email}. Please check your email inbox to complete registration setup.",
                "user": full_name,
            }
        ),
        200,
    )


# -----------------------------------------------------------------------------
# STREAMLIT FRONTEND INTERFACE (FEED THE NATIONS Vision)
# -----------------------------------------------------------------------------
def run_streamlit_ui():
    st.set_page_config(
        page_title="FEED THE NATIONS",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header & Vision Statement
    st.title("🌾 FEED THE NATIONS")
    st.caption("Empowering Agricultural Transformation, Sustainability & Food Security")
    st.markdown("---")

    # Navigation Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Register / Onboarding", "Marketplace", "Farmer Dashboard", "About Our Vision"],
    )

    if page == "Home":
        st.header("Welcome to FEED THE NATIONS")
        st.write(
            "Connecting farmers, suppliers, and communities to ensure sustainable food distribution worldwide."
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Farmers Supported", "10,000+")
        with col2:
            st.metric("Crops Distributed", "50,000 Tons")
        with col3:
            st.metric("Active Regions", "24")

    elif page == "Register / Onboarding":
        st.header("Join the Movement")
        st.subheader("Create Your Account")

        with st.form("registration_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            role = st.selectbox("Role", ["Farmer", "Distributor", "Investor", "Consumer"])
            submitted = st.form_submit_button("Register")

            if submitted:
                if email:
                    # Clear guidance instructing users to complete registration via email
                    st.success(
                        f"Thank you, **{full_name or 'partner'}**! Registration initiated. "
                        f"Please **check your email address ({email})** for complete registration setup."
                    )
                    st.info(
                        "📩 A confirmation link has been sent to your inbox. Follow the instructions in the email to activate your account."
                    )
                else:
                    st.error("Please enter a valid email address to complete registration.")

    elif page == "Marketplace":
        st.header("Agricultural Marketplace")
        st.write("Browse produce, equipment, and agricultural services.")
        # Marketplace implementation placeholder

    elif page == "Farmer Dashboard":
        st.header("Farmer Insights & Resources")
        st.write("Manage yields, monitor weather updates, and access financial tools.")

    elif page == "About Our Vision":
        st.header("Our Mission & Vision")
        st.write(
            """
            **FEED THE NATIONS** is dedicated to eradicating hunger and boosting agricultural efficiency through technology. 
            By bridging the gap between local producers and global demand, we build resilient agricultural ecosystems.
            """
        )

# -----------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -----------------------------------------------------------------------------
# When deployed via `streamlit run app.py`, Streamlit executes this file.
# We render the Streamlit UI directly.
run_streamlit_ui()
