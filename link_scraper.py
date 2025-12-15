from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

BASE_URL = "https://shop.erarta.com/ru/shop/catalogue/"

def get_links_from_page(url, i):
    driver.get(url)
    CARD_SELECTOR = f"div#product_list_{i} > div.product-grid-item"
    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR))
    )

    print("Найдено карточек:", len(cards))

    links = []
    for card in cards:
        link_el = card.find_element(By.CSS_SELECTOR, "a")
        href = link_el.get_attribute("href")
        links.append(href)
    return links

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

links = []
for i in range(1, 62):
    wait = WebDriverWait(driver, 10)
    URL_new_page = f"{BASE_URL}?pageIndex={i}"
    l = get_links_from_page(URL_new_page, i)
    print(f"Страница {i} новых ссылок {len(l)}")
    links.extend(l)

driver.quit()

rows = [{"url": href} for href in links]

with open("art_links_all.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["url"])
    writer.writeheader()
    writer.writerows(rows)
