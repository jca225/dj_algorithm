from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from typing import Union, List
from dataclasses import dataclass
from datetime import time as dt
import pickle
import traceback

# Open the file outside the loop
file_path = "/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_sets.data"
file = open(file_path, 'ab')  # Keep the file open for appending


SLEEP_TIME = 15
@dataclass
class Instrumental:
    name: str
    artist: str
    startTime: Union[dt, None]
    url: Union[str, None]

@dataclass
class Acapella:
    name: str
    artist: str
    startTime: Union[dt, None]
    url: Union[str, None]

@dataclass
class Song:
    name: str
    artist: str
    order: int
    startTime: Union[dt, None]
    spotify_url: Union[str, None]
    soundcloud_url: Union[str, None]
    mixed_with: list

@dataclass
class ID:
    order: int
    startTime: Union[dt, None]
    mixed_with: list

@dataclass
class Mashup:
    name: str
    artist: str
    order: str
    startTime: Union[dt, None]
    spotify_url: Union[str, None]
    soundcloud_url: Union[str, None]
    atoms: List[Union[Song, Acapella, Instrumental, ID]]
    mixed_with: list

class Set:
    def __init__(self, url):
        self.set = []
        self.url = url
        self.audioLinks = []
    
    def add(self, a):
        self.set.append(a)
    
    def addMashupAtom(self, atom):
        assert(type(self.set[-1]) == Mashup)
        self.set[-1].atoms.append(atom)

    def addMixedWith(self, atom):
        self.set[-1].mixed_with.append(atom)

    def addUrls(self, spotify_link, soundcloud_link):
        self.set[-1].spotify_url = spotify_link
        self.set[-1].soundcloud_url = soundcloud_link
    
    def addAudioLinks(self, audioLinks):
        self.audioLinks = audioLinks

class SetParser:
    

    def scrape_set(self, url:str):
        try:
            set = self._scrapeSetAux(url)
            return set
        except Exception as e:
            print("Did not work for url: " + str(url))
            traceback.print_exc()
            # Optional: print more details
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")
            
    def _scrapeSetAux(self,url:str):
        """Scrape songs from set given by `url`"""
        song_list = Set(url)
        driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in your PATH
        driver.get(url)
        time.sleep(SLEEP_TIME)
        self.soup = BeautifulSoup(driver.page_source, "html.parser")
        if not self._checkMissingData():
            return []
        urls = self._getSetLink(driver)
        if len(urls) == 0:
            return []
        song_list.addAudioLinks(urls)
        rows = self.soup.find_all('div', attrs={'data-trno': True})
        for row in rows:
            try:
                soundcloud_click_element, spotify_click_element = self._scrollFindLinks(driver, row, row.find("div", class_="iRow"))
                song_or_mashup_indicator = row.get('data-isided') == 'true'
                mashup_atom_indicator = row.get('data-mashpos') == 'true'
                startTimeStr = row.find('div', class_='bPlay').find('div').text
                if startTimeStr == '':
                    startTime = dt(hour=0, minute=0, second=0)
                else:
                    splitTimeStr = startTimeStr.split(":")
                    if len(splitTimeStr) == 3: startTime = dt(hour=int(splitTimeStr[0]), minute=int(splitTimeStr[1]), second=int(splitTimeStr[2]))
                    else: startTime = dt(hour=0, minute=int(splitTimeStr[0]), second=int(splitTimeStr[1]))
            except:
                startTime = None
            if not song_or_mashup_indicator and not mashup_atom_indicator: # ID
                track_index = row.find('div', class_="bPlay").find("span").text.strip()
                track = ID(track_index, startTime, [])
                song_list.add(track)
                continue
            track_name = row.find('div', class_="bCont tl").find("meta", attrs={'itemprop': 'name'})['content']
            track_artist = row.find('div', class_="bCont tl").find("meta", attrs={'itemprop': 'byArtist'})['content']
            if song_or_mashup_indicator: # Song or Mashup
                track_index = row.find('div', class_="bPlay").find("span").text.strip()
                if 'data-mashup' in row.attrs:
                    track = Mashup(track_name, track_artist, track_index, startTime, None, None, [], [])
                else:
                    track = Song(track_name, track_artist, track_index, startTime,  None, None, [])    
                if track_index == 'w/': 
                    song_list.addMixedWith(track)
                else:
                    song_list.add(track)
                sc_url = self._clickElementLink(driver, soundcloud_click_element)
                sp_url = self._clickElementLink(driver, spotify_click_element)
                song_list.addUrls(sp_url, sc_url)

            elif mashup_atom_indicator: # Mashup atom, hidden
                track = Song(track_name, track_artist, track_index, startTime,  None, None, [])
                sc_url = self._clickElementLink(driver, soundcloud_click_element)
                sp_url = self._clickElementLink(driver, spotify_click_element)
                track.spotify_url = sp_url
                track.soundcloud_url = sc_url
                song_list.addMashupAtom(track)

        driver.quit()
        return song_list

    def _scrollFindLinks(self, driver, row):
        try:
            soundcloud_click_element = driver.find_element(By.ID, row.get("id")).find_element(By.CLASS_NAME, "iRow").find_element(By.CLASS_NAME, "fa-soundcloud")
            spotify_click_element =  driver.find_element(By.ID, row.get("id")).find_element(By.CLASS_NAME, "iRow").find_element(By.CLASS_NAME, "fa-spotify")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", soundcloud_click_element)
            time.sleep(SLEEP_TIME)
        except AttributeError:
            return None, None
        return soundcloud_click_element, spotify_click_element

    def _checkMissingData(self):
        """Checks if any of the tracks are missing in the set"""
        try:
            if self.soup.find('div', class_='bItmH').span.text == 'Currently no (full) recording available, tracklist incomplete and track order might not be correct.': return False
            else: return True
        except: 
            return True
        
    def _getSetLink(self, driver) -> list:
        """Gets the link to the set. Mainly used for finding tracks with no url (i.e.,Ids or mashups)"""
        target_links = []
        try:
            if self.soup.find_all('div', class_="noUser")[1].find('span').text == 'No media links found. Submit the first via the add button.': return links
        except: pass  
        active_link = self.soup.find('div', class_="tBar bB").find('div', class_="tBtn mediaTab active")
        class_names_links = ["fa-heartthis","fa-youtube-play","fa-soundcloud","fa-apple"]
        
        for class_name in class_names_links:
            try:
                set_link = driver.find_element(By.CLASS_NAME, class_name)
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", set_link)     
                break
            except:
                continue
        link_elements_noisy = self.soup.find_all('div', class_="mediaTabItm")
        for link in link_elements_noisy:
        # for (link_source_one, link_source_two) in zip(open_links, hidden_links):
            #if link_source_one.find('iframe') == None:
            #    links.append(link_source_two.find('iframe').get('src'))
            #else:
            #    links.append(link_source_one.find('iframe').get('src'))
            target_links.append(link.find('iframe').get('src'))
        # active_link = self.soup.find('div', class_="tBar bB").find_all('div', class_="tBtn mediaTab active")
        return target_links

    def _clickElementLink(self, driver, click_elem):
        try:
            click_elem.click()
            time.sleep(SLEEP_TIME)
            # Get the new page with the new soundcloud link
            soup_afterclick = BeautifulSoup(driver.page_source, "html.parser")
            url = soup_afterclick.find('div', id='tlTab').find('div', class_='mP f border rB').find('div', class_="iMediaP c").find('iframe').get('src')
            self._exitClick(driver)
        except Exception as e:
            url = None
        return url
    
    def _exitClick(self, driver):
        """Exit out of clicked link for track url"""
        exit_element =  driver.find_element(By.CLASS_NAME, "close")
        #exit_element =  driver.find_element(By.XPATH, "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@id='tlTab']//*[@class='mP f border rB']//*[@class='close']")
        exit_element.click()
        time.sleep(SLEEP_TIME)




