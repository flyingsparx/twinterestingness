from flask import Flask, url_for, render_template, request, session, escape, redirect, g
import json, urllib2, sqlite3, os, time, datetime
import utils

app = Flask(__name__)
app.secret_key = os.environ.get('TWINTEREST_SECRET_KEY')


# On every request, check if user is logged in.
# If so, generate a global user object from the user's session
@app.before_request
def before_request():
     if 'access_key' in session:
        try:
            g.user = utils.generateUserFromSession(session)
        except:
            g.user=None
     else:
#         g.user = None
         g.user = 1

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
    verifier = request.args['oauth_verifier']
    if verifier is None:
        return redirect(url_for('home'))
    request_key = session['request_token_key']
    request_secret = session['request_token_secret']
    access_token = utils.getAccessToken(verifier, request_key, request_secret)
    # Remove request token info and replace with access token info
    session.pop('request_token_key')
    session.pop('request_token_secret')
    session['access_key'] = access_token[0]
    session['access_secret'] = access_token[1]

    # Also store some user info in the session so that we can display
    # some relevant user info (without spamming the API)
    user = utils.getDetails(session)
    session['screen_name'] = user.screen_name
    session['profile_image'] = user.profile_image_url
    session['name'] = user.name
    session['friends_count'] = user.friends_count
    return redirect(url_for('home'))


# /question/<question_id>
# Listen for requests to a specific question.
# If not logged in, redirect back home:
@app.route("/question/<q>/")
def question(q):
    if not g.user == None:
        t = utils.getHomeTimeline(session)
        return render_template("question.html", user=g.user, timeline = t)
    else:
        return redirect(url_for('home'))


# /cookies:
# Display a cookie information page.
@app.route("/cookies/")
def cookies():   
    return render_template('cookies.html', user=g.user)


# /logout:
# Pop the access token variables from the session and redirect back home:
@app.route("/logout/")
def logout():
    session.pop('access_key')
    session.pop('access_secret')
    return redirect(url_for('home'))





# Main code (if invoked from Python at command line for development server)
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
