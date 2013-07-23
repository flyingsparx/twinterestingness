import tweepy
import os
from models import *

# Load the application's consumer token and secret from 
# environment variables.
CONSUMER_TOKEN = os.environ.get('twinteresting_token')
CONSUMER_SECRET = os.environ.get('twinteresting_secret')

## AUTHORISATION METHODS ##

# Get the OAuth authorisation URL from Twitter. Users taking
# part in the experiment will be redirected here to authenticate
# with Twitter before being re-sent back to our callback() endpoint.
def getAuthURL():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    redirect_url = None
    try:
        redirect_url = auth.get_authorization_url()
    except:
        print "Error getting auth URL"
    return (auth, redirect_url)

# Generate the access_token from the verifier sent back from Twitter
# to callback(). This is the final stage of the OAuth authorisation
# and returns the access token key and secret to be stored in the
# user's session.
def getAccessToken(verifier, request_key, request_secret):
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_request_token(request_key, request_secret)
    try:
        auth.get_access_token(verifier)
    except:
        print "Error getting access token"
    return (auth.access_token.key, auth.access_token.secret)

# Generate an authenticated API instance with the access_token
# stored in the user's session.
def getAuthenticatedAPI(session):
    key = session['access_key']
    secret = session['access_secret']
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(key, secret)
    return tweepy.API(auth)

def getMyAuthenticatedAPI():
    key = os.environ.get('twinterest_access_token_flyingsparx')
    secret = os.environ.get('twinterest_access_secret_flyingsparx')
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(key, secret)
    return tweepy.API(auth)    

## TWITTER API METHODS ##

# Get a representation of the User who has logged in
def getDetails(session):
#    api = getAuthenticatedAPI(session)
    api = getMyAuthenticatedAPI()
    user = api.verify_credentials()
    return user

# Get the authenticated user's home timeline (Tweets from self and friends)
def getHomeTimeline(session):
    print "\nHere\n"
#    api = getAuthenticatedAPI(session)
    api = getMyAuthenticatedAPI()
    timeline = api.home_timeline()
    for tweet in timeline:
        words = []
        tokens = tweet.text.split(" ")
        for token in tokens:
            word = ""
            if token.startswith("http"):
#                word = '<a href="'+token+'">'+token+'</a>'
                word = '<span class="link">'+token+'</span>'
            elif token.startswith("@"):
#                word = '<a href="https://twitter.com/'+token.replace("@","")+'">'+token+'</a>'
                word = '<span class="link">'+token+'</span>'
            elif token.startswith("#"):
#                word = '<a href="https://twitter.com/search?q=%23'+token.replace("#","")+'&src=hash">'+token+'</a>'
                word = '<span class="link">'+token+'</span>'
            else:
                word = token
            words.append(word)
        tweet.display_text = " ".join(words)
    return timeline


## UTILITY METHODS AND CLASSES ##

# Create and return a User object based on the details stored in
# the user's session variables.
#def generateUserFromSession(session):
#    name = session['name']
#    screen_name = session['screen_name']
#    profile_image = session['profile_image']
#    friends_count = session['friends_count']
#    user = User(name, screen_name, profile_image, friends_count)
#    return user

def getTimelineForQuestion(question, session):
    if int(question) == 1:
        return getHomeTimeline(session)
    else:
        return None
