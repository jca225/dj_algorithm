from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename="artist_scraper_log_2.log", encoding="utf-8", level=logging.DEBUG)


def scrape_artist(url):
    """Scrape sets from artist given by `url`, and saves them on disk"""
    chop = webdriver.ChromeOptions()
    chop.add_extension("/Users/johnmabrahams/Desktop/dj_algorithm/ad_blocker.crx")
    driver = webdriver.Chrome(options = chop)
    time.sleep(20)
    chld = driver.window_handles[1]
    driver.switch_to.window(chld)
    driver.close()
    current_tab=driver.window_handles[0]
    driver.switch_to.window(current_tab)
    # Initialize the Chrome driver
    driver = webdriver.Chrome()
    driver.get(url)
    urls = []
    all_rows = set()
    prev_rows_count = 0
    scroll_counter = 0
    scroll_heuristic = lambda x : x > 10 
    while True:
        rows = driver.find_elements(By.CLASS_NAME, "bItm")
        all_rows |= set(rows)
        if len(rows) == prev_rows_count and not scroll_heuristic(scroll_counter):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_counter += 1
            time.sleep(random.uniform(1, 4))
            continue
        if len(rows) == prev_rows_count:
            print("End of page reached")
            break
        scroll_counter = 0
        prev_rows_count = len(rows) 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 4))
            
    for row in all_rows:
        currentUrl = "https://www.1001tracklists.com" + row.get_attribute('onclick').split("window.open(")[1].split("\',")[0][1:-2]
        urls.append(currentUrl)
    # with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/alesso_set_urls.data", "wb") as file:
    #     pickle.dump(urls, file)
    driver.quit()
    return urls




dj_urls = [
    # "https://www.1001tracklists.com/dj/alesso/index.html",
    "https://www.1001tracklists.com/dj/discolines/index.html",
    "https://www.1001tracklists.com/dj/davidguetta/index.html",
    "https://www.1001tracklists.com/dj/moguai/index.html",
    # "https://www.1001tracklists.com/dj/swedishhousemafia/index.html", # NB: Set fully parsed
    "https://www.1001tracklists.com/dj/afrojack/index.html",
    "https://www.1001tracklists.com/dj/diplo/index.html",
    "https://www.1001tracklists.com/dj/tiesto/index.html",
    "https://www.1001tracklists.com/dj/fisher/index.html",
    "https://www.1001tracklists.com/dj/oddmob/index.html",
    "https://www.1001tracklists.com/dj/johnsummit/index.html",
]


# Where does this non-determinism with respect to urls originate
# (i.e., the inconsistency?)


# TODO: Find the last set in david guetta, assert
# it is the actual last set
import re
import pickle
def extract_between(url):
    match = re.search(r'https://www.1001tracklists.com/dj/(.*?)/index.html', url)
    return match.group(1) if match else None


idx = 0
import pickle
for url in dj_urls:
    idx += 1
    if idx < 3:
        continue
    logger.debug("Parsing artist: " + extract_between(url))
    filename = extract_between(url) + ".set"
    # Timer for debugging
    start_time = time.time()
    artist_urls = scrape_artist(url)
    end_time = time.time()
    logger.debug("Finished parsing artist: " + extract_between(url))
    logger.debug("Number of sets scraped : " + str(len(artist_urls)))
    logger.debug(f"Total time            : {end_time - start_time:.4f} seconds")
    time.sleep(60 * random.uniform(8, 12))
    with open(filename, 'wb') as file:
        pickle.dump(artist_urls, file)



        