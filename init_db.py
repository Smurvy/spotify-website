import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("""INSERT INTO reviews (song,rating,review) 
               VALUES ("Sunglasses", 5,"Very good")""")
connection.commit()
connection.close()