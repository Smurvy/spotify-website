import os
import os.path
import requests

current_directory = os.path.dirname(__file__)
parent_directory = os.path.split(current_directory)[0]
file_path = os.path.join(parent_directory, 'static', 'images')


def convert_to_binary_data(filename):
    image_path = os.path.join(file_path,filename)
    # Convert digital data to binary format
    with open(image_path, 'rb') as file:
        blobData = file.read()
        # cleannup after converted to blob data. Dont need to store data locally
        os.remove(image_path)
    return blobData


def write_image(album_url,album_name):
    img_data = requests.get(album_url).content
    album_name = album_name.replace(" ","").replace("/","_")
    image_file_name = f"{album_name}.jpg"
    image_path = os.path.join(file_path,image_file_name)
    
    with open(image_path, 'wb') as handler:
        handler.write(img_data)
    
    return image_file_name
    

def get_image_blob(album_cover_url,album):
    image_file = write_image(album_cover_url,album)
    album_cover_blob = convert_to_binary_data(image_file)
    return album_cover_blob