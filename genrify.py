""" Module to add genre metadata to mp3 files. Utilizes Spotipy and music_tag external modules.
    
    
    Classes:
        Library: Container Object that holds FileObjects to be manipulated
        FileObject: Contains File Metadata and functions for modifying file metadata
        Loader: Handles visualization of current conversion progress

    Functions:
        __main__(): Begins conversion process
        confirm(): Helper function to check user input for y or n
        check_config(): Checks for existance of config.py file for Spotify API Credentials
"""
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

def __main__():
    """ Main Function that initiates genre conversion. Handles user input for runtime settings."""
    
    
    OVERWRITE = False
    song_limit = -1
    folder_name = str(input("Please provide the folder path containing your MP3s:\n"))
    overwrite_setting = str(input("Would you like to overwrite current file's genres if they exist? Y/y or N/n\n")).lower()
    
    test = str("/Users/mrdenitz/Downloads/songs_downloaded_1879/")
    OVERWRITE = confirm(overwrite_setting)
    if OVERWRITE:
        you_sure = str(input("Are you sure you'd like to overwrite current song genres? Y/y or N/n\n")).lower()
        OVERWRITE = confirm(you_sure)
    limit = str(input("Do you want to set a limit on how many songs you'd like to change? Y/y or N/n\n")).lower()
    if confirm(limit):
        song_limit = int(input("How many files do you want to change?\n"))
    if folder_name == "":
        folder_name = test
    with Loader("Getting file song data...",""):
        lib = Library(folder_name,OVERWRITE,song_limit)
    loader = Loader("","")

    loader.start()
    num_completed,num_artist_nf = lib.set_genres(loader)
    loader.stop()
    existing = lib.existing_count
    print("-----")
    print("Succesfully converted {num_completed} Genres!".format(num_completed=num_completed))
    if num_artist_nf != 0:
        print("{artist} songs couldnt be processed. See log files for errors or missing data".format(artist=num_artist_nf))
    if existing != 0:
        print("{existing} songs already have genres and were not overwritten.".format(existing=existing))
    print("-----")

def confirm(choice):
    """ Checks user input for y or n 

    Args:
        choice (str): Holds the user input string

    Returns:
        bool: True for yes and False for no
    """
    if choice != "" and choice[0] == 'y':
        return True
    else:
        return False


def check_config():
    """Checks if config file exists, if not then attempts to create one from user input"""
    config_exist = importlib.util.find_spec("config")
    if config_exist is None:
        print("No config file found:\n")
        client_id = str(input("Please enter Spotify API Client ID:\n"))
        client_secret = str(input("Please enter Spotify API Client Secret:\n"))
        with  open("config.py", "w") as file:
            l1 = "client_id='{}'\n".format(client_id)
            l2 = "client_secret='{}'\n".format(client_secret)
            file.writelines([l1, l2])
        file.close()
# We must check for config file before deciding to import
check_config()
import config



