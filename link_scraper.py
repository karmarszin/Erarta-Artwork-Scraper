from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from models import engine, Artwork
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
import datetime as dt


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

BASE_URL = "https://shop.erarta.com/ru/shop/catalogue/original/"

def get_links_from_page(url, i):
    driver.get(url)
    CARD_SELECTOR = f"div#product_list_{i} > div.product-grid-item"

    try:
        cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR))
        )
    except TimeoutException:
        print("Карточки не загрузились за отведённое время")
        cards = []   # обязательно что-то присвоить, иначе дальше будет NameError
        

    print("Найдено карточек:", len(cards))

    links = []
    for card in cards:
        link_el = card.find_element(By.CSS_SELECTOR, "a")
        href = link_el.get_attribute("href")
        links.append(href)
    return links


def run_scraper(pages_count=5):
    #driver = webdriver.Chrome()
    #wait = WebDriverWait(driver, 10)

    links = []
    try:
        # for i in range(1, 62):
        for i in range(1, pages_count+1):
            #wait = WebDriverWait(driver, 10)
            URL_new_page = f"{BASE_URL}?pageIndex={i}"
            l = get_links_from_page(URL_new_page, i)
            print(f"Страница {i} новых ссылок {len(l)}")
            links.extend(l)
        # driver.quit()
        rows = [{"url": href} for href in links]

        session = Session(engine)
        stmt = insert(Artwork).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=['url'],
            set_={'updated_at': dt.datetime.now()}
        )
        session.execute(stmt)
        session.commit()
    finally:
        driver.quit()


if __name__ == '__main__':
    run_scraper(pages_count=10)