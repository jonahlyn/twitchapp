import sys
from flask import Flask, render_template, url_for, session, flash, redirect, jsonify
from flask_oauthlib.client import OAuth
from config import DevelopmentConfig
from functools import wraps
import requests


# Configure the application
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


# Authentication configuration
oauthapp = OAuth(app)
twitch = oauthapp.remote_app(
    'twitch',
    consumer_key=app.config['TWITCH_KEY'],
    consumer_secret=app.config['TWITCH_SECRET'],
    base_url='https://api.twitch.tv/kraken/',
    request_token_url=None,
    request_token_params={'scope': ["user_read", "channel_check_subscription"]},
    access_token_url='https://api.twitch.tv/kraken/oauth2/token',
    authorize_url='https://api.twitch.tv/kraken/oauth2/authorize',
    access_token_method='POST',
)


#########################
# Public routes
#########################

@app.route('/')
def index():
    return render_template('index.html', title="Welcome")


#########################
# Authorization routes
#########################

@twitch.tokengetter
def get_twitch_token():
    if 'twitch_oauth' in session:
        return session.get('twitch_oauth')


def change_twitch_header(uri, headers, body):
    """
    Modifies the request header before the request is made to the Twitch api.
    """
    # todo: Does the new twitch api still require this? It seems to work.
    auth = headers.get('Authorization')
    if auth:
        auth = auth.replace('Bearer', 'OAuth')
        headers['Authorization'] = auth

    # Append the client id to the end of the url.
    # todo: can this be done as part of the configuration
    url = uri + "?client_id=" + app.config['TWITCH_KEY']

    return url, headers, body

twitch.pre_request = change_twitch_header


def validate_token():
    """
    Required by twitch: https://dev.twitch.tv/docs/authentication#if-you-use-twitch-for-login-to-your-app-you-must-validate-every-request
    Submits a request to the Twitch root URL. Response should include status of token.

    Usage:
    returns None on fail, user name on success
    """
    r = twitch.get(twitch.base_url)
    #assert app.debug == False

    if(r.data['token']['valid'] == True):
        return jsonify(r.data['token']['user_name'])


def authorized(fn):
    """
    Decorator that checks if the user is authenticated.

    Usage:
    @app.route("/")
    @authorized
    def secured_root(userid=None):
        pass
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if 'twitch_oauth' not in session:
            # Access token was not found in the session
            flash('Please log in to continue')
            return render_template('index.html', title="Unauthorized", content=""), 401

        userid = validate_token()
        if userid is None:
            # Token is no longer valid
            flash('Please log in to continue')
            return render_template('index.html', title="Unauthorized"), 401

        return fn(*args, **kwargs)
    return decorated_function
    

@app.route('/login')
def login():
    callback_url = url_for('oauthorized', _external=True) 
    return twitch.authorize(callback=callback_url or None)


@app.route('/logout')
def logout():
    session.pop('twitch_oauth', None)
    flash('You are now logged out')
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitch.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitch_oauth'] = resp
        flash('Successfully logged in.')
    return redirect(url_for('index'))


#########################
# Secured Routes
#########################

@app.route('/me')
@authorized
def getme():
    url = twitch.base_url
    r = twitch.get(url)
    return jsonify(r.data)


@app.route('/test')
@authorized
def test():
    return render_template('index.html', title="Test")




if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=443, ssl_context='adhoc', debug=True)
    app.run(host='0.0.0.0', port=80, debug=True)

