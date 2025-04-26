from data_structures import *
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Union
import re
import time
import pickle
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.errorhandler import ElementNotInteractableException
import sys

from selenium.common.exceptions import NoSuchElementException



def parse_set(url, file_dir):
    chop = webdriver.ChromeOptions()
    chop.add_extension("/Users/johnmabrahams/Operation Pierce Fulton/ad_blocker.crx")
    driver = webdriver.Chrome(options = chop)
    
    
    time.sleep(20)
    chld = driver.window_handles[1]
    driver.switch_to.window(chld)
    driver.close()
    current_tab=driver.window_handles[0]
    driver.switch_to.window(current_tab)
    driver.get(url)

    # Check to see if captcha was hit
    try:
        driver.find_element(By.XPATH, "//img[@alt='Captcha']")
        print("Captcha found. Exiting...")
        driver.quit()
        sys.exit()
    except NoSuchElementException:
        print("No captcha found, continuing...")
        
    dj_set = Set()

    def _get_id(atom):
        match = re.search(r"(trRow)\d+", atom.get_attribute("class"))
        return int(re.search(r"\d+", match.group()).group())

    time.sleep(30)
    # Get all the meta data elements for a set
    moduleMetaDataElements = driver.find_elements("xpath", "//body[@id='body']//meta")
    # Relevant and irrelevant meta data names
    relevantMetaDataTypes = ["name", "datePublished", "numTracks", "genre"]
    irrelevantMetaDataValues = ['tracklist', '1001Tracklists', 'YouTube video']
    # Sort through only the relevant information in `moduleMetaDataElements`
    moduleMetaDataRelevantInfo = [metadata for metadata in moduleMetaDataElements if metadata.get_attribute("itemprop") in relevantMetaDataTypes and metadata.get_attribute("content") not in irrelevantMetaDataValues]
    moduleMetaData = [(metadata.get_attribute("itemprop"), metadata.get_attribute("content")) for metadata in moduleMetaDataRelevantInfo][0:5]
    # Create a dictionary of values from the metadata
    moduleMetaDataDict = {k : v for k, v in moduleMetaData}
    # Save the relevant values found
    dj_set.name = moduleMetaDataDict['name']
    dj_set.date_published = moduleMetaDataDict['datePublished']
    dj_set.num_tracks = moduleMetaDataDict['numTracks']



    def return_links(song_atom):
        """This function handles the clickage of link icons and parses the corresponding URL"""
        link_classes = ["fa-soundcloud", "fa-youtube-play", "fa-spotify", "fa-apple"]
        # Scroll up to the atom that contained the invisible mashups
        ActionChains(driver).scroll_by_amount(0, -300).perform()
        time.sleep(2)
        ActionChains(driver).scroll_to_element(song_atom).perform()
        time.sleep(2)
        # Scroll back down
        ActionChains(driver).scroll_by_amount(0, 300).perform()
        time.sleep(2)
        links = [song_atom.find_elements(By.CLASS_NAME, link) for link in link_classes]
        links_reduced = [link for link in links if link != []]
        if links_reduced == []:
            return
        links_reduced = [link[0] for link in links_reduced]
        all_actual_links = []

        for link in links_reduced:
            try:
                link.click()
            except ElementNotInteractableException:
                continue
            time.sleep(8)
                
            if not link.get_attribute("onclick"):
                continue
            link_window = driver.find_element(By.CLASS_NAME, "mP") # f border rB")
            link_close_button = link_window.find_element(By.CLASS_NAME, "close")
            actual_link = link_window.find_element(By.TAG_NAME, 'iframe').get_attribute("src")
            all_actual_links.append(actual_link)
            link_close_button.click()
            time.sleep(2)
        return all_actual_links


    def initialize_track_variables(track, currentIndex, play_time, retrievedMetaData, song_atom):
        """This method saves the metadata data for the current atom to our track object"""
        track.index = currentIndex
        try:
            track.name = retrievedMetaData["name"]
            track.artist = retrievedMetaData["byArtist"]
        except KeyError:
            track.name = "id"
            track.artist = "id"
        track.time = play_time
        track.links = return_links(song_atom)

    # This expression gets the visible atoms. 
    visible_song_atoms = driver.find_elements(By.CLASS_NAME, "tlpTog")
    # This expression gets the invisible atoms (i.e., those binded to a mix with an ellipses (...))
    invisible_song_atoms = driver.find_elements(By.CLASS_NAME, "tlpSubTog")
            
    # Loop through the visible song atoms and get their corresponding metadata
    for i in range(len(visible_song_atoms)):

        # 1. Get the visible song's data attributes, including the song link
        track = CompoundTrack()
        main_song_atom = visible_song_atoms[i]
        currentIndex = main_song_atom.find_element(By.TAG_NAME, "span").text
        metadata = main_song_atom.find_elements(By.TAG_NAME, "meta")
        play_time = main_song_atom.find_elements(By.CLASS_NAME, "cue")[0].text
        retrievedMetaData = {}
        for data in metadata:
            retrievedMetaData[data.get_attribute("itemprop")] = data.get_attribute("content")
        initialize_track_variables(track, currentIndex, play_time, retrievedMetaData, main_song_atom)
        dj_set.tracks[_get_id(main_song_atom)] = track
        
        # 2. Check for any mashups
        # Hidden songs are indicated by the tgBtn (toggle button) class name within the song atom
        if len(main_song_atom.find_elements(By.CLASS_NAME, "tgBtn")) == 1:
            invisible_atoms = []
            # Loop through the invisible atoms parsed on our initial scan (they show up on the html code DOM, but are hidden from the user)
            for invisible_atom in invisible_song_atoms:
                invisible_atom_id = _get_id(invisible_atom)
                if invisible_atom_id == _get_id(main_song_atom):
                    invisible_atoms.append(invisible_atom)
            # Click the button to make the invisible song atoms visible
            main_song_atom.find_element(By.CLASS_NAME, "tgBtn").click()
            for invisible_atom in invisible_atoms:
                hidden_track = AtomicTrack()
                currentIndex = invisible_atom.find_element(By.TAG_NAME, "span").text
                metadata = invisible_atom.find_elements(By.TAG_NAME, "meta")
                retrievedMetaData = {}
                for data in metadata:
                    retrievedMetaData[data.get_attribute("itemprop")] = data.get_attribute("content")
                initialize_track_variables(hidden_track, currentIndex, play_time, retrievedMetaData, invisible_atom)
                dj_set.tracks[_get_id(main_song_atom)].invisible_atoms.append(hidden_track)
            # Scroll up to the atom that contained the invisible mashups
            time.sleep(3)
            ActionChains(driver).scroll_to_element(main_song_atom).perform()
            ActionChains(driver).scroll_by_amount(0, -300).perform()
            time.sleep(3)
            # Click the button to make the visible song atoms invisible
            main_song_atom.find_element(By.CLASS_NAME, "tgBtn").click()
            # Scroll back down
            ActionChains(driver).scroll_by_amount(0, 300).perform()

        # 3. Check for any binded (mixed with) songs, indicated by a 'w/'
        try:
            # This will get the elements that are not invisible but bind to a previous song with a `w/` indicator.
            while visible_song_atoms[i+1].find_element(By.TAG_NAME, "span").text.rstrip().lstrip() == 'w/':
                mashed_track = AtomicTrack()
                i += 1
                mashed_song_atom = visible_song_atoms[i]
                currentIndex = mashed_song_atom.find_element(By.TAG_NAME, "span").text
                metadata = mashed_song_atom.find_elements(By.TAG_NAME, "meta")
                play_time = mashed_song_atom.find_elements(By.CLASS_NAME, "cue")[0].text
                retrievedMetaData = {}
                for data in metadata:
                    retrievedMetaData[data.get_attribute("itemprop")] = data.get_attribute("content")
                initialize_track_variables(mashed_track, currentIndex, play_time, retrievedMetaData, mashed_song_atom)
                dj_set.tracks[_get_id(main_song_atom)].invisible_atoms.append(mashed_track)
        # An IndexError means we indexed outside of the appropriate range, and therefore must be at the end of the loop.
        except IndexError:
            break


    # TODO: Do this in the appropriate dj name file
    file = file_dir + "_".join([dj_set.name, dj_set.date_published]) + ".mx"
    with open(file, 'wb') as file:
        pickle.dump(dj_set, file)
    driver.quit()


"""
TODO:
Add method for checking if set already exists. Should be fairly straight-forward
"""