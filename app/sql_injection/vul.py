import sqlite3

# Sample database setup
def setup_database():
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'password123')")
    conn.commit()
    conn.close()

# Vulnerable login function
def vulnerable_login(username, password):
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    # Unsafe SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing Query: {query}")
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result

# Demonstrate SQL Injection
if __name__ == "__main__":
    setup_database()
    print("### Vulnerable Login ###")
    # SQL Injection attempt
    injected_username = "' OR '1'='1"
    injected_password = "' OR '1'='1"
    user = vulnerable_login(injected_username, injected_password)
    if user:
        print("Login successful! User:", user)
    else:
        print("Login failed.")
