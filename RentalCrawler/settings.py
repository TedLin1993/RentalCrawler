import scrapy
import logging
import datetime

scrapy.utils.log.configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='scrapy.log',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)

LOG_LEVEL = 'INFO'
USER_AGENT = 'sample-test-bot'

today = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
FEED_URI = f"rental_data_{today}.csv"
FEED_FORMAT = "csv"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

SPIDER_MODULES = ['RentalCrawler.spiders']
NEWSPIDER_MODULE = 'RentalCrawler.spiders'

# Need to be aware of meta redirect to avoid unnecessary download
METAREFRESH_ENABLED = False

# cookiejar are sometimes too smart....
COOKIES_ENABLED = False

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'RentalCrawler.pipelines.HouseDedupPipeline': 300,
}

EXTENSIONS = {
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 2
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

DOWNLOAD_DELAY = 1

BROWSER_INIT_SCRIPT = 'console.log("This command enable Playwright")'
