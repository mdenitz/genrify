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
        self.genres = "" 
        self.failed_to_read = False 
        self.song = self.get_mt_object(filename)
    
    def get_mt_object(self,file):
        try:
            song = mt.load_file(file)
            self.failed_to_read = True
            return song
        except:
            
            error_message = "The filename: {} was unable to be processed".format(self.filename)
            self.log("error_log.txt", error_message)
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
                genre_message = "Genre couldn't be found"
                self.genres = ""
            else:
                genre_message = "The genre is {}".format(genre)
            print('The track number is {track_num} and the track name is {tracktitle} by {artist}. {genre}'  .format(
                track_num=track_num, tracktitle=name, artist=artist, genre=genre_message))

    def check_file_loaded(self):
        if not self.failed_to_read:
            return False
        return True
    def set_genre(self):
        if self.check_file_loaded() and self.genres != "":
            #set example genre
            self.song['genre'] = self.genres
            self.song.save()
    def get_genre(self):
        if self.searching_name == "":
            no_artist_msg = "NO_ARTIST: No artist was found for filename: {filename}\n".format(filename=self.filename)
        elif self.check_file_loaded():
            try:
                results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                                               type='artist',limit=1)
                if results['artists']['items'] == []:
                    raise ValueError("Artist not found on Spotify API") 
                genres = results['artists']['items'][0]['genres']
                if genres == []:
                    no_genre_message = "NO_GENRE: No genre was found on the Spotify API for {artist}\n".format(artist=self.searching_name)
                    self.log("missing_data.txt",no_genre_message)
                    return
                self.genres = " ".join(genre.capitalize() for genre in genres[0].split())
            except Exception as e:
                self.genres = ""
                error_message = "Filename: {filename}, Artist: {artist}, Genres: {genres} error: {e}\n".format(
                        filename=self.filename,artist=self.searching_name,genres=genres,e=str(e))
                self.log("error_log.txt",error_message)
    def log(self,filename,message):
        f = open(filename, "a+")
        f.write(str(message))
        f.close()
