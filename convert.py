import os
import music_tag as mt
import spotipy
import textwrap
from spotipy.oauth2 import SpotifyClientCredentials as SCC
import importlib.util
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
def check_config():
    """Checks if config file exists, if not then attempts to create one from user input"""
    config_exist = importlib.util.find_spec("config")
    if config_exist is None:
        print("No config file found:\n")
        client_id = str(input("Please enter Spotify API Client ID:\n"))
        client_secret = str(input("Please enter Spotify API Client Secret:\n"))
        with  open("config.py","w") as file:
            l1 = "client_id='{}'\n".format(client_id)
            l2 = "client_secret='{}'\n".format(client_secret)
            file.writelines([l1, l2])
        file.close()

check_config()
import config



class FileObject:
    """ FileObject contains file metadata and makes attempts to get mp3 genre

    
    Attributes:
        filename (str): File's path
        name (str): Title of the music track
        searching_name (str): The artist name that will be searched
        genres (str): The genre that will be applied to the song
        read_success (bool): Checks if file read_succesfully
        mt_object (obj): Music Tag object that is used to modify file


        """
    # Tries to utilize Spotipy Client Credential Flow
    # If no config.py file initiated then results in erro
    try:

        client_credentials_manager = SCC(client_id=config.client_id,
                                                 client_secret=config.client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        print("Issue with Oauth: {}".format(e))
        exit()


    batch_number = 0
    def __init__(self,filename):
        #set default to false just incase it doesnt read
        self.filename = filename
        self.name = ""
        self.searching_name = ""
        self.genres = "" 
        self.read_success = False 
        self.mt_object = self.get_mt_object(filename)
        self.get_song_data()
    def get_mt_object(self,file):
        try:
            song = mt.load_file(file)
            self.read_success = True
            return song
        except:
            
            error_message = "The filename: {} was unable to be processed".format(self.filename)
            self.log("error_log.txt", error_message)
            return None
    def get_song_data(self):
        if self.check_file_loaded():
            genre = self.mt_object['genre'].value
            self.name = self.mt_object['tracktitle']
            artist = self.mt_object['artist'].value.split('feat.')[0].split('ft.')[0].split(',')[0].split('&')[0].strip()
            track_num = self.mt_object['tracknumber']
            self.searching_name = "{artist}".format(
                    artist=artist)
            if artist is None or artist == "":
                raise ValueError("Artist not found for Filename: {filename}".format(
                    filename = self.name))

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
        if not self.read_success:
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
            self.log("missing_data.txt",no_artist_msg)
            return 1
        elif self.check_file_loaded():
            try:
                results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                                               type='artist',limit=1)

                #self.log("debug.txt",str(results)+ " , ")
                if results['artists']['items'] == []:
                    #raise ValueError("Artist not found on Spotify API") 
                    self.log("error_log.txt","Artist:{artist}  not found on Spotify API\n".format(
                        artist=self.searching_name))
                    return 1 
                genres = results['artists']['items'][0]['genres']
                if genres == []:
                    no_genre_message = "NO_GENRE: No genre was found on the Spotify API for {artist}\n".format(artist=self.searching_name)
                    self.log("missing_data.txt",no_genre_message)
                    return 1
                self.genres = " ".join(genre.capitalize() for genre in genres[0].split())
                return 0
            except Exception as e:
                if e.__class__.__name__ == "ConnectionError":
                    print("Couldnt connect to server\n")
                    exit()
                self.genres = ""
                genres = ""
                error_message = "Filename: {filename}, Artist: {artist}, Genres: {genres} error: {e}\n".format(
                        filename=self.filename,artist=self.searching_name,genres=genres,e=str(e))
                self.log("error_log.txt",error_message)
                return 1

    def log(self,filename,message):
        try:

            f = open(filename, "a+")
           # prnt_message = "Batch # {batch} - {message}".format(
           #         batch=FileObject.batch_num, message=message)
            prnt_message = "batch # {batch} - {message}".format(
                    batch=FileObject.batch_num, message=message)
            prep = "\nBatch # {batch} - ".format(batch=FileObject.batch_num)
             
            #
            #
            #f.write(prnt_message)
            f.write(textwrap.fill(text=message, width=299,initial_indent=prep,subsequent_indent=prep[1:],
                                  ))
            f.close()
        except Exception as e:
            print("Couldnt log errors and/or missing data\n")
            print(str(e))

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
        FileObject.batch_num = self.get_batch_num()
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

    def get_batch_num(self):
        error_file = "./error_log.txt"
        missing_file = "./missing_data.txt"
        batch_num = max(self.file_checker(error_file),self.file_checker(missing_file))
        if batch_num != -1:
            return batch_num + 1
        else:
            return 0

    def file_checker(self,PATH):
        batch_num = -1 
        if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
            with open(PATH) as f:
                for line in f:
                    pass
                last_line = line
                batch_num = int(line.split(" ")[2])
        return batch_num 


class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def message(self,message):
        self.desc = message
    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()



