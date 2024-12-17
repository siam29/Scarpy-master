from config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
SQLALCHEMY_CONNECTION_STRING = f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


BOT_NAME = "hotel_scraper"
SPIDER_MODULES = ["hotel_scraper.spiders"]
NEWSPIDER_MODULE = "hotel_scraper.spiders"


# Enable the PostgreSQL Pipeline
ITEM_PIPELINES = {
   'hotel_scraper.pipelines.PostgreSQLPipeline': 300,
}


ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 3
COOKIES_ENABLED = False


TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"