import time
from models import init_db
from link_scraper import run_scraper
from link_visitor import run_visitor

def main():
    print("=== Запуск ETL-пайплайна ===")
    start_time = time.time()

    print("\n[Шаг 0] Инициализация базы данных...")
    init_db()

    print("\n[Шаг 1] Сбор ссылок с витрины каталога...")
    run_scraper(pages_count=10) # до 62 страниц

    print("\n[Шаг 2] Извлечение детальных данных по картинам...")
    run_visitor(batch_size=20)

    elapsed = time.time() - start_time
    print(f"\n=== Пайплайн успешно завершен за {elapsed:.2f} сек. ===")

if __name__ == "__main__":
    main()