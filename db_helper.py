import mysql.connector
from mysql.connector import Error
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",  # password thingy
    "database": "math_arena_db"
}
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        conn.close()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(50) NOT NULL,
            high_score INT DEFAULT 0,
            games_played INT DEFAULT 0
        )""")
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print("DB Init Error:", e)
        return False

def register_player(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM players WHERE username = %s", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already taken!"
        cursor.execute("INSERT INTO players (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        return True, "Account Created Successfully!"
    except Error as e:
        return False, str(e)

def login_player(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, high_score FROM players WHERE username = %s", (username,))
        res = cursor.fetchone()
        conn.close()
        if res and res[0] == password:
            return True, res[1]
        return False, 0
    except Error:
        return False, 0

def save_score(username, score):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE players 
            SET games_played = games_played + 1,
                high_score = GREATEST(high_score, %s)
            WHERE username = %s
        """, (score, username))
        conn.commit()
        cursor.execute("SELECT high_score FROM players WHERE username = %s", (username,))
        high = cursor.fetchone()[0]
        conn.close()
        return high
    except Error as e:
        print("Save error:", e)
        return score