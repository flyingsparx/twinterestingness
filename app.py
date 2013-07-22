from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import json, urllib2, sqlite3, os, time, datetime
import twitter_utils as utils
import database
from models import *

app = Flask(__name__)
app.secret_key = os.environ.get('TWINTEREST_SECRET_KEY')
database.initDB()

# On every request, check if user is logged in.
# If so, generate a global user object from the user's session
@app.before_request
def before_request():
    if 'access_key' in session:
        try:
            g.sess = database.getSession(session['id'])
            g.user = g.sess.user

        except:
            g.user = None
            g.sess = None
    else:
        g.user = None
        g.sess = None

# Root for twinterest.flyingsparx.net
# if user variable set, show standard homepage.
# else, create a Twitter OAuth URL and send this to the homepage.
@app.route("/")
def home():
    if not g.user == None:
           return render_template('home.html',  user=g.user)
    else:
        auth, authUrl = utils.getAuthURL()
        # set request token key and secret in the session variables so we
        # can get them later:
        session['request_token_key'] = auth.request_token.key
        session['request_token_secret'] = auth.request_token.secret
        return render_template('home.html', auth = authUrl, user = g.user)

# Return function when redirected by Twitter back to application.
# If verifier is set, use request tokens and verifier to create a
# Twitter OAuth access token, remove the request token from the session
# variables and replace them with the access token.
# If verifier not set, redirect back home unauthenticated.
@app.route("/callback")
def callback():
    # Check verifier exists...
    verifier = request.args['oauth_verifier']
    if verifier is None:
        return redirect(url_for('home'))
    
    # If it does, get the request key and token and generate an access token:
    request_key = session['request_token_key']
    request_secret = session['request_token_secret']
    access_token = utils.getAccessToken(verifier, request_key, request_secret)

    # Request information on the authorised user:
    user = utils.getDetails(session)
    # Create a 'session' instance for this user and save the user details:
    sess = database.createSession(user)

    # Remove request token info and replace with access token and our session  info
    session.pop('request_token_key')
    session.pop('request_token_secret')
    session['access_key'] = access_token[0]
    session['access_secret'] = access_token[1]
    session['id'] = sess.id
    
    return redirect(url_for('home'))


# /question/<question_id>
# Listen for requests to a specific question.
# If not logged in, redirect back home:
@app.route("/question/<q>/")
def question(q):
    if not g.user == None:
        try:
            requested_question = int(q)
        except:
            return redirect(url_for('home'))

        on_question = database.getQuestionNumber(g.sess)
        if requested_question > on_question:
            timeline = database.getTimeline(g.sess, on_question)
        if requested_question <= on_question:
            timeline = database.getTimeline(g.sess, requested_question)
        if requested_question == (on_question+1):
            timeline = utils.getTimelineForQuestion(requested_question, session)
            requested_question = database.createQuestion(g.sess, timeline)

        return render_template("question.html", user=g.user, timeline = timeline, question = requested_question)
        

# /api/update-question (Asynchronous / API calls only):
# Requests to POST data updates for questions.
# Return JSON as requests to this will be made asynchronously:
@app.route("/api/update-question/<q>/")
def api(q):
    if not g.user == None:  
        try:
            q = int(q)
            if q > database.getQuestionNumber(g.sess):
                raise Exception
        except:
            return json.dumps({"error":1,"info":"Invalid question"})
        
        # First, get list of all Tweets and a list of selections (0 or 1)
        # (Assumes same order for both!):
        tweet_ids = request.form["tweet_ids"].split(",")
        selected = request.form["selected"].split(",")
        combined_dict = {}
        for i, tweet_id in enumerate(tweet_ids):
            combined_dict[int(tweet_id)] = int(selected[i])

        outcome = database.updateTimeline(g.sess, q, combined_dict)
        if outcome == False:
            return json.dumps({"error":1,"info":"Error storing details"})
        return json.dumps({"error":0})


# /cookies:
# Display a cookie information page:
@app.route("/cookies/")
def cookies():   
    return render_template('cookies.html', user=g.user)


# /logout:
# Pop the access token variables from the session and redirect back home:
@app.route("/logout/")
def logout():
    session.pop('access_key')
    session.pop('access_secret')
    session.pop('id')
    return redirect(url_for('home'))


##
## MAIN APPLICATION CODE
##

# Handle error logging. 
# Necessary since it's awkward testing Twitter interactions (callbacks,
# authorisation, etc.) on ports other than 80 (i.e. in developnent mode)
if app.debug is not True:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('python.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
