from flask import Flask,render_template
import requests
import asyncio
import sqlite3



app = Flask(__name__)

def write_image(album_url,album_name):
        img_data = requests.get(album_url).content
        album_name = album_name.replace(" ","").replace("/","_")
        image_file_name = f"{album_name}.jpg"
        with open(f"static/images/{image_file_name}", 'wb') as handler:
            handler.write(img_data)
        
        return album_name

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    


@app.route('/')
async def hello():
    if requests.get("http://127.0.0.1:8000/api/is_playing").json()["is_playing"] == True:
        loop = asyncio.get_event_loop()
        future1 = loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/current_artist')
        future2 = loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/current_album')
        future3 = loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/current_song')
        future4 = loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/current_album_cover_url')
        artist = await future1
        album = await future2
        song = await future3
        album_cover_url = await future4

        # TODO: add functionality for when the image is not avaliable or user is not play a song

        artist = artist.json()["artist_name"]
        album = album.json()["album_name"]
        song = song.json()["song_name"]
        album_cover_url = album_cover_url.json()["album_cover_url"]
        
        formatted_album_name = write_image(album_cover_url,album)
        
    
        # make a call to a db to get the review for the db, if there is none, return a string "No review written yet"
        connection = sqlite3.connect('database.db')
        cur = connection.cursor()
        review = cur.execute("SELECT review FROM reviews WHERE song=?", (song,)).fetchall()

        if(len(review) > 0):
            review = review[0][0]


        return render_template("index.html",artist=artist,album=album,song=song,album_cover_directory=f"static/images/{formatted_album_name}.jpg",review= "There is currently no review!" if len(review) == 0 else review)
    else:
        
        return render_template("nothing_playing.html") 

@app.route('/submit_review')
def submit_review():
    return render_template