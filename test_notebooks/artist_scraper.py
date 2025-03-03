from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def scrape_artist(url):
    """Scrape sets from artist given by `url`, and saves them on disk"""
    # Initialize the Chrome driver
    driver = webdriver.Chrome()
    driver.get(url)
    urls = []
    all_rows = set()
    prev_rows_count = 0
    while True:
        rows = driver.find_elements(By.CLASS_NAME, "bItm")
        all_rows |= set(rows)
        if len(rows) == prev_rows_count:
            print("End of page reached")
            break
        # if  len(all_rows) >= 300:
        #     print("300 sets parsed")
        #     break
        prev_rows_count = len(rows) 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20)
            
    for row in all_rows:
        currentUrl = "https://www.1001tracklists.com" + row.get_attribute('onclick').split("window.open(")[1].split("\',")[0][1:-2]
        urls.append(currentUrl)
    # with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_set_urls.data", "wb") as file:
    #     pickle.dump(urls, file)
    driver.quit()
    return urls




dj_urls = [
    "https://www.1001tracklists.com/dj/alesso/index.html",
    "https://www.1001tracklists.com/dj/discolines/index.html",
    "https://www.1001tracklists.com/dj/davidguetta/index.html",
    "https://www.1001tracklists.com/dj/moguai/index.html",
    "https://www.1001tracklists.com/dj/swedishhousemafia/index.html",
    "https://www.1001tracklists.com/dj/afrojack/index.html",
    "https://www.1001tracklists.com/dj/diplo/index.html",
    "https://www.1001tracklists.com/dj/tiesto/index.html",
    "https://www.1001tracklists.com/dj/fisher/index.html",
    "https://www.1001tracklists.com/dj/oddmob/index.html",
    "https://www.1001tracklists.com/dj/johnsummit/index.html",
]


import re
import pickle
def extract_between(url):
    match = re.search(r'https://www.1001tracklists.com/dj/(.*?)/index.html', url)
    return match.group(1) if match else None

import pickle
for url in dj_urls:
    filename = extract_between(url) + ".set"
    artist_urls = scrape_artist(url)
    time.sleep(300)
    with open(filename, 'wb') as file:
        pickle.dump(artist_urls, file)