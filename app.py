from flask import Flask, url_for, render_template, request, session, escape, redirect
import json, urllib2, sqlite3, os, time, datetime
import utils

app = Flask(__name__)
app.secret_key = os.environ.get('TWINTEREST_SECRET_KEY')

@app.route("/")
def home():
    if 'access_key' in session:
        user = utils.generateUserFromSession(session)
        return render_template('home.html', logged = True, user=user)
    else:
        auth, authUrl = utils.getAuthURL()
        session['request_token_key'] = auth.request_token.key
        session['request_token_secret'] = auth.request_token.secret
        return render_template('home.html', auth = authUrl, logged = False)

@app.route("/callback")
def callback():
    verifier = request.args['oauth_verifier']
    request_key = session['request_token_key']
    request_secret = session['request_token_secret']
    access_token = utils.getAccessToken(verifier, request_key, request_secret)
    # Remove request token info and replace with access token info
    session.pop('request_token_key')
    session.pop('request_token_secret')
    session['access_key'] = access_token[0]
    session['access_secret'] = access_token[1]

    # Also store some user info in the session 
    user = utils.getDetails(session)
    session['screen_name'] = user.screen_name
    session['profile_image'] = user.profile_image_url
    session['name'] = user.name
    session['friends_count'] = user.friends_count
    return redirect(url_for('home'))

@app.route("/logout/")
def logout():
    session.pop('access_key')
    session.pop('access_secret')
    return redirect(url_for('home'))



# Main code
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
