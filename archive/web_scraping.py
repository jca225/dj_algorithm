from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as seleniumExceptions
from bs4 import BeautifulSoup
import re
import time
from typing import Union, List
from dataclasses import dataclass
from datetime import time as dt
import pickle

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
        
    def scrape_set(self,url:str):
        """Scrape songs from set given by `url`"""
        song_list = Set(url)
        driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in your PATH
        driver.get(url)
        time.sleep(5)
        self.soup = BeautifulSoup(driver.page_source, "html.parser")
        if not self.checkMissingData():
            return []
        urls = self.getSetLink(driver)
        if len(urls) == 0:
            return []
        song_list.addAudioLinks(urls)
        rows = self.soup.find_all('div', attrs={'data-trno': True})
        for row in rows:
            try:
                soundcloud_click_element, spotify_click_element = self.scrollFindLinks(driver, row, row.find("div", class_="iRow"))
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
                track = ID(track_index, startTime)
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
                sc_url = self.clickElementLink(driver, soundcloud_click_element)
                sp_url = self.clickElementLink(driver, spotify_click_element)
                song_list.addUrls(sp_url, sc_url)

            elif mashup_atom_indicator: # Mashup atom, hidden
                track = Song(track_name, track_artist, track_index, startTime,  None, None, [])
                sc_url = self.clickElementLink(driver, soundcloud_click_element)
                sp_url = self.clickElementLink(driver, spotify_click_element)
                track.spotify_url = sp_url
                track.soundcloud_url = sc_url
                #if not isinstance(song_list[-1], Mashup):
                #    song_list.addMashupAtom(track)
                #else:
                song_list.addMashupAtom(track)

        driver.quit()
        return song_list

    def scrollFindLinks(self, driver, row, row_url):
        try:
            soundcloud_element_path = " ".join(row_url.find("i", class_="fa-soundcloud").get("class"))
            spotify_element_path = " ".join(row_url.find("i", class_="fa-spotify").get("class"))        
            soundcloud_global_dir =  "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@id='tlTab']//*[@id='" + row.get("id") + "']//*[@class='" + " ".join(row_url.get("class")) + "']//*[@class='" +soundcloud_element_path + "']"
            spotify_global_dir =  "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@id='tlTab']//*[@id='" + row.get("id") + "']//*[@class='" + " ".join(row_url.get("class")) + "']//*[@class='" +spotify_element_path + "']"
            soundcloud_click_element = driver.find_element(By.XPATH, soundcloud_global_dir)
            spotify_click_element = driver.find_element(By.XPATH, spotify_global_dir)
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", soundcloud_click_element)
            time.sleep(3)
        except AttributeError:
            #scroll_to =  "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@id='tlTab']//*[@id='" + row.get("id") + "']"
            #driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", scroll_to)
            return None, None
        return soundcloud_click_element, spotify_click_element

    def checkMissingData(self):
        """Checks if any of the tracks are missing in the set"""
        try:
            if self.soup.find('div', class_='bItmH').span.text == 'Currently no (full) recording available, tracklist incomplete and track order might not be correct.': return False
            else: return True
        except: 
            return True
        
    def getSetLink(self, driver) -> list:
        """Gets the link to the set. Mainly used for finding tracks with no url (i.e.,Ids or mashups)"""
        links = []
        try:
            if self.soup.find_all('div', class_="noUser")[1].find('span').text == 'No media links found. Submit the first via the add button.': return links
        except: pass  
        active_link = self.soup.find('div', class_="tBar bB").find('div', class_="tBtn mediaTab active")
        class_ = " ".join(active_link.find("i").attrs['class'])
        setlink_path = "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@class='tBar bB']//*[@class='tBtn mediaTab active']//*[@class='" + class_ + "']"
        set_link = driver.find_element(By.XPATH, setlink_path)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", set_link)     
        hidden_links = self.soup.find_all('div', class_="mediaTabItm hidden")
        open_links = self.soup.find_all('div', class_="mediaTabItm")
        for (link_source_one, link_source_two) in zip(open_links, hidden_links):
            if link_source_one.find('iframe') == None:
                links.append(link_source_two.find('iframe').get('src'))
            else:
                links.append(link_source_one.find('iframe').get('src'))
        active_link = self.soup.find('div', class_="tBar bB").find_all('div', class_="tBtn mediaTab active")
        return links

    def getSongLinks(self, driver, soundcloud_click_element, spotify_click_element):
        pass
        # clickElementLink()
        # try:
        #     soundcloud_click_element.click()
        #     time.sleep(3)
        #     # Get the new page with the new soundcloud link
        #     soup_afterclick = BeautifulSoup(driver.page_source, "html.parser")
        #     soundcloud_url = soup_afterclick.find('div', id='tlTab').find('div', class_='mP f border rB').find('div', class_="iMediaP c").find('iframe').get('src')
        #     self.exitClick(driver)
        # except Exception as e:
        #     soundcloud_url = None
        # try:
        #     spotify_click_element.click()
        #     time.sleep(3)
        #     # Get the new page with the new spotify link
        #     soup_afterclick = BeautifulSoup(driver.page_source, "html.parser")
        #     spotify_url = soup_afterclick.find('div', id='tlTab').find('div', class_='mP f border rB').find('div', class_="iMediaP c").find('iframe').get('src')
        #     self.exitClick(driver)
        # except Exception as e:
        #     spotify_url = None
        # return self.clickElementLink(driver, soundcloud_click_element), self.clickElementLink(driver, spotify_click_element)
    
    def clickElementLink(self, driver, click_elem):
        try:
            click_elem.click()
            time.sleep(3)
            # Get the new page with the new soundcloud link
            soup_afterclick = BeautifulSoup(driver.page_source, "html.parser")
            url = soup_afterclick.find('div', id='tlTab').find('div', class_='mP f border rB').find('div', class_="iMediaP c").find('iframe').get('src')
            self.exitClick(driver)
        except Exception as e:
            url = None
        return url
    
    def exitClick(self, driver):
        """Exit out of clicked link for track url"""
        exit_element =  driver.find_element(By.XPATH, "//*[@id='body']//*[@id='root']//*[@id='middle']//*[@id='tlTab']//*[@class='mP f border rB']//*[@class='close']")
        exit_element.click()
        time.sleep(3)
    # def scrape_dj(url, BASE_URL):
    #     time.sleep(10)
    #     # Set up the Selenium WebDriver
    #     driver = (
    #     webdriver.Chrome()
    #     )  # Make sure you have chromedriver installed and in your PATH
    #     driver.get(url)

    #     # Extract and print initial data
    #     initial_html = driver.page_source
    #     initial_soup = BeautifulSoup(initial_html, "html.parser")
    #     initial_music = initial_soup.find_all("div", class_="middle")


    #     for div_element in initial_music.find_all('div', class_='bItm action oItm'): 
    #         onclick_val = div_element['onclick']
    #         onclick_link = re.search(r"window\.open\('([^']*)'", onclick_val).group(1)
    #         LINK_LIST.append(BASE_URL + onclick_link)

    #     # source for scrolling: https://stackoverflow.com/questions/63647849/scroll-to-the-end-of-the-infinite-loading-page-using-selenium-python
    #     # Get scroll height after first time page load
    #     last_height = driver.execute_script("return document.body.scrollHeight")
    #     while True:
    #         # Scroll down to bottom
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         # Wait to load page / use a better technique like `waitforpageload` etc., if possible
    #         time.sleep(2)

    #         new_html = driver.page_source
            
    #         new_soup = BeautifulSoup(new_html, "html.parser")

    #         new_music = new_soup.find('div', id='middle')
    #         for div_element in new_music.find_all('div', class_='bItm action oItm'): 
    #             onclick_val = div_element['onclick']
    #             onclick_link = re.search(r"window\.open\('([^']*)'", onclick_val).group(1)
    #             LINK_LIST.append(BASE_URL + onclick_link)
                

    #         # Calculate new scroll height and compare with last scroll height
    #         new_height = driver.execute_script("return document.body.scrollHeight")
    #         if new_height == last_height:
    #             break
    #         last_height = new_height

    #     # Close the WebDriver
    #     driver.quit()


if __name__ == "__main__":
    artist_url = 'https://www.1001tracklists.com/dj/alesso/index.html'
    BASE_URL = 'https://www.1001tracklists.com'
    #scrape_dj(target_url, BASE_URL)

    test_url = "https://1001tracklists.com/tracklist/spz8qmk/alesso-kineticfield-edc-las-vegas-united-states-2024-05-19.html"
    scrape_artist('https://www.1001tracklists.com/dj/alesso/index.html')
    # set = SetParser().scrape_set(test_url)
    # Save the instance to a file
    # with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/person_instance.pkl", "wb") as file:
    #     pickle.dump(set, file)

