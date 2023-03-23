from FileObject import FileObject 
import os
import time
class Library:
    def __init__(self, foldername,optional_count=-1):
        self.FileObjects= []
        self.folderName = foldername
        self.optional_count = optional_count
        self.get_objects()
    def get_objects(self):
        directory = self.folderName
        direct_list = os.listdir(directory)
        if self.optional_count < 0:
            self.optional_count = len(direct_list)

        for file in direct_list[:self.optional_count]: 
            filename = os.fsdecode(file)
            if filename.endswith(".mp3"):
                #print("filename: {filename}, directory: {directory}".format(
                #filename=filename, directory=directory))
                path = os.path.join(directory, filename)
                current_song = FileObject(path)
                self.FileObjects.append(current_song)
    def print_objects(self):
        for song in self.FileObjects:
            song.get_song_data()
        
        
    def set_genres(self):
        for chunk in self.chunks(self.FileObjects,25):
            for song in chunk:
                song.get_genre()
                song.set_genre()
            time.sleep(3)
     

    
    def chunks(self,lst,n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

#example_file = r"/Users/mrdenitz/Downloads/songs_downloaded_1879/01 Goodmorning.mp3"
#example = FileObject(example_file)
#example.get_song_data()
#example.set_genre("Rapss")
#example.get_song_data()
#
example_folder = str("/Users/mrdenitz/Downloads/songs_downloaded_1879/")
lib = Library(example_folder,52)
print(len(lib.FileObjects))
#lib.print_objects()
lib.set_genres()
#lib.get_track_id()
print("-----")
print("Succesfully converted Genres! See log files for errors or missing data")
print("-----")
lib.print_objects()
