# Importing Libraries
import streamlit as st
import pandas as pd
import sqlite3
import mysql

# Database connection
def get_connection():
    con = sqlite3.connect('Employee_database.db')
    cur = con.cursor()
    return con,cur

# create the table
def init_db():
    con,cur = get_connection()
    cur.execute("""CREATE TABLE IF NOT EXISTS Employees(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                manager_id INTEGER,
                FOREIGN KEY (manager_id) REFERENCES employees (id)
                );
                """)
    con.commit()

# Function to Add an Employee
def add_employee(name, department, position, manager_id):
    con,cur = get_connection()
    cur.execute('INSERT INTO Employees (name, department, position, manager_id) VALUES (?, ?, ?, ?)', 
              (name, department, position, manager_id))
    con.commit()

# Function to Update an Employee
def update_employee(emp_id, name, department, position, manager_id):
    con,cur = get_connection()
    cur.execute('UPDATE Employees SET name=?, department=?, position=?, manager_id=? WHERE id=?', 
              (name, department, position, manager_id, emp_id))
    con.commit()

# # Function to Delete an Employee
def delete_employee(emp_id):
    con,cur = get_connection()
    cur.execute('DELETE FROM Employees WHERE id=?', (emp_id,))
    con.commit()

# Function to Search the Employee
def search_employees(criteria, value):
    con,cur = get_connection()
    query = f"SELECT * FROM employees WHERE {criteria} LIKE ?"
    cur.execute(query, ('%' + value + '%',))
    return cur.fetchall()

# Function to display the reporting hierarchy
def get_hierarchy(emp_id, level=0, visited=None):
    con,cur = get_connection()
    if visited is None:
        visited = set()
    if emp_id in visited:
        return [('Circular Reference Detected', emp_id)]
    visited.add(emp_id)
    cur.execute('SELECT * FROM employees WHERE manager_id=?', (emp_id,))
    rows = cur.fetchall()
    hierarchy = []
    for row in rows:
        hierarchy.append(('  ' * level + row[1], row[0]))
        hierarchy.extend(get_hierarchy(row[0], level + 1, visited))
    return hierarchy

# Streamlit app layout
def main():
    st.header("EMPLOYEE RECORD MANAGEMENT SYSTEM")

# Navigation
menu =["Add Employee","Update Employee","Delete Employee","Search Employee","View Hierarchy"]
choice = st.sidebar.selectbox("Menu",menu)

# Initialize the database
init_db()

if choice == "Add Employee":
    st.subheader("Add Employee details")
    name = st.text_input('Name')
    department = st.text_input('Department')
    position = st.text_input('Position')
    manager_id = st.number_input('Manager ID', min_value=0)
    if st.button('Add Employee'):
        add_employee(name, department, position, manager_id)
        st.success('Employee added successfully')


elif choice == "Update Employee":
    st.subheader("Update the Employee details") 
    emp_id = st.number_input('Employee ID', min_value=1)
    name = st.text_input('Name')
    department = st.text_input('Department')
    position = st.text_input('Position')
    manager_id = st.number_input('Manager ID', min_value=0)
    if st.button('Update Employee'):
        update_employee(emp_id, name, department, position, manager_id)
        st.success('Employee updated successfully')   


elif choice == "Delete Employee":
    st.subheader("Delete the Employee details")
    emp_id = st.number_input('Employee ID', min_value=1)
    if st.button('Delete Employee'):
        delete_employee(emp_id)
        st.success('Employee deleted successfully')   


elif choice == "Search Employee":
    st.subheader("Search the Employee details")
    criteria = st.selectbox('Search By', ['name', 'department', 'position'])
    value = st.text_input('Search Value')
    if st.button('Search'):
        results = search_employees(criteria, value)
        df = pd.DataFrame(results, columns=['ID', 'Name', 'Department', 'Position', 'Manager ID'])
        st.dataframe(df)
    

elif choice == "View Hierarchy":
    st.subheader("view the hierarchy of Employee")
    emp_id = st.number_input('Employee ID', min_value=1)
    if st.button('Show Hierarchy'):
        hierarchy = get_hierarchy(emp_id)
        for name, emp_id in hierarchy:
            st.text(name)    


if __name__ == "__main__":
    main()    