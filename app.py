import streamlit as st # type: ignore
import sqlite3
from sqlite3 import Error
import pandas as pd # type: ignore

# Database functions
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('app.db')
    except Error as e:
        st.error(f"Error creating connection to database: {e}")
    return conn

def create_tables(conn):
    try:
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        username text NOT NULL,
                                        password text NOT NULL,
                                        role text NOT NULL,
                                        college text
                                    ); """
        sql_create_tournaments_table = """ CREATE TABLE IF NOT EXISTS tournaments (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL,
                                            details text NOT NULL
                                        ); """
        sql_create_registrations_table = """ CREATE TABLE IF NOT EXISTS registrations (
                                            id integer PRIMARY KEY,
                                            user_id integer NOT NULL,
                                            tournament_id integer NOT NULL,
                                            FOREIGN KEY (user_id) REFERENCES users (id),
                                            FOREIGN KEY (tournament_id) REFERENCES tournaments (id)
                                        ); """
        if conn is not None:
            c = conn.cursor()
            c.execute(sql_create_users_table)
            c.execute(sql_create_tournaments_table)
            c.execute(sql_create_registrations_table)
        else:
            st.error("Error! Cannot create the database connection.")
    except Error as e:
        st.error(f"Error creating tables: {e}")

def register_user(conn, username, password, role, college=None):
    try:
        sql = ''' INSERT INTO users(username, password, role, college)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (username, password, role, college))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        st.error(f"Error registering user: {e}")
        return None

def login_user(conn, username, password, role):
    try:
        sql = ''' SELECT * FROM users WHERE username=? AND password=? AND role=? '''
        cur = conn.cursor()
        cur.execute(sql, (username, password, role))
        return cur.fetchone()
    except Error as e:
        st.error(f"Error logging in user: {e}")
        return None

def get_tournaments(conn):
    try:
        sql = ''' SELECT * FROM tournaments '''
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Error as e:
        st.error(f"Error fetching tournaments: {e}")
        return []

def register_tournament(conn, user_id, tournament_id):
    try:
        sql = ''' INSERT INTO registrations(user_id, tournament_id)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (user_id, tournament_id))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        st.error(f"Error registering for tournament: {e}")
        return None

def get_players(conn):
    try:
        sql = ''' SELECT * FROM users WHERE role='player' '''
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Error as e:
        st.error(f"Error fetching players: {e}")
        return []

def update_tournament(conn, tournament_id, name, details):
    try:
        sql = ''' UPDATE tournaments
                  SET name = ?,
                      details = ?
                  WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (name, details, tournament_id))
        conn.commit()
    except Error as e:
        st.error(f"Error updating tournament: {e}")

def create_tournament(conn, name, details):
    try:
        sql = ''' INSERT INTO tournaments(name, details)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (name, details))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        st.error(f"Error creating tournament: {e}")
        return None

def get_registered_tournaments(conn, user_id):
    try:
        sql = ''' SELECT t.name, t.details FROM tournaments t
                  JOIN registrations r ON t.id = r.tournament_id
                  WHERE r.user_id = ? '''
        cur = conn.cursor()
        cur.execute(sql, (user_id,))
        return cur.fetchall()
    except Error as e:
        st.error(f"Error fetching registered tournaments: {e}")
        return []

def get_player_registrations(conn):
    try:
        sql = ''' SELECT u.username, u.college, t.name FROM users u
                  JOIN registrations r ON u.id = r.user_id
                  JOIN tournaments t ON t.id = r.tournament_id
                  WHERE u.role = 'player' '''
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Error as e:
        st.error(f"Error fetching player registrations: {e}")
        return []

# Streamlit app
def main():
    st.title("Inter College Tournament Management System")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = "Home"

    if st.session_state['logged_in']:
        user = st.session_state['user']
        st.sidebar.write(f"Logged in as: {user[1]}")

    menu = ["Home", "Player Section", "Admin Section"]
    choice = st.sidebar.selectbox("Menu", menu)

    conn = create_connection()
    create_tables(conn)

    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['page'] = "Home"
        st.success("You have successfully logged out")

    if choice == "Home":
        st.session_state['page'] = "Home"
    elif choice == "Player Section":
        st.session_state['page'] = "Player Section"
    elif choice == "Admin Section":
        st.session_state['page'] = "Admin Section"

    if st.session_state['page'] == "Home":
        st.subheader("Home")
        st.image("images/football.jpg", caption="Soccer Tournament", use_container_width=True)
        st.image("images/cricket.jpg", caption="Cricket Tournament", use_container_width=True)

    elif st.session_state['page'] == "Player Section":
        player_menu = ["Player Login", "New Player Registration", "Player Dashboard"]
        player_choice = st.sidebar.selectbox("Player Menu", player_menu)

        if player_choice == "Player Login":
            st.subheader("Player Login Section")
            username = st.text_input("User Name")
            password = st.text_input("Password", type='password')
            role = "player"
            if st.button("Login"):
                user = login_user(conn, username, password, role)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.success("Logged In as {}".format(username))
                else:
                    st.warning("Incorrect Username/Password")

        elif player_choice == "New Player Registration":
            st.subheader("Create New Player Account")
            username = st.text_input("User Name")
            password = st.text_input("Password", type='password')
            college = st.text_input("College Name")
            if st.button("SignUp"):
                if username and password and college:
                    user_id = register_user(conn, username, password, "player", college)
                    if user_id:
                        st.success("You have successfully created a player account")
                        st.info("Go to Player Login Menu to login")
                    else:
                        st.error("Failed to create account. Please try again.")
                else:
                    st.warning("Please fill out all fields.")

        elif player_choice == "Player Dashboard":
            if 'logged_in' in st.session_state and st.session_state['logged_in']:
                user = st.session_state['user']
                if user[3] == 'player':
                    st.subheader("Player Dashboard")
                    tournaments = get_tournaments(conn)
                    if tournaments:
                        for tournament in tournaments:
                            st.write("Tournament: ", tournament[1])
                            st.write("Details: ", tournament[2])
                            if st.button(f"Register for {tournament[1]}", key=tournament[0]):
                                register_tournament(conn, user[0], tournament[0])
                                st.success(f"Registered for {tournament[1]}")
                    else:
                        st.write("No tournaments available at the moment.")
                    
                    st.subheader("Registered Tournaments")
                    registered_tournaments = get_registered_tournaments(conn, user[0])
                    if registered_tournaments:
                        for rt in registered_tournaments:
                            st.write("Tournament: ", rt[0])
                            st.write("Details: ", rt[1])
                    else:
                        st.write("You have not registered for any tournaments.")
                else:
                    st.warning("You are not authorized to view this page")
            else:
                st.warning("Please login first")

    elif st.session_state['page'] == "Admin Section":
        admin_menu = ["Admin Login", "New Admin Registration", "Admin Dashboard"]
        admin_choice = st.sidebar.selectbox("Admin Menu", admin_menu)

        if admin_choice == "Admin Login":
            st.subheader("Admin Login Section")
            username = st.text_input("Admin User Name")
            password = st.text_input("Admin Password", type='password')
            role = "admin"
            if st.button("Login"):
                user = login_user(conn, username, password, role)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.success("Logged In as Admin {}".format(username))
                else:
                    st.warning("Incorrect Admin Username/Password")

        elif admin_choice == "New Admin Registration":
            st.subheader("Create New Admin Account")
            username = st.text_input("Admin User Name")
            password = st.text_input("Password", type='password')
            if st.button("SignUp"):
                if username and password:
                    user_id = register_user(conn, username, password, "admin")
                    if user_id:
                        st.success("You have successfully created an admin account")
                        st.info("Go to Admin Login Menu to login")
                    else:
                        st.error("Failed to create account. Please try again.")
                else:
                    st.warning("Please fill out all fields.")

        elif admin_choice == "Admin Dashboard":
            if 'logged_in' in st.session_state and st.session_state['logged_in']:
                user = st.session_state['user']
                if user[3] == 'admin':
                    st.subheader("Admin Dashboard")
                    st.subheader("Create Tournament")
                    tournament_name = st.text_input("Tournament Name")
                    tournament_details = st.text_area("Tournament Details")
                    if st.button("Create Tournament"):
                        if create_tournament(conn, tournament_name, tournament_details):
                            st.success(f"Tournament {tournament_name} created successfully")
                        else:
                            st.error("Failed to create tournament. Please try again.")

                    st.subheader("Manage Tournaments")
                    tournaments = get_tournaments(conn)
                    for tournament in tournaments:
                        st.write("Tournament: ", tournament[1])
                        st.write("Details: ", tournament[2])
                        new_name = st.text_input(f"New name for {tournament[1]}", key=f"name_{tournament[0]}")
                        new_details = st.text_input(f"New details for {tournament[1]}", key=f"details_{tournament[0]}")
                        if st.button(f"Update {tournament[1]}", key=f"update_{tournament[0]}"):
                            update_tournament(conn, tournament[0], new_name, new_details)
                            st.success(f"Updated {tournament[1]}")

                    st.subheader("Player Registrations")
                    player_registrations = get_player_registrations(conn)
                    if player_registrations:
                        df = pd.DataFrame(player_registrations, columns=["Player", "College", "Tournament"])
                        st.dataframe(df)
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Player Registrations as CSV",
                            data=csv,
                            file_name='player_registrations.csv',
                            mime='text/csv',
                        )
                    else:
                        st.write("No player registrations found.")
                else:
                    st.warning("You are not authorized to view this page")
            else:
                st.warning("Please login first")

if __name__ == '__main__':
    main()