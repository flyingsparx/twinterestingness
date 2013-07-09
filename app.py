from flask import Flask, url_for, render_template, request, session, escape, redirect
import json, urllib2, sqlite3, os, time, datetime

app = Flask(__name__)

@app.route("/")
def home():
    return 'Homepage'

# Main code
if __name__ == '__main__':
    app.debug = True 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
