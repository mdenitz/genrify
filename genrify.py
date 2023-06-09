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
import requests
from bs4 import BeautifulSoup
import json
    

def __main__():
    """ Main Function that initiates genre conversion. Handles user input for runtime settings."""
    
    
    folder_name = ""
    OVERWRITE = False
    song_limit = -1
    # If no folder path given we will keep asking
    while folder_name == "":
        # Get folder name and strip weird space if neccessary 
        folder_name = str(input("Please provide the folder path containing your MP3s:\n")).replace('\\ ', ' ').strip()
        if folder_name.strip() == "":
            print("No Path given for folder...\n")


    # Check if Overwrite is on
    overwrite_setting = str(input("Would you like to overwrite current file's genres if they exist? Y/y or N/n\n")).lower()
    OVERWRITE = confirm(overwrite_setting)
    # Double check to make sure the user wants to overwrite their genre data
    if OVERWRITE:
        you_sure = str(input("Are you sure you'd like to overwrite current song genres? Y/y or N/n\n")).lower()
        OVERWRITE = confirm(you_sure)
    # Check for limit on how many mp3s are processed
    limit = str(input("Do you want to set a limit on how many songs you'd like to change? Y/y or N/n\n")).lower()
    if confirm(limit):
        song_limit = int(input("How many files do you want to change?\n"))
    #  Get the song data using music_tag
    with Loader("Getting file song data...",""):
        lib = Library(folder_name,OVERWRITE,song_limit)
    loader = Loader("","")

    # Now we will begin attempting to collect genre data from Spotify API
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
    """ Checks user input for y or n. Defaults to no if something other than
        y or Y is inputted.

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
    """Checks if config file exists, if not then attempts to create one from user input
    Returns:
        bool: True if we are using simple auth, false if not
    """
    scc_auth = str(input("Would you like to use Spotify client credentials flow (alternative is easy auth)? Y/y or N/n\n")).lower()
    harder_auth = confirm(scc_auth)
    if not harder_auth:
        return False 

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
    return True
# The following functions perform API calls using requests. 
def get_new_token():
    """Gets API Key from Spotify if no credentials provided
    Returns:
        str: The API Key
    """
    try:
        r = requests.request("GET", "https://open.spotify.com/")
        r_text = BeautifulSoup(r.content, "html.parser").find("script", {"id": "session"}).get_text()
        return json.loads(r_text)['accessToken']
    except Exception as e:
        print("Couldnt get API Key\n")
        exit()


token = None
# We must check for config file before deciding to import
if check_config():
    import config
else:
    # if we dont have a config file or are choosing not to use then get token
    token = get_new_token()



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
    def attempt_auth():
        """Attempts to get Spotify Credentials from config.py. If no 
        credentials found then environment variables are checked. If that doesn't
        succeed then API Key is pulled from site
        Returns:
            obj: None if no spotipy client established, else spotipy client
        """

        if token is not None:
            return None
        # Tries to utilize Spotipy Client Credential Flow
        # If no config.py file initiated then results in error
        try:

            client_credentials_manager = SCC(client_id=config.client_id,
                                                     client_secret=config.client_secret)
            return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            print("Issue with Oauth: {}\n".format(e))
            print("Attempting to resolve with Environment Variables.\n")
            sleep(1)
            try:
                 client_id = os.environ.get('client_id')
                 client_secret = os.environ.get('client_secret')
                 if client_id != None and client_secret != None:
                     client_credentials_manager = SCC(client_id=client_id,
                                                      client_secret=client_secret)
                     print("Credentials verified using environment variables. Proceed.\n")
                     sleep(1)
                     return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

                 else:
                     print("No Environment Variables Found...\n")
                     #print("Please either set client_id and client_secret in config.py file or set as environment variables.\n")
                     print("Now attempting to grab API Key from Spotify Site\n")
                     return None
            except Exception as e:
                print("Couldnt resolve with Environment Variables\n")
                return None
    def get_artist(artist_name):
        """Makes API call to get spotify genre info without credentials flow
        Args:
            artist_name (str): Name of the artist
        Returns:
            dict: The API call result
        """
        url ="https://api.spotify.com/v1/search?query=artist%3A{artist}&type=artist&locale=en-US%2Cen%3Bq%3D0.6&offset=0&limit=1".format(artist=artist_name)
        payload={}
        headers = {
          'authorization': 'Bearer {}'.format(str(token)),
          'Sec-Fetch-Dest': 'empty',
          }
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)   



    def get_result(searching_name):
        """Searches for the genre using either credential flow or API Key
        Args:
            searching_name (str): Artist's name to search
        Returns:
            dict: Spotify search result
        """
        if FileObject.sp is not None:
            return FileObject.sp.search(q='artist:{}'.format(searching_name),
                                 type='artist',limit=1)

        else:
            return FileObject.get_artist(searching_name)


    #Attempt to sign in with spotipy
    sp = attempt_auth()
    if sp is None:
        #Modify token if no spotipy client
        global token
        token = get_new_token()
        print("API Key succesfully retrieved from Spotify\n")

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
        
        Exceptions: Failed search resulting in 401 response will yield 
        Connection Error.Other errors non connection related will be logged.
        """
        #No artist name
        if self.searching_name == "":
            no_artist_msg = "NO_ARTIST: No artist was found for filename: {filename}\n".format(filename=self.file_path)
            self.log("missing_data.txt",no_artist_msg)
            return 1
        # if file is loaded
        elif self.check_file_loaded():
            try:
                # API CALL
                #results = FileObject.sp.search(q='artist:{}'.format(self.searching_name),
                #                               type='artist',limit=1)
   
                results = FileObject.get_result(self.searching_name)

                # Artist not found on Spotify
                if results['artists']['items'] == []:
                    self.log("error_log.txt","Artist:{artist}  not found on Spotify API\n".format(
                        artist=self.searching_name))
                    return 1 
                genres = results['artists']['items'][0]['genres']
                # No genre found on Spotify for the artist
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
            #prepend the Batch # onto the message
            prnt_message = "batch # {batch} - {message}".format(
                    batch=FileObject.batch_num, message=message)
            prep = "\nBatch # {batch} - ".format(batch=FileObject.batch_num)
             
            #Write the message and wrap text to fit in a line
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
        folder_name (str): The given user path to the folder
        optional_count (int): Number of files to be loaded (if specified by user)
        existing_count (int): Number of files that already have genres
    """
  
    def __init__(self, foldername,overwrite,optional_count=-1):
        self.FileObjects= []
        self.folder_name = foldername
        self.optional_count = optional_count
        self.existing_count = 0
        self.get_objects(overwrite)
    def get_objects(self,overwrite):
        """Iterates through directory and appends FileObject to FileObjects array
        if neccesary.

        Args:
            overwrite (bool): Set to true if we are going to overwrite files that 
            have existing genre. False if we are not overwriting. Defaulted to False.
            
        """
        directory = self.folder_name
        direct_list = os.listdir(directory)
        # If we dont have a count
        if self.optional_count < 0:
            self.optional_count = len(direct_list)
        # We do have a count
        elif self.optional_count > len(direct_list):
            self.optional_count = len(direct_list)
        count = 0
        # Iterate over files
        for idx,file in enumerate(direct_list): 
            if count >= self.optional_count:
                break
            filename = os.fsdecode(file)
            # Make sure file is mp3
            if filename.endswith(".mp3"):
                path = os.path.join(directory, filename)
                # Create FileObject
                current_song = FileObject(path)
                # Overwite On
                if overwrite:
                    self.FileObjects.append(current_song)
                    count += 1
                # Overwrite off and there is no genre
                elif not overwrite and current_song.genres == "":
                    self.FileObjects.append(current_song)
                    count += 1
                # Overwrite off and there is no genre
                elif current_song.genres != "":
                    self.existing_count += 1             
    def print_songs(self):
        """Helper to print all FileObjects"""
        for song in self.FileObjects:
            song.print_song()
        
        
    def set_genres(self,loader):
        """Responsible for initiating all processes: Getting current song data.
        Getting current genre if it exists. Validating file information. Conducting
        genre change.

        Args:
            loader (obj): The Loader object that will be responsible for
            reporting current progress.
        Returns:
            (int), (int): # songs changed, artists not found

        """
        songs_changed = 0
        artist_nf = 0 
        FileObject.batch_num = self.get_batch_num()
        for song in self.FileObjects:
            # Get FileObject Data 
            song.get_song_data()
            # Get genre. If artist not found  or genre not found 
            # we add to our count for missin_data and log
            artist_nf += song.get_genre()
            # Actually set genre and track count 
            songs_changed += song.set_genre()
            #Update current message
            loader.message("{songs_changed}/{total} Converted. {issues} missing/errors".format(
                songs_changed=songs_changed,total=len(self.FileObjects),issues=artist_nf))

     
        return songs_changed, artist_nf 

    # Currently not used 
    def chunks(self,lst,n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def get_batch_num(self):
        """Get the current batch number for this run"""
        error_file = "./error_log.txt"
        missing_file = "./missing_data.txt"
        success_file = "./success.txt"
        # Take the maximum between the two log files
        batch_num = max(self.file_checker(error_file),self.file_checker(missing_file),self.file_checker(success_file))
        # Increase batch number if it exists
        if batch_num != -1:
            return batch_num + 1
        else:
            return 0

    def file_checker(self,PATH):
        """Checks if batch number is present in file.
        Args:
            PATH (str): File path

        Returns:
            int: the batch number
        """
        batch_num = -1 
        # If file exists and readable
        try:

            if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
                with open(PATH) as f:
                    for line in f:
                        pass
                    last_line = line
                    batch_num = int(line.split(" ")[2])
        except Exception as e:
            print("Issue with getting batch #: error - {}".format(str(e)))
        finally:
            return batch_num

        


class Loader:
    """A loader-like context manager.

    Args:
        desc (str, optional): The loader's description. Defaults to "Loading...".
        end (str, optional): Final print. Defaults to "Done!".
        timeout (float, optional): Sleep time between prints. Defaults to 0.1.
    Attributes:
        _thread (obj): private holds Thread object
        steps (list): holds visualization steps
        done (bool): False if ongoing, True if done
    """

    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False

    def message(self,message):
        """Setter for current message displayed

        Args:
            message (str): Message to be displayed
        """
        self.desc = message
    def start(self):
        """Begins the thread"""
        self._thread.start()
        return self

    def _animate(self):
        """Animates the loading wheel"""
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        """Commences thread"""
        self.start()

    def stop(self):
        """Stops loader and prints end statement"""
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(f"\r{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()


# Runs Script
if __name__ == "__main__":
    __main__()



