import music_tag as mt
class FileObject:
    def __init__(self,filename):
        #set default to false just incase it doesnt read
        self.filename = filename
        self.searching_name = ""
        self.failed_to_read = False 
        self.song = self.get_mt_object(filename)
    
    def get_mt_object(self,file):
        try:
            song = mt.load_file(file)
            self.failed_to_read = True
            return song
        except:
            print("An error occured")
            return None
    def get_song_data(self):
        if self.check_file_loaded():
            genre = self.song['genre'].value
            name = self.song['tracktitle']
            artist = self.song['artist']
            track_num = self.song['tracknumber']
            self.searching_name = "{name} {artist}".format(
                    name=name,artist=artist)
            if genre is None or genre == "":
                genre_message = ""
            else:
                genre_message = "The genre is {}".format(genre)
            print('The track number is {track_num} and the track name is {tracktitle}. {genre}'  .format(
                track_num=track_num, tracktitle=name, genre=genre_message))

    def check_file_loaded(self):
        if not self.failed_to_read:
            print("The filename: {} was unable to be processed".format(self.filename))
            return False
        return True
    def set_genre(self,genre):
        if self.check_file_loaded():
            #set example genre
            self.song['genre'] = genre
            self.song.save()


