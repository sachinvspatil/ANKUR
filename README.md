# ANKUR – JNVK Alumni Data Management

A modern web application for maintaining and connecting alumni data for Jawahar Navodaya Vidyalaya, Karkala (JNVK).

## Features

- 📝 **Alumni Registration:**
  - Collects Name, Phone Number, Batch Number, Year of Passout, Email, Address, and Profession.
- 🔐 **Secure Login:**
  - Passwords are securely hashed and stored.
- 👀 **Alumni Directory:**
  - Logged-in users can view a searchable list of alumni (Name, Batch, Profession, Email, Year of Passout).
- 🛡️ **Admin Panel:**
  - Activate/deactivate/delete users, view all alumni, and manage accounts.
- ☁️ **Supabase Backend:**
  - All data is securely stored and managed using Supabase.
- 🎨 **Modern UI:**
  - Responsive, card-style login and registration forms with custom CSS.

## Requirements

- Python 3.8 or above
- Streamlit
- pandas
- supabase-py
- All dependencies in `requirements.txt`

## Setup & Run

1. Clone this repo:
   ```sh
   git clone https://github.com/sachinvspatil/ANKUR.git
   cd ANKUR
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your `secrets.toml` in `.streamlit/` with your Supabase and admin credentials.
4. Run the app:
   ```sh
   streamlit run main.py
   ```

## Supabase Tables
- `alumni_users`: Stores alumni registration and login info.
- `user_sessions_ankur`: Tracks user login sessions.

## License
MIT