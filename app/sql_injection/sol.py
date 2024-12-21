import sqlite3

# Secure login function
def secure_login(username, password):
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()
    # Safe parameterized query
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    print(f"Executing Secure Query: {query}")
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

# Demonstrate Secure Query
if __name__ == "__main__":
    print("\n### Secure Login ###")
    # SQL Injection attempt
    injected_username = "' OR '1'='1"
    injected_password = "' OR '1'='1"
    user = secure_login(injected_username, injected_password)
    if user:
        print("Login successful! User:", user)
    else:
        print("Login failed.")