class ArtistParser:
    def scrape_artist(self, url:str):
        """Scrape sets from artist given by `url`, and saves them on disk"""

        driver = webdriver.Chrome()  
        driver.get(url)
        time.sleep(SLEEP_TIME)
        urls = []
        all_rows = set()
        prev_rows_count = 0
        while True:
            rows = driver.find_elements(By.CLASS_NAME, "bItm")
            all_rows |= set(rows)
            if len(rows) == prev_rows_count:
                print("End of page reached")
                break
            if  len(all_rows) >= 300:
                print("300 sets parsed")
                break
            prev_rows_count = len(rows) 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SLEEP_TIME)
            
        for row in all_rows:
            currentUrl = "https://www.1001tracklists.com" + row.get_attribute('onclick').split("window.open(")[1].split("\',")[0][1:-2]
            urls.append(currentUrl)
        with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_set_urls.data", "wb") as file:
            pickle.dump(urls, file)
        return urls



if __name__ == "__main__":
    artist_url = 'https://www.1001tracklists.com/dj/alesso/index.html'
    urls = ArtistParser().scrape_artist(artist_url)
    #BASE_URL = 'https://www.1001tracklists.com'
    #scrape_dj(target_url, BASE_URL)

    #test_url = "https://1001tracklists.com/tracklist/spz8qmk/alesso-kineticfield-edc-las-vegas-united-states-2024-05-19.html"
    #set = SetParser().scrape_set(test_url)
    # Save the instance to a file
    #with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_sets.data", "wb") as file:
    #    pickle.dump(all_sets, file)



"""
I have an idea:
Rather than trying to parse the sets to be parsed and the corresponding sets in parallel, we can instead
do them sequentially. 
"""
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Use appropriate driver for your browser
driver.get("https://example.com")  # Replace with your target URL

# Set a container for data
data = set()  # Using a set to prevent duplicates

# Define a function to scroll and extract data
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for new content to load
    
    # Extract the desired data
    elements = driver.find_elements(By.CLASS_NAME, "your-class-name")  # Replace with the appropriate selector
    for element in elements:
        data.add(element.text)
    
    # Check if we've reached the bottom of the page
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break  # Exit the loop when no new data is loaded
    last_height = new_height

# Close the driver
driver.quit()

# Print the data
for item in data:
    print(item)

"""