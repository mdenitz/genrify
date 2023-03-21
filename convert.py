from FileObject import FileObject 
import os
import requests
class Library:
    def __init__(self, foldername):
        self.FileObjects= []
        self.folderName = foldername
        self.get_objects()
    def get_objects(self):
        directory = self.folderName
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".mp3"):
                #print("filename: {filename}, directory: {directory}".format(
                #filename=filename, directory=directory))
                path = os.path.join(directory, filename)
                current_song = FileObject(path)
                self.FileObjects.append(current_song)
                break
    def print_objects(self):
        for song in self.FileObjects[:5]:
            song.get_song_data()
        
    def fetch(self):
        #Gets the current Libary
        #gets list of song objects
        pass
    
    def get_genre(self):
        first_obj = self.FileObjects[0]
        
    def get_track_id(self):
        first_obj = self.FileObjects[0]
        #print(first_obj.searching_name)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        url = "https://www.chosic.com/api/tools/search?q={search_name}&type=track&limit=1".format(
                search_name="righteous juice wrld")
        response = requests.get(url,headers=headers)
        print(response.status_code, response.url)


#example_file = r"/Users/mrdenitz/Downloads/songs_downloaded_1879/01 Goodmorning.mp3"
#example = FileObject(example_file)
#example.get_song_data()
#example.set_genre("Rapss")
#example.get_song_data()
#
example_folder = str("/Users/mrdenitz/Downloads/songs_downloaded_1879/")
lib = Library(example_folder)
lib.print_objects()
#lib.get_track_id()
