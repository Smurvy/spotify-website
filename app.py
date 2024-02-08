from flask import Flask,render_template,request
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
        
        return image_file_name

def get_db_connection(name_db):
    conn = sqlite3.connect(f'{name_db}.db')
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
        album_cover = convertToBinaryData(formatted_album_name)

        conn = get_db_connection("database")
        cur = conn.cursor()





        cur.execute("""INSERT INTO songs(album,artist,song,album_cover,review)
                        SELECT ?,?,?,?,"There is currently no review"
                        WHERE NOT EXISTS(SELECT 1 FROM songs WHERE song = ?);
                        
                        
                        
                        
                        """, (album, artist, song, album_cover,song,))

        # make a call to a db to get the review for the db, if there is none, return a string "No review written yet"

        review = cur.execute("SELECT review FROM songs WHERE song=?", (song,)).fetchall()

        






        if(len(review) > 0):
            review = review[0][0]

        conn.commit()
        conn.close()

        # need to start pulling pictures/data from database
        return render_template("index.html",artist=artist,album=album,song=song,album_cover_directory=f"static/images/{formatted_album_name}",review= "There is currently no review!" if len(review) == 0 else review)
    else:
        
        return render_template("nothing_playing.html") 

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open("static/images/" + filename, 'rb') as file:
        blobData = file.read()
    return blobData

@app.route('/review/<string:song>')
def review(song):
    return render_template("submit_review.html",song=song.replace("_", " "))

@app.route('/submit_review',methods=['POST'])
def submit_review():
    response = dict(request.get_json())
    song = response["SendInfo"]["song"]["name"]
    review = response["SendInfo"]["review"]


    print(review)
    print(song)
    
    conn = get_db_connection("database")
    cur = conn.cursor()

    cur.execute("""UPDATE songs SET review = ? WHERE song = ?""", (review,song,))

    conn.commit()
    conn.close()

    return "SUCCESS"