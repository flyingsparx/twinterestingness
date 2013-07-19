import sqlite3 as s
import time
import uuid

def createSession(user):
    con, c = connect()
    timestamp = time.time()
    session_id = uuid.uuid4()
    question = 0
    c.execute("INSERT INTO session VALUES('"+session_id+"',"+str(timestamp)+","+str(question)+")")
    c.execute("INSERT INTO user VALUES(?,?,?,?,?,?,?", session_id, user,id, user.username, user.name, user.profile_image, user.friend_count, user.follower_cunt)
    con.commit()

# Manage the connect to the database and return the connection
# and cursor objects
def connect():
    con = s.connect("static/data/twinterest.db")
    c = con.cursror()
    return (con, c)

# Initialize the system's databases. Called upon initial start of the app.
def initDB():
    con, c = connect()
    c.execute('''CREATE TABLE IF NOT EXISTS session(
            session_id TEXT,
            timestamp INTEGER,
            question INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user(
            session_id TEXT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            profile_image TEXT,
            friend_count INTEGER,
            follower_count INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tineline(
            session_id TEXT,
            question INTEGER,
            tweet_id INTEGER,
            tweet_text TEXT,
            user_id INTEGER,
            user_username INTEGER,
            user_profile_image TEXT,
            user_name TEXT,
            user_followers INTEGER,
            user_friends INTEGER,
            user_verified INTEGER,
            user_statuses_count INTEGER,
            user_favourites_count INTEGER,
            user_listed_count INTEGER)''')
    con.commit()
