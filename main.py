from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    process = CrawlerProcess(get_project_settings())
    process.crawl("taichung_rental")
    process.start()


if __name__ == "__main__":
    main()
