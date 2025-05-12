import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl("taichung_rental")
    process.start()


def main():
    while True:
        print("Spide start!")
        run_spider()
        print("Spider finished! Sleep 5 minutes.")
        time.sleep(300)


if __name__ == "__main__":
    main()
