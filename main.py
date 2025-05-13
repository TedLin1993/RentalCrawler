from flask import Flask, Response
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from multiprocessing import Process

app = Flask(__name__)


def run_crawler():
    process = CrawlerProcess(get_project_settings())
    process.crawl("taichung_rental")
    process.start()


@app.route("/run-crawler", methods=["POST"])
def trigger_crawler():
    p = Process(target=run_crawler)
    p.start()
    return Response("Crawler started", status=202)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
