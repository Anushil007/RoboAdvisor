import sqlite3

def create_users_table():
    # Connect to database
    conn = sqlite3.connect('mydatabase.db')

    # Create a cursor object
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE users
                 (age INTEGER,
                  income INTEGER,
                  experience INTEGER,
                  horizon INTEGER,
                  risk TEXT,
                  style TEXT,
                  products TEXT,
                  updates INTEGER)''')

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()

def insert_user(age, income, experience, horizon, risk, style, products, updates):
    # Connect to database
    conn = sqlite3.connect('mydatabase.db')

    # Create a cursor object
    c = conn.cursor()

    
    # Get the selected products as a list and join them into a string
    product_str = ','.join(products)

    # Insert data into table
    c.execute('INSERT INTO users (age, income, experience, horizon, risk, style, products, updates) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (age, income, experience, horizon, risk, style, product_str, updates))

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()
