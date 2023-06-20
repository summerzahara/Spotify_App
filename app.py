from flask import Flask, render_template, session, redirect, url_for, request
from dotenv import load_dotenv
import spotipy, os, time
from spotipy.oauth2 import SpotifyOAuth



app = Flask(__name__)
app.debug = True
app.config["SESSION_NAME"] = "Spotify_Session"
app.secret_key = os.getenv("app_secret_key")
token_pass = os.getenv("token_pass")

load_dotenv()

@app.route("/")
def login():
    auth_url = my_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

# Redirect URI
@app.route("/uri")
def redirect_uri():
    session.clear()
    code = request.args.get("code")
    token_info = my_spotify_oauth().get_access_token(code)
    session[token_pass] = token_info
    return redirect(url_for("spotify_favs", external=True))

#RenderResults
@app.route("/spotifyfavs")
def spotify_favs():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    
    sp = spotipy.Spotify(auth=token_info["access_token"])
    top_tracks = sp.current_user_top_tracks(10,0,"short_term")
    for track in top_tracks['items']:
        print('track    : ' + track['name'])
        print('audio    : ' + track['preview_url'])
        print('cover art: ' + track['album']['images'][0]['url'])
        print()
    return render_template("index.html", top_tracks=top_tracks)

#Get session token
def get_token():   
    token_info = session.get(token_pass, None)
    if not token_info:
        redirect(url_for("login", external=False))
    now = int(time.time())
    is_expired = token_info["expires_at"] - now < 60
    if(is_expired):
        spotify_oauth = my_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info["refesh_token"])
    return token_info

#get oauth credentials for dotenv file
def my_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("client_id"),
        client_secret = os.getenv("client_secret"),
        redirect_uri = url_for('redirect_uri', _external= True),
        scope = os.getenv("scope")
    )


if __name__ == "__main__":
    app.run(debug=True)