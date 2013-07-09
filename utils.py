import tweepy

CONSUMER_TOKEN = os.environ.get('twinteresting_token')
CONSUMER_SECRET = os.environ.get('twinteresting_secret')

def getAuthURL():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    redirect_url = None
    try:
        redirect_url = auth.get_authorization_url()
    except:
        print "Error getting auth URL"
    return redirect_url


