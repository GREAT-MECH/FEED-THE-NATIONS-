import os
import requests
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Flask Session Key
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "feed-the-nations-secret-key-change-me")

# Supabase Configurations
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJld2V3c3Ria25pZ29seGlvendwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgzNDU5MTUsImV4cCI6MjEwMzkyMTkxNX0.s1reBkT9vmYSKGM0yPJTJiAWxT0xxdO446GVOI6ib3U
""")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Paystack Configurations
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "sk_live_5d70f03c20eea14b71be5b116e453e6a6848eebe")
PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"


# -------------------------------------------------------------------
# Core Routes & Vision
# -------------------------------------------------------------------

@app.route("/")
def home():
    user = session.get("user")
    return render_template("index.html", user=user)


@app.route("/about")
def about():
    """FEED THE NATIONS Vision & Mission"""
    return render_template("about.html")


# -------------------------------------------------------------------
# Authentication (Supabase)
# -------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Please provide both an email and a password.", "error")
            return render_template("register.html")

        try:
            # Trigger registration via Supabase Auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:
                # Inform user about email confirmation requirement
                flash(
                    "Registration successful! Please check your inbox and click the verification link sent to your email to activate your account.",
                    "success"
                )
                return redirect(url_for("login"))
            else:
                flash("Could not complete registration. Please try again.", "error")

        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg:
                flash("An account with this email already exists. Please log in.", "error")
            else:
                flash(f"Sign-up error: {error_msg}", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session["user"] = {
                "id": response.user.id,
                "email": response.user.email
            }
            flash("Welcome back to FEED THE NATIONS!", "success")
            return redirect(url_for("dashboard"))

        except Exception:
            flash("Login failed. Check your credentials or ensure your email has been confirmed.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        flash("Please log in to access your dashboard.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)


# -------------------------------------------------------------------
# Paystack Revenue & Donation System
# -------------------------------------------------------------------

@app.route("/donate", methods=["GET", "POST"])
def donate():
    user = session.get("user")
    
    if request.method == "POST":
        email = request.form.get("email", user.get("email") if user else "").strip()
        amount = request.form.get("amount", "").strip()

        if not email or not amount:
            flash("Please enter a valid email and donation amount.", "error")
            return render_template("donate.html")

        # Convert amount to kobo (Paystack expects amounts in smallest currency unit)
        amount_in_kobo = int(float(amount) * 100)

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": amount_in_kobo,
            "callback_url": url_for("paystack_callback", _external=True)
        }

        try:
            paystack_res = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers)
            res_data = paystack_res.json()

            if res_data.get("status"):
                # Redirect user to Paystack payment authorization URL
                authorization_url = res_data["data"]["authorization_url"]
                return redirect(authorization_url)
            else:
                flash("Could not initiate transaction. Please try again.", "error")

        except Exception as e:
            flash(f"Payment gateway error: {str(e)}", "error")

    return render_template("donate.html", user=user)


@app.route("/paystack/callback")
def paystack_callback():
    reference = request.args.get("reference")
    if not reference:
        flash("Invalid transaction reference.", "error")
        return redirect(url_for("home"))

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    try:
        verify_res = requests.get(f"{PAYSTACK_VERIFY_URL}{reference}", headers=headers)
        res_data = verify_res.json()

        if res_data.get("status") and res_data["data"]["status"] == "success":
            payment_data = res_data["data"]
            amount_paid = payment_data["amount"] / 100  # Convert back from kobo
            
            # Record transaction in Supabase DB (Optional)
            try:
                supabase.table("donations").insert({
                    "email": payment_data["customer"]["email"],
                    "amount": amount_paid,
                    "reference": reference,
                    "status": "success"
                }).execute()
            except Exception:
                pass  # Continue even if table logging fails

            flash(f"Thank you for your donation of ₦{amount_paid:,.2f}! Your support powers the FEED THE NATIONS mission.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Payment verification failed. Please contact support if debited.", "error")

    except Exception as e:
        flash(f"Verification error: {str(e)}", "error")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
