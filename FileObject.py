import music_tag as mt
import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials as SCC
class FileObject:
    client_credentials_manager = SCC(client_id=config.client_id,
                                    client_secret=config.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def __init__(self,filename):
        #set default to false just incase it doesnt read
        self.filename = filename
        self.searching_name = ""
        self.genres = None
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
            artist = self.song['artist'].value.split('feat.')[0].split(',')[0].split('&')[0].strip()
            track_num = self.song['tracknumber']
            self.searching_name = "{artist}".format(
                    artist=artist)
            if genre is None or genre == "":
                genre_message = ""
            else:
                genre_message = "The genre is {}".format(genre)
            print('The track number is {track_num} and the track name is {tracktitle} by {artist}. {genre}'  .format(
                track_num=track_num, tracktitle=name, artist=artist, genre=genre_message))

    def check_file_loaded(self):
        if not self.failed_to_read:
            print("The filename: {} was unable to be processed".format(self.filename))
            return False
        return True
    def set_genre(self):
        if self.check_file_loaded() and self.genres is not None:
            #set example genre
            self.song['genre'] = self.genres
            self.song.save()
    def get_genre(self):
        if self.check_file_loaded():
            results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                                           type='artist')
            self.genres = results['artists']['items'][0]['genres']
            print(self.genres)
