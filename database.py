import sqlite3 as s
import time, uuid
from models import *

# Create a new session and save to database. This is called when a user is redirected
# back after verifying with Twitter.
# As well as storing the session (to keep track of current question, etc.),
# also store the user information.
# This 'session' represents a user answering the questions, and is used
# in case a particular user has multiple attempts.
def createSession(user):
    con, c = connect()
    timestamp = time.time()
    session_id = str(uuid.uuid4())
    question = 0
    c.execute("INSERT INTO session VALUES('"+str(session_id)+"',"+str(timestamp)+","+str(question)+")")
    
    # Turn verified status into integer for storage (0=false,1=true)
    verified = 0
    if user.verified:
        verified = 1

    c.execute("INSERT INTO user VALUES(?,?,?,?,?,?,?,?,?,?,?)", [str(session_id), user.id, user.screen_name, user.name, user.profile_image_url, user.friends_count, user.followers_count, user.statuses_count, user.favourites_count, user.listed_count, verified])
    con.commit()
    
    s = Session(session_id, user, timestamp)
    return s

# Return the session given by the sess_id
# Session contains the user represented by the session
def getSession(sess_id):
    con, c = connect()
    r1 = c.execute("SELECT * FROM session WHERE session_id='"+str(sess_id)+"'").fetchone()
    r = c.execute("SELECT * FROM user WHERE session_id='"+str(sess_id)+"'").fetchone()
    user = User(r['user_id'],r['name'],r['username'],r['profile_image'],r['friend_count'],r['follower_count'],r['statuses_count'],r['favourites_count'],r['listed_count'],r['verified'])
    sess = Session(sess_id,user,r1['timestamp'])
    return sess

# Get the current question for this user's session.
# e.g. a session last opened question 3, then the int 3 will be returned.
# Useful if user navigates away and returns.
def getQuestionNumber(sess):
    con, c = connect()
    row = c.execute("SELECT question FROM session WHERE session_id='"+sess.id+"'").fetchone()
    return int(row[0])


# Save a new question's timeline to DB, incrementing the sessions current
# question by 1.
# Returns the number of the created question
def createQuestion(sess, timeline):
    con, c = connect()
    c.execute("UPDATE session SET question=question+1 WHERE session_id='"+str(sess.id)+"'")
    con.commit()
    question_num = getQuestionNumber(sess)

    myTimeline = Timeline() # make our timeline object
    for tweet in timeline:
        myTweet = Tweet(tweet.id,tweet.text,tweet.retweet_count,tweet.user,0)
        myTimeline.add_tweet(myTweet)

        # Turn verified status into integer for storage (0=false,1=true)
        verified = 0
        if tweet.user.verified:
            verified = 1
        
        c.execute("INSERT INTO timeline VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                [sess.id,question_num,tweet.id,tweet.text,tweet.retweet_count,tweet.user.id,
                tweet.user.screen_name,tweet.user.profile_image_url,
                tweet.user.name,tweet.user.followers_count,tweet.user.friends_count,
                verified,tweet.user.statuses_count,tweet.user.favourites_count,
                tweet.user.listed_count,0])
    con.commit()

    q = Question(sess,question_num,myTimeline)
    return q

# Get the timeline for a given session's question. Will return the stored
# answers if the question had previously been asked already.
def getTimeline(sess, question_num):
    con, c = connect()
    result = c.execute("SELECT * FROM timeline WHERE session_id='"+str(sess.id)+"'and question="+str(question_num)).fetchall()

    timeline = Timeline()
    for row in result:
        user = User(row['user_id'],row['user_name'],row['user_username'],row['user_profile_image'],row['user_friends'],row['user_followers'],row['user_statuses_count'],row['user_favourites_count'],row['user_listed_count'],row['user_verified'])
        tweet = Tweet(row['tweet_id'],row['tweet_text'],row['tweet_retweet_count'],user,row['selected'])
        timeline.add_tweet(tweet)
    return timeline
    
# Update which Tweets of the timeline have been selected as interesting by the user   
# Accepts dict consisting of tweet_id => selected(0,1)
def updateTimeline(sess,question,selected):
    try:
        con, c = connect()
        for tweet in selected:
            c.execute("UPDATE timeline SET selected="+str(selected[tweet])+" WHERE session_id="+str(sess.id)+" AND question="+str(question.number)+" AND tweet_id="+str(tweet))
        con.commit()
    except:
        return False
    return True 
        

# Manage the connect to the database and return the connection
# and cursor objects
def connect():
    con = s.connect("static/data/twinterest.db")
    con.row_factory = s.Row
    c = con.cursor()
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
            follower_count INTEGER,
            statuses_count INTEGER,
            favourites_count INTEGER,
            listed_count INTEGER,
            verified INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS timeline(
            session_id TEXT,
            question INTEGER,
            tweet_id INTEGER,
            tweet_text TEXT,
            tweet_retweet_count INTEGER,
            user_id INTEGER,
            user_username INTEGER,
            user_profile_image TEXT,
            user_name TEXT,
            user_followers INTEGER,
            user_friends INTEGER,
            user_verified INTEGER,
            user_statuses_count INTEGER,
            user_favourites_count INTEGER,
            user_listed_count INTEGER,
            selected INTEGER)''')
    con.commit()
