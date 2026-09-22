import re
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models import engine, Artist, Artwork


def clean_price(raw_price: str) -> Optional[float]:
    """Удаляет пробелы, валюту и конвертирует в float."""
    if not raw_price:
        return None
    # Оставляем только цифры
    digits = re.sub(r"[^\d]", "", raw_price)
    return float(digits) if digits else None

def clean_year(raw_year: str) -> Optional[int]:
    """Извлекает 4-значный год создания."""
    if not raw_year:
        return None
    match = re.search(r"\b(19\d\d|20\d\d)\b", raw_year)
    return int(match.group(1)) if match else None

def get_or_create_artist(session: Session, cache: dict[str, int], artist_name: str) -> Optional[int]:
    """
    Возвращает artist_id.
    1. Ищет в локальном кэше (O(1)).
    2. Если нет в кэше — ищет в БД.
    3. Если нет в БД — создает запись, вызывает flush() для получения id
       и сохраняет id в кэш.
    """
    clean_name = artist_name.strip()
    if not clean_name:
        return None

    # проверяем локальный кэш
    if clean_name in cache:
        return cache[clean_name]

    # проверяем БД
    artist = session.scalar(select(Artist).where(Artist.name == clean_name))
    if not artist:
        # создаем нового автора
        artist = Artist(name=clean_name)
        session.add(artist)
        session.flush()  # выталкивает INSERT в базу и заполняет artist.id без закрытия транзакции

    # обновляем кэш в памяти
    cache[clean_name] = artist.id
    return artist.id

# ---------------------------------------------------------------------------
# ПАРСИНГ!!
# ---------------------------------------------------------------------------

def parse_artwork_details(driver: webdriver.Chrome, url: str) -> dict:
    """Парсит страницу картины и возвращает словарь с сырыми данными."""
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    def get_text_or_empty(xpath: str) -> str:
        try:
            return driver.find_element(By.XPATH, xpath).text.strip()
        except Exception:
            return ""

    name = get_text_or_empty("//h1[@class='title']")
    artist = get_text_or_empty("//h2[@class='author']//a")
    
    price = get_text_or_empty("(//span[@class='price-value'])[2]")
    if not price:
        price = get_text_or_empty("(//span[@class='price-value'])")

    size = get_text_or_empty("//div[@class='left-container-detail']//form[1]//div[3]//div[1]//p[1]")
    year = get_text_or_empty("//div[@class='no-curl']//form[1]//div[4]//div[1]//p[1]")
    art_type = get_text_or_empty("//div[@class='left-container-detail']//form[2]//div[2]//div[1]//p[1]//a[1]")
    genre = get_text_or_empty("//div[@class='no-curl']//div[3]//div[1]//p[1]//a[1]")
    baguette = get_text_or_empty("//div[@class='left-container-detail']//div[6]//div[1]//p[1]//a[1]")
    technique = get_text_or_empty("//div[@class='no-curl']//div[@class='hidden-xs']//div[5]//div[1]//p[1]//a[1]")

    return {
        "name": name,
        "artist": artist,
        "price": clean_price(price),
        "size": size or None,
        "year": clean_year(year),
        "art_type": art_type or None,
        "genre": genre or None,
        "baguette": baguette or None,
        "technique": technique or None,
    }

def run_visitor(batch_size: int = 10, max_total: Optional[int] = None):
    """
    Итерируется по базе пачками размера batch_size, пока не закончатся
    записи со статусом 'pending' (или пока не будет достигнут max_total).
    """
    driver = webdriver.Chrome()
    total_processed = 0
    batch_number = 1

    try:
        with Session(engine) as session:

            print("Загрузка кэша авторов из БД...")
            artists_cache = dict(session.execute(select(Artist.name, Artist.id)).all())
            print(f"В кэше авторов: {len(artists_cache)}")
            while True:
                current_limit = batch_size
                if max_total is not None:
                    remaining = max_total - total_processed
                    if remaining <= 0:
                        print(f"Достигнут общий лимит обработки ({max_total} записей).")
                        break
                    current_limit = min(batch_size, remaining)

                pending_artworks = session.scalars(
                    select(Artwork)
                    .where(Artwork.status == "pending")
                    .limit(current_limit)
                ).all()

                if not pending_artworks: # если пуская очередь
                    print("\nВсе задачи со статусом 'pending' успешно обработаны!")
                    break

                print(f"\n=== Батч #{batch_number} (задач в пачке: {len(pending_artworks)}) ===")

                for i, artwork in enumerate(pending_artworks, start=1):
                    print(f"[{i}/{len(pending_artworks)}] Парсинг: {artwork.url}")
                    try:
                        data = parse_artwork_details(driver, artwork.url)
                        artist_id = get_or_create_artist(session, artists_cache, data["artist"])

                        artwork.title = data["name"]
                        artwork.artist_id = artist_id
                        artwork.price = data["price"]
                        artwork.size = data["size"]
                        artwork.year = data["year"]
                        artwork.art_type = data["art_type"]
                        artwork.genre = data["genre"]
                        artwork.baguette = data["baguette"]
                        artwork.technique = data["technique"]
                        artwork.status = "done"

                    except Exception as exc:
                        print(f"  [Ошибка при парсинге]: {exc}")
                        artwork.status = "error"

                    total_processed += 1

                # весь батч в БД за одну транзакцию
                session.commit()
                print(f"--> Батч #{batch_number} зафиксирован в БД. Всего обработано: {total_processed}")
                
                batch_number += 1

    finally:
        driver.quit()
        print(f"\nСессия браузера закрыта. Итого обработано записей: {total_processed}")

if __name__ == "__main__":
    run_visitor()