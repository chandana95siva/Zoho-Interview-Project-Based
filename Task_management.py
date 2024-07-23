
import streamlit as st
import sqlite3
from hashlib import sha256
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('task_management.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            priority INTEGER,
            status TEXT,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES Projects(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES Tasks(id),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    ''')
    
    conn.commit()

def register_user(username, password, email):
    hashed_password = sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO Users (username, password, email) VALUES (?, ?, ?)", (username, hashed_password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, hashed_password))
    return cursor.fetchone()

def create_task(title, description, due_date, priority, status, project_id):
    cursor.execute("INSERT INTO Tasks (title, description, due_date, priority, status, project_id) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, description, due_date, priority, status, project_id))
    conn.commit()

def update_task(task_id, title, description, due_date, priority, status, project_id):
    cursor.execute("UPDATE Tasks SET title = ?, description = ?, due_date = ?, priority = ?, status = ?, project_id = ? WHERE id = ?",
                   (title, description, due_date, priority, status, project_id, task_id))
    conn.commit()

def delete_task(task_id):
    cursor.execute("DELETE FROM Tasks WHERE id = ?", (task_id,))
    conn.commit()

def main():
    st.title("Task Management Application")

    menu = ["Register", "Login", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        email = st.text_input("Email")
        if st.button("Register"):
            success = register_user(username, password, email)
            if success:
                st.success("Registered successfully!")
            else:
                st.error("Username already exists")

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")

    elif choice == "Dashboard":
        if not st.session_state.get('logged_in'):
            st.error("You need to log in first")
            return
        
        

        # Display tasks
        st.header("Tasks")
        tasks = cursor.execute("SELECT * FROM Tasks").fetchall()
        # if tasks:
        #     for task in tasks:
        #         st.write(f"**Title:** {task[1]}")
        #         st.write(f"**Description:** {task[2]}")
        #         st.write(f"**Due Date:** {task[3]}")
        #         st.write(f"**Priority:** {task[4]}")
        #         st.write(f"**Status:** {task[5]}")
        #         st.write(f"**Project ID:** {task[6]}")
        #         st.write("---")
        # else:
        #     st.write("No tasks available")

        # Task creation form
        st.header("Create a New Task")
        with st.form(key='create_task_form'):
            title = st.text_input("Title")
            description = st.text_area("Description")
            due_date = st.date_input("Due Date", min_value=datetime.today())
            priority = st.selectbox("Priority", [1, 2, 3])
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
            project_id = st.number_input("Project ID", min_value=1)
            submit_button = st.form_submit_button("Create Task")
            if submit_button:
                create_task(title, description, due_date, priority, status, project_id)
                st.success("Task created successfully!")

        # Task update form
        st.header("Update an Existing Task")
        with st.form(key='update_task_form'):
            task_id = st.number_input("Task ID to Update", min_value=1)
            title = st.text_input("New Title")
            description = st.text_area("New Description")
            due_date = st.date_input("New Due Date", min_value=datetime.today())
            priority = st.selectbox("New Priority", [1, 2, 3])
            status = st.selectbox("New Status", ["Not Started", "In Progress", "Completed"])
            project_id = st.number_input("New Project ID", min_value=1)
            update_button = st.form_submit_button("Update Task")
            if update_button:
                update_task(task_id, title, description, due_date, priority, status, project_id)
                st.success("Task updated successfully!")

        # Task deletion form
        st.header("Delete a Task")
        with st.form(key='delete_task_form'):
            task_id = st.number_input("Task ID to Delete", min_value=1)
            delete_button = st.form_submit_button("Delete Task")
            if delete_button:
                delete_task(task_id)
                st.success("Task deleted successfully!")

if __name__ == "__main__":
    create_tables()
    main()
