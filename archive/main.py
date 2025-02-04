from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from typing import Union, List
from dataclasses import dataclass
from datetime import time as dt
import pickle
from web_scraping import *

# Load the instance from the file
with open("/Users/johncabrahams/Desktop/Archive/Operation Pierce Fulton/person_instance.pkl", "rb") as file:
    loaded_instance = pickle.load(file)

# Use the loaded instance
print("hi")