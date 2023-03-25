import music_tag as mt
import spotipy
import config
from spotipy.oauth2 import SpotifyClientCredentials as SCC
class FileObject:
    client_credentials_manager = SCC(client_id=config.client_id,
                                             client_secret=config.client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def __init__(self,filename):
        #set default to false just incase it doesnt read
        self.filename = filename
        self.name = ""
        self.searching_name = ""
        self.genres = "" 
        self.failed_to_read = False 
        self.mt_object = self.get_mt_object(filename)
        self.get_song_data()
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
            genre = self.mt_object['genre'].value
            self.name = self.mt_object['tracktitle']
            artist = self.mt_object['artist'].value.split('feat.')[0].split(',')[0].split('&')[0].strip()
            track_num = self.mt_object['tracknumber']
            self.searching_name = "{artist}".format(
                    artist=artist)
            if artist is None or artist == "":
                raise ValueError("Artist not found for Filename: {filename}".format(
                    filename =self.name))

            if genre is None or genre == "":
                genre_message = "File doesnt have genre set"
                self.genres = ""
            else:
                genre_message = "The genre is {}".format(genre)
                self.genres = genre
            #print('The track number is {track_num} and the track name is {tracktitle} by {artist}. {genre}'  .format(
            #    track_num=track_num, tracktitle=name, artist=artist, genre=genre_message))

    def print_song(self):
        if self.check_file_loaded():
            print('Track name is {tracktitle} by {artist}.The genre is {genre}'  .format(
                tracktitle=self.name, artist=self.searching_name, genre=self.genres))


    def check_file_loaded(self):
        if not self.failed_to_read:
            return False
        return True
    def set_genre(self):
        if self.check_file_loaded() and self.genres.strip() != "":
            #set example genre
            self.mt_object['genre'] = self.genres
            self.mt_object.save()
            return 1
        else:
            return 0
    def get_genre(self):
        if self.searching_name == "":
            no_artist_msg = "NO_ARTIST: No artist was found for filename: {filename}\n".format(filename=self.filename)
        elif self.check_file_loaded():
            try:
                results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                                               type='artist',limit=1)
                #self.log("debug.txt",str(results)+ " , ")
                if results['artists']['items'] == []:
                    #raise ValueError("Artist not found on Spotify API") 
                    self.log("error_log.txt","Artist:{artist}  not found on Spotify API\n".format(
                        artist=self.searching_name))
                    return
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
