import streamlit as st
import hashlib
import sqlite3
import os

class AuthManager:
    def __init__(self, db_path='users.db'):
        """
        Initialize the authentication manager with a SQLite database
        """
        self.db_path = db_path
        self._create_users_table()

    def _create_users_table(self):
        """
        Create users table if it doesn't exist
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    email TEXT
                )
            ''')
            conn.commit()

    def _hash_password(self, password):
        """
        Hash the password using SHA-256
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email):
        """
        Register a new user
        """
        # Check if username already exists
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False
            
            # Hash the password before storing
            hashed_password = self._hash_password(password)
            
            # Insert new user
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                           (username, hashed_password, email))
            conn.commit()
            return True

    def validate_login(self, username, password):
        """
        Validate user login credentials
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                # Check if the hashed password matches
                stored_password = result[0]
                return stored_password == self._hash_password(password)
            return False

def display_login_page():
    """
    Render the login page with registration and login functionality
    """
    st.title("🔐 YourNote - Login")
    
    # Initialize AuthManager
    auth_manager = AuthManager()
    
    # Choose between Login and Register
    login_or_register = st.radio("Select Action", ["Login", "Register"])
    
    if login_or_register == "Login":
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if auth_manager.validate_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    else:
        # Registration form
        with st.form("register_form"):
            new_username = st.text_input("Choose a Username")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                # Validate registration
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    registration_success = auth_manager.register_user(new_username, new_password, new_email)
                    if registration_success:
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error("Username already exists. Please choose another.")

def logout():
    """
    Clear session state and log out the user
    """
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()