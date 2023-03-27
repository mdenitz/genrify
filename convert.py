from FileObject import FileObject 
import os
class Library:
    def __init__(self, foldername,overwrite,optional_count=-1):
        self.FileObjects= []
        self.folderName = foldername
        self.optional_count = optional_count
        self.existing_count = 0
        self.get_objects(overwrite)
    def get_objects(self,overwrite):
        directory = self.folderName
        direct_list = os.listdir(directory)
        if self.optional_count < 0:
            self.optional_count = len(direct_list)
        elif self.optional_count > len(direct_list):
            self.optional_count = len(direct_list)
        count = 0
        for idx,file in enumerate(direct_list): 
            if count >= self.optional_count:
                break
            filename = os.fsdecode(file)
            if filename.endswith(".mp3"):
                #print("filename: {filename}, directory: {directory}".format(
                #filename=filename, directory=directory))
                path = os.path.join(directory, filename)
                current_song = FileObject(path)
                if overwrite:
                    self.FileObjects.append(current_song)
                    count += 1
                elif not overwrite and current_song.genres == "":
                    self.FileObjects.append(current_song)
                    count += 1
                elif current_song.genres != "":
                    self.existing_count += 1             
    def print_songs(self):
        for song in self.FileObjects:
            song.print_song()
        
        
    def set_genres(self,loader):
        songs_changed = 0
        artist_nf = 0 
        for song in self.FileObjects:
            song.get_song_data()
            artist_nf += song.get_genre()
            songs_changed += song.set_genre()
            loader.message("{songs_changed}/{total} Converted. {issues} missing/errors".format(
                songs_changed=songs_changed,total=len(self.FileObjects),issues=artist_nf))

     
        return songs_changed, artist_nf 

    
    def chunks(self,lst,n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

