from convert import Library


def __main__():
    OVERWRITE = False
    song_limit = -1
    folder_name = str(input("Please provide the folder path containing your MP3s:\n"))
    overwrite_setting = str(input("Would you like to overwrite current file's genres if they exist? Y/y or N/n\n")).lower()
    
    example_folder = str("/Users/mrdenitz/Downloads/songs_downloaded_1879/")
    OVERWRITE = confirm(overwrite_setting)
    if OVERWRITE:
        you_sure = str(input("Are you sure you'd like to overwrite current song genres? Y/y or N/n\n")).lower()
        OVERWRITE = confirm(you_sure)
    limit = str(input("Do you want to set a limit on how many songs you'd like to change? Y/y or N/n\n")).lower()
    if confirm(limit):
        song_limit = int(input("How many files do you want to change?\n"))

    lib = Library(example_folder,OVERWRITE,song_limit)
    num_completed = lib.set_genres()
    print("-----")
    print("Succesfully converted {num_completed} Genres! See log files for errors or missing data".format(num_completed=num_completed))
    print("-----")
    #lib.print_songs()

def confirm(choice):
    if choice != "" and choice[0] == 'y':
        return True
    else:
        return False
if __name__ == "__main__":
    __main__()



