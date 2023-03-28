#import importlib.util
from convert import Library
from Loader import Loader
def check_config():
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


def __main__():
    
    
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
    #lib.print_songs()

def confirm(choice):
    if choice != "" and choice[0] == 'y':
        return True
    else:
        return False
if __name__ == "__main__":
    __main__()



