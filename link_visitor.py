from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import pandas as pd

df_links = pd.read_csv('erarta_scraping\\art_links.csv', header=None)
links_list = df_links[0].tolist()[1:]

driver = webdriver.Chrome()

data = []
counter = 0
for link in links_list:
    counter += 1
    current_pic = {}
    current_pic["url"] = link

    driver.get(link)
    wait = WebDriverWait(driver, 5)

    try:
        name = driver.find_element('xpath', "//h1[@class='title']").text
    except Exception:
        name = ""

    try:
        artist = driver.find_element('xpath', "//h2[@class='author']//a").text
    except Exception:
        artist = ""

    try:
        price = driver.find_element('xpath', "(//span[@class='price-value'])[2]").text
        if price == "":
            price = driver.find_element('xpath', "(//span[@class='price-value'])").text
    except Exception:
        price = ""

    try:
        size = driver.find_element('xpath', "//div[@class='left-container-detail']//form[1]//div[3]//div[1]//p[1]").text
    except Exception:
        size = ""

    try:
        year = driver.find_element('xpath', "//div[@class='no-curl']//form[1]//div[4]//div[1]//p[1]").text
    except Exception:
        year = ""

    try:
        art_type = driver.find_element('xpath', "//div[@class='left-container-detail']//form[2]//div[2]//div[1]//p[1]//a[1]").text
    except Exception:
        art_type = ""

    try:
        genre = driver.find_element('xpath', "//div[@class='no-curl']//div[3]//div[1]//p[1]//a[1]").text
    except Exception:
        genre = ""
    # багет картины часто отсутствует
    try:
        baguette = driver.find_element('xpath', "//div[@class='left-container-detail']//div[6]//div[1]//p[1]//a[1]").text
    except Exception:
        baguette = ""

    try:
        technique = driver.find_element('xpath', " //div[@class='no-curl']//div[@class='hidden-xs']//div[5]//div[1]//p[1]//a[1]").text
    except Exception:
        technique = ""

    current_pic["name"] = name
    current_pic["artist"] = artist
    current_pic["price"] = price
    current_pic["size"] = size
    current_pic["year"] = year
    current_pic["art_type"] = art_type
    current_pic["genre"] = genre
    current_pic["baguette"] = baguette
    current_pic["technique"] = technique

    data.append(current_pic)
    print(f"{counter} Спарсил:", name or "[без названия]")

driver.quit()

fieldnames = [
    "url",
    "name",
    "artist",
    "price",
    "size",
    "year",
    "art_type",
    "genre",
    "baguette",
    "technique",
]

with open("art_org.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
