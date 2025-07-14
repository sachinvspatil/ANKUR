import streamlit as st
import base64
import hashlib
import pandas as pd
import uuid
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Utility ------------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ------------------ Supabase Table Setup ------------------
# Table: alumni_users (id, name, phone, batch, year_of_passout, email, address, profession, password_hash, active)
# Table: user_sessions_ankur (id, email, session_token, active)

# ------------------ User Management ------------------
def save_user(name, phone, batch, year, email, address, profession, password_hash, active=True):
    email = email.lower()
    supabase.table("alumni_users").insert({
        "name": name,
        "phone": phone,
        "batch": batch,
        "year_of_passout": year,
        "email": email,
        "address": address,
        "profession": profession,
        "password_hash": password_hash,
        "active": active
    }).execute()

def user_exists(email):
    email = email.lower()
    res = supabase.table("alumni_users").select("id").eq("email", email).execute()
    return len(res.data) > 0

def validate_login(email, password):
    pw_hash = hash_password(password)
    email = email.lower()
    res = supabase.table("alumni_users").select("password_hash,active").eq("email", email).execute()
    if not res.data:
        return False, "User not found. Please register."
    user = res.data[0]
    if user["password_hash"] != pw_hash:
        return False, "Incorrect password."
    if not user["active"]:
        return False, "Account not activated. Please contact admin."
    return True, "Login successful."

def activate_user(email, active=True):
    email = email.lower()
    supabase.table("alumni_users").update({"active": active}).eq("email", email).execute()

def delete_user(email):
    email = email.lower()
    supabase.table("alumni_users").delete().eq("email", email).execute()

def load_users():
    res = supabase.table("alumni_users").select("name,phone,batch,year_of_passout,email,address,profession,active").execute()
    return pd.DataFrame(res.data)

# ------------------ Session Management ------------------
def is_user_logged_in(email, session_token=None):
    email = email.lower()
    res = supabase.table("user_sessions_ankur").select("session_token,active").eq("email", email).eq("active", True).execute()
    if not res.data:
        return False
    if session_token:
        return res.data[0]["session_token"] == session_token
    return True

def set_user_session(email, active=True, session_token=None):
    email = email.lower()
    if active:
        if not session_token:
            session_token = str(uuid.uuid4())
        res = supabase.table("user_sessions_ankur").select("id").eq("email", email).execute()
        if res.data:
            session_id = res.data[0]["id"]
            supabase.table("user_sessions_ankur").update({"active": True, "session_token": session_token}).eq("id", session_id).execute()
        else:
            supabase.table("user_sessions_ankur").insert({"email": email, "active": True, "session_token": session_token}).execute()
        return session_token
    else:
        supabase.table("user_sessions_ankur").update({"active": False, "session_token": None}).eq("email", email).execute()
        return None

# ------------------ UI Config ------------------
st.set_page_config(page_title="ANKUR - JNVK Alumni", page_icon="logo.png", layout="wide")
image_path = "logo.png"
image_base64 = get_image_base64(image_path)
st.markdown(
    f"""
    <style>
    .header {{ display: flex; align-items: center; }}
    .header img {{ width: 50px; }}
    .header h1 {{ margin-left: 10px; font-size: 2rem; }}
    .copyright {{
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 14px;
        color: gray;
        text-align: center;
    }}
    </style>
    <div class="header">
        <img src="data:image/png;base64,{image_base64}" alt="Logo">
        <h1>ANKUR – JNVK Alumni</h1>
    </div>
    <div class="copyright">© 2025 ANKUR. All rights reserved.</div>
    """,
    unsafe_allow_html=True,
)

# ------------------ Login/Register UI ------------------
def is_valid_email(email):
    import re
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def login_register_ui():
    # Load external CSS for styling
    with open("ankur_style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Place tabs directly in the main area for full width
    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Register"])
    with tab1:
        st.markdown('<div class="ankur-logo"><img src="data:image/png;base64,' + get_image_base64("logo.png") + '" /></div>', unsafe_allow_html=True)
        st.markdown('<div class="ankur-title">Welcome to ANKUR</div>', unsafe_allow_html=True)
        st.markdown('<div class="ankur-sub">JNVK Alumni Portal Login</div>', unsafe_allow_html=True)
        username = st.text_input("✉️ Email", key="login_user")
        password = st.text_input("🔒 Password", type="password", key="login_pw")
        if st.button("Login", key="login_btn"):
            if is_user_logged_in(username) and not is_user_logged_in(username, st.session_state.get("session_token")):
                st.error("This user is already logged in from another device or session.")
            else:
                ok, msg = validate_login(username, password)
                if ok:
                    session_token = set_user_session(username, active=True)
                    st.session_state.user = username
                    st.session_state.session_token = session_token
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="ankur-logo"><img src="data:image/png;base64,' + get_image_base64("logo.png") + '" /></div>', unsafe_allow_html=True)
        st.markdown('<div class="ankur-title">Register for ANKUR</div>', unsafe_allow_html=True)
        st.markdown('<div class="ankur-sub">Create your alumni account</div>', unsafe_allow_html=True)
        new_name = st.text_input("👤 Full Name", key="reg_name")
        new_phone = st.text_input("📱 Phone Number", key="reg_phone")
        new_batch = st.text_input("🏷️ Batch Number", key="reg_batch")
        new_year = st.text_input("🎓 Year of Passout", key="reg_year")
        new_email = st.text_input("✉️ Email", key="reg_user")
        new_address = st.text_area("🏠 Address", key="reg_address")
        new_profession = st.text_input("💼 Profession", key="reg_profession")
        new_password = st.text_input("🔒 Choose Password", type="password", key="reg_pw")
        if st.button("Register", key="register_btn"):
            if not is_valid_email(new_email):
                st.error("Please enter a valid email address.")
            elif not new_phone or not new_phone.isdigit() or len(new_phone) < 10:
                st.error("Please enter a valid phone number.")
            elif user_exists(new_email):
                st.error("Email already registered.")
            elif not new_name or not new_password or not new_batch or not new_year or not new_profession:
                st.error("All fields except address are required.")
            else:
                save_user(new_name, new_phone, new_batch, new_year, new_email, new_address, new_profession, hash_password(new_password), active=True)
                st.success("Registration successful! You can now log in.")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Admin Panel ------------------
ADMIN_USERNAME = st.secrets["admin"]["username"]
ADMIN_PASSWORD = st.secrets["admin"]["password"]

def admin_login_ui():
    st.title("🛡️ Admin Access")
    u = st.text_input("Admin Username")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if u == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            st.session_state.admin = True
            st.session_state.show_admin_login = False
            st.rerun()
        else:
            st.error("Invalid admin credentials")

def admin_panel():
    st.title("👥 Admin Dashboard")
    df = load_users()
    st.markdown(f"**Total Registered Alumni:** {len(df)}")
    act = df[df.active.astype(str).str.lower()=="true"]
    inact = df[df.active.astype(str).str.lower()!="true"]
    st.markdown(f"**• Active:** {len(act)} • **Inactive:** {len(inact)}")
    st.markdown("---")
    st.subheader("Manage Account Status")
    for i, r in df.iterrows():
        cols = st.columns([3,2,1,1,1])
        cols[0].write(r["email"])
        cols[1].write(r.get("phone", "N/A"))
        cols[2].write("🟢" if str(r["active"]).lower()=="true" else "🔴")
        if str(r["active"]).lower()!="true":
            if cols[3].button("Activate", key=f"act_{r['email']}"):
                activate_user(r["email"], True)
                st.rerun()
        else:
            if cols[3].button("Deactivate", key=f"deact_{r['email']}"):
                activate_user(r["email"], False)
                st.rerun()
        if cols[4].button("Delete", key=f"del_{r['email']}"):
            delete_user(r["email"])
            st.rerun()
    if st.button("Logout Admin"):
        del st.session_state.admin
        st.rerun()

# ------------------ Main App Routing ------------------
if st.session_state.get("show_admin_login"):
    admin_login_ui()
    st.stop()

if st.session_state.get("admin"):
    admin_panel()
    st.stop()

if "user" not in st.session_state:
    login_register_ui()
    st.stop()

st.sidebar.success(f"Logged in: {st.session_state.user}")
# On every page load, check session_token
if "user" in st.session_state and "session_token" in st.session_state:
    if not is_user_logged_in(st.session_state.user, st.session_state.session_token):
        st.warning("You have been logged out because your account was used to log in elsewhere.")
        del st.session_state.user
        del st.session_state.session_token
        st.rerun()

# On logout, clear the session in Supabase
if st.sidebar.button("Logout"):
    if "user" in st.session_state:
        set_user_session(st.session_state.user, active=False)
        del st.session_state.user
        if "session_token" in st.session_state:
            del st.session_state.session_token
    st.rerun()

# Add Admin Login button to sidebar
if st.sidebar.button("Admin Login"):
    st.session_state.show_admin_login = True

# ------------------ Alumni Directory ------------------
st.title("🎓 JNVK Alumni Directory")

alumni_df = load_users()

st.markdown("#### Browse Alumni (Name, Batch, Profession, Email, Year of Passout)")

# Only show selected fields for privacy
show_df = alumni_df[["name", "batch", "profession", "email", "year_of_passout"]].sort_values(by=["year_of_passout", "batch", "name"], ascending=[False, True, True])
st.dataframe(show_df, use_container_width=True)

st.info("You can search, filter, and sort the alumni list above. For privacy, only limited details are shown.")

st.markdown("""
---
💬 **For queries or corrections, contact the admin.
""")
