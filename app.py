from flask import Flask,render_template,request
import requests
import asyncio
import sqlite3
import base64
import os
import pprint




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


def formatData(t,s):
    if not isinstance(t,dict) and not isinstance(t,list):
        print("\t"*s+str(t))
    else:
        for key in t:
            print("\t"*s+str(key))
            if not isinstance(t,list):
                formatData(t[key],s+1)


@app.route('/')
async def hello():
    conn = get_db_connection("database")
    cur = conn.cursor()

    


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

        

        artist = artist.json()["artist_name"]
        album = album.json()["album_name"]
        song = song.json()["song_name"]
        album_cover_url = album_cover_url.json()["album_cover_url"]

        formatted_album_name = write_image(album_cover_url,album)
        album_cover = convertToBinaryData(formatted_album_name)

        # must be everything AFTER the last slash in the share link
        encode_url = "301e8VN6F6t9EmGM41boaN?si=efa5797342df48b1"
        pprint.pprint(requests.get(f"http://127.0.0.1:8000/api/get_playlist/songs/{encode_url}/songs").json())
        
       

        if(cur.execute("SELECT * FROM songs WHERE song=?", (song,)).fetchone() != None):
            string = cur.execute("""SELECT album_cover FROM songs WHERE song = ? """,(song,)).fetchall()[0][0]
            base64_encoded_image = base64.b64encode(string).decode("utf-8")
            review = cur.execute("SELECT review FROM songs WHERE song=?", (song,)).fetchall()

            # this updates the play count each time the page is reloaded and the song exists in the database
            # not ideal, but too lazy to deal with it, pretty garbage
            # TODO: implement "Recently Listend" so we can check if the songn playing is new, then we only add if that song is new
            
            cur.execute("""UPDATE songs
                        SET plays = plays + 1
                        WHERE song = ?
                        """,(song,))

            #
            

            plays = cur.execute("""SELECT plays FROM songs WHERE song = ?""",(song,)).fetchone()[0]


            conn.commit()
            conn.close()
            return render_template("index.html",artist=artist,album=album,song=song,album_cover=base64_encoded_image,review=review[0][0],plays=plays)
        
        

        cur.execute("""INSERT INTO songs(album,artist,song,album_cover,review,plays)
                        SELECT ?,?,?,?,"There is currently no review",1
                        WHERE NOT EXISTS(SELECT 1 FROM songs WHERE song = ?);
                        """, (album, artist, song, album_cover,song))

        plays = cur.execute("""SELECT plays FROM songs WHERE song = ?""",(song,)).fetchone()[0]

        # make a call to a db to get the review for the db, if there is none, return a string "No review written yet"
        

        review = cur.execute("SELECT review FROM songs WHERE song=?", (song,)).fetchall()

        string = cur.execute("""SELECT album_cover FROM songs WHERE song = ? """,(song,)).fetchall()[0][0]
        base64_encoded_image = base64.b64encode(string).decode("utf-8")



        conn.commit()
        conn.close()

        # need to start pulling pictures/data from database
        return render_template("index.html",artist=artist,album=album,song=song,album_cover=base64_encoded_image,review=review[0][0],plays=plays)
    else:
        
        return render_template("nothing_playing.html") 

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open("static/images/" + filename, 'rb') as file:
        blobData = file.read()
        os.remove("static/images/" + filename)
    return blobData

@app.route('/review/<string:song>')
def review(song):
    return render_template("submit_review.html",song=song.replace("_", " "))

@app.route('/submit_review',methods=['POST'])
def submit_review():
    
    response = dict(request.get_json())
    print(response)
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


@app.route('/artist_profile/<string:artist>')
def artist_profile(artist):
    conn = get_db_connection("database")
    cur = conn.cursor()

    songs = []

    data = cur.execute("SELECT song,plays FROM songs WHERE artist=? ORDER BY plays DESC", (artist,))
    data = data.fetchall()
    
    for row in data:
        songs.append({"song" : row[0],"plays" : row[1]})

    conn.commit()
    conn.close()


    return render_template("artist_profile.html",artist=artist,songs=songs)

if __name__ == "__main__":
    app.run(port=8999, debug=True)