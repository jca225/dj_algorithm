from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pickle
import time
from selenium.webdriver.common.by import By

# Time between actions
SLEEP_TIME = 10
# Define the path to the chromedriver
chromedriver_path = "/Users/johncabrahams/chromedriver-mac-x64/chromedriver"
# Set up the Service object
SERVICE = Service(executable_path=chromedriver_path)

class ArtistParser:
    def scrape_artist(self, url:str):
        """Scrape sets from artist given by `url`, and saves them on disk"""
        # Initialize the WebDriver with the Service object
        driver = webdriver.Chrome(service=SERVICE)
        driver.get(url)
        time.sleep(SLEEP_TIME)
        urls = []
        all_rows = set()
        last_height = driver.execute_script("return document.body.scrollHeight")
        exit_condition = False
        while not exit_condition:
            rows = driver.find_elements(By.CLASS_NAME, "bItm")
            all_rows |= set(rows)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
            time.sleep(SLEEP_TIME)
            # exit_condition = (last_height == new_height) and (len(all_rows > 300))
            exit_condition = driver.find_elements(By.CLASS_NAME, "redTxt")[-1].text == "No more items found"
            print("URLs parsed: " + str(len(rows)))
            
            
        for row in all_rows:
            currentUrl = "https://www.1001tracklists.com" + row.get_attribute('onclick').split("window.open(")[1].split("\',")[0][1:-2]
            urls.append(currentUrl)
        with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_set_urls.data", "wb") as file:
            pickle.dump(urls, file)
        return urls



if __name__ == "__main__":
    artist_url = 'https://www.1001tracklists.com/dj/alesso/index.html'
    urls = ArtistParser().scrape_artist(artist_url)