class FileObject:
    """ FileObject contains file metadata and makes attempts to get mp3 genre with spotipy package. 

    Class Attributes:
        client_credentials_manager (obj): Spotify Client Credentials Manager
        sp (obj): Instance of Spotipy to run search
        batch_num (int): Holds batch number for logging

    Attributes:
        file_path (str): File's path
        name (str): Title of the music track
        searching_name (str): The artist name that will be searched
        genres (str): The genre that will be applied to the song
        read_success (bool): Checks if file read_succesfully
        mt_object (obj): Music Tag object that is used to modify file
    """
    # Tries to utilize Spotipy Client Credential Flow
    # If no config.py file initiated then results in error
    try:

        client_credentials_manager = SCC(client_id=config.client_id,
                                                 client_secret=config.client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    except Exception as e:
        print("Issue with Oauth: {}".format(e))
        exit()


    batch_number = 0
    def __init__(self, file_path):
        self.file_path = file_path 
        self.name = ""
        self.searching_name = ""
        self.genres = "" 
        self.read_success = False 
        self.mt_object = self.get_mt_object()
        self.get_song_data()
    def get_mt_object(self):
        """Attempts to get music_tag object. If not found then error is logged and FileObject marked as unprocessed.

        """
        try:
            song = mt.load_file(self.file_path)
            self.read_success = True
            return song
        except:
            # Log error if file can't be processed 
            error_message = "The filename: {} was unable to be processed".format(self.file_path)
            self.log("error_log.txt", error_message)
            return None
    def get_song_data(self):
        """If music_tag object is correctly loaded then parses data for FileObject."""
        if self.check_file_loaded():
            genre = self.mt_object['genre'].value
            self.name = self.mt_object['tracktitle']
            #Must process single leading artist
            artist = self.mt_object['artist'].value.split('feat.')[0].split('ft.')[0].split(',')[0].split('&')[0].strip()
            self.searching_name = "{artist}".format(
                    artist=artist)
            # If no artist exists then we handle this later and set our artist name to "" 
            if artist is None or artist == "":
                self.searching_name = ""
            if genre is None or genre == "":
                genre_message = "File doesnt have genre set"
                self.genres = ""
            else:
                genre_message = "The genre is {}".format(genre)
                self.genres = genre

    def print_song(self):
        """ Helper to print current mp3 data."""
        if self.check_file_loaded():
            print('Track name is {tracktitle} by {artist}.The genre is {genre}'  .format(
                tracktitle=self.name, artist=self.searching_name, genre=self.genres))


    def check_file_loaded(self):
        """Checks if the file was processed correctly
        Returns:
            bool: True if read succesfully, False if not
        """
        if not self.read_success:
            return False
        return True
    def set_genre(self):
        """ Sets genre for current song if new genre exists
        Returns:
            int: 1 if genre processed, 0 if genre not processed
        """
        if self.check_file_loaded() and self.genres.strip() != "":
            self.mt_object['genre'] = self.genres
            self.mt_object.save()
            message = "{tracktitle} by {artist} successfully set to genre: {genre}".format(
                tracktitle=self.name, artist=self.searching_name, genre=self.genres)
            self.log("success.txt", message)

            return 1
        else:
            return 0
    def get_genre(self):
        """Attempts to get genre using Spotipy client.
        Returns:
            int: 1 if artist not found and log happens, 0 if artist found
        
        """
        if self.searching_name == "":
            no_artist_msg = "NO_ARTIST: No artist was found for filename: {filename}\n".format(filename=self.file_path)
            self.log("missing_data.txt",no_artist_msg)
            return 1
        elif self.check_file_loaded():
            try:
                results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                                               type='artist',limit=1)

                if results['artists']['items'] == []:
                    self.log("error_log.txt","Artist:{artist}  not found on Spotify API\n".format(
                        artist=self.searching_name))
                    return 1 
                genres = results['artists']['items'][0]['genres']
                if genres == []:
                    no_genre_message = "NO_GENRE: No genre was found on the Spotify API for {artist}\n".format(artist=self.searching_name)
                    self.log("missing_data.txt", no_genre_message)
                    return 1
                self.genres = " ".join(genre.capitalize() for genre in genres[0].split())
                return 0
            except Exception as e:
                # Handles no connection to server
                if e.__class__.__name__ == "ConnectionError":
                    print("Couldnt connect to server\n")
                    exit()
                self.genres = ""
                genres = ""
                error_message = "Filename: {filename}, Artist: {artist}, Genres: {genres} error: {e}\n".format(
                        filename=self.file_path, artist=self.searching_name, genres=genres, e=str(e))
                self.log("error_log.txt", error_message)
                return 1

    def log(self,filename,message):
        """Function to log errors, missing data, and successes
        
        Args:
            filename (str): Name of the logging file
            message (str): The message to be logged
        
        """

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
            print("Couldnt log succesfully: error - {}\n".format(str(e)))

class Library:
"""Container Object that holds FileObjects to be manipulateda. Takes in optional parameters
    collected from user input.

    Attributes:
        FileObjects (list): Contains FileObjects
        folder_name
        read_success (bool): Checks if file read_succesfully
        mt_object (obj): Music Tag object that is used to modify file
    """
  
    def __init__(self, foldername,overwrite,optional_count=-1):
        self.FileObjects= []
        self.folder_name = foldername
        self.optional_count = optional_count
        self.existing_count = 0
        self.get_objects(overwrite)
    def get_objects(self,overwrite):
        directory = self.folder_name
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


if __name__ == "__main__":
    __main__()



