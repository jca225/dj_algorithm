import pickle
from set_scraper import *


"""
Pseudo-code:

1. Loop through all the files in data. For each:
    A. Find the .set file
    B. Loop through each url in the .set file. For each
        I. Run set_scraper(url) - NB: File is pickled within this function, so it has the necessary side-effects
        II. Error handle for captcha - wait 4 hours (or something)
        III. Continue
        IV. Implement error handling for when it simply could not be parsed 

"""


import os
data_directory = "/Users/johncabrahams/Desktop/Projects/Operation Pierce Fulton/data/"

# NB: There are only folders in the data directory
for artist_folder in os.listdir(data_directory):
    # Deal with hidden .$(filename) files
    if artist_folder[0] == ".": continue
    # Invariant: "$(artist_folder).set" must exist in the folder
    artist_folder_full = data_directory + artist_folder + "/"
    with open(artist_folder_full + artist_folder + ".set", 'rb') as file:
        # Read in the list of urls
        artist_set_urls:list[str] = pickle.load(file)
    for artist_url in artist_set_urls:
        # NB: The error is with captcha
        # What is the server overload threshold?
        try:
            parse_set(artist_url, artist_folder_full)
            time.sleep(3 * 60)
        except Exception as e:
            print(str(e))
            print("On url: " + str(artist_url))
            continue