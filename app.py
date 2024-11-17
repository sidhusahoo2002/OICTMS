import streamlit as st # type: ignore
import sqlite3

# Database connection function
def create_connection():
    conn = sqlite3.connect('ictms.db')
    return conn

# Function to authenticate user
def authenticate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to register user
def register_user(username, password, role):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

# Function to fetch tournaments
def fetch_tournaments():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tournaments")
    tournaments = cursor.fetchall()
    conn.close()
    return tournaments

# Function to add tournament
def add_tournament(name, date, location, fee):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tournaments (name, date, location, fee) VALUES (?, ?, ?, ?)", (name, date, location, fee))
    conn.commit()
    conn.close()

# Function to register for a tournament
def register_for_tournament(user_id, tournament_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registrations (user_id, tournament_id) VALUES (?, ?)", (user_id, tournament_id))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("Inter College Tournament Management System")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Select Action", menu)

if choice == "Login":
    st.subheader("Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.success(f"Logged in as {user[1]}")
            user_id = user[0]  # Assuming the first column is the user ID
            if user[3] == "admin":
                st.subheader("Admin Dashboard")
                st.write("Welcome to the Admin Dashboard")
                
                # Admin functionalities
                tournament_name = st.text_input("Tournament Name")
                tournament_date = st.text_input("Tournament Date")
                tournament_location = st.text_input("Tournament Location")
                tournament_fee = st.number_input("Tournament Fee", min_value=0.0)
                
                if st.button("Add Tournament"):
                    add_tournament(tournament_name, tournament_date, tournament_location, tournament_fee)
                    st.success("Tournament added successfully!")
                
                # View all tournaments
                st.subheader("All Tournaments")
                tournaments = fetch_tournaments()
                for tournament in tournaments:
                    st.write(f"Name: {tournament[1]}, Date: {tournament[2]}, Location: {tournament[3]}, Fee: {tournament[4]}")
                    
            elif user[3] == "player":
                st.subheader("Player Dashboard")
                st.write("Welcome to the Player Dashboard")
                
                # View all tournaments
                st.subheader("Available Tournaments")
                tournaments = fetch_tournaments()
                for tournament in tournaments:
                    st.write(f"Name: {tournament[1]}, Date: {tournament[2]}, Location: {tournament[3]}, Fee: {tournament[4]}")
                    if st.button(f"Register for {tournament[1]}"):
                        register_for_tournament(user_id, tournament[0])  # Assuming the first column is the tournament ID
                        st.success(f"Registered for {tournament[1]} successfully!")
        else:
            st.error("Invalid username or password")

elif choice == "Register":
    st.subheader("Registration Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Select Role", ["player", "admin"])
    
    if st.button("Register"):
        register_user(username, password, role)
        st.success("User  registered successfully!")