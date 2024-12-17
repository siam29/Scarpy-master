from itemadapter import ItemAdapter
from .database.base import DatabaseManager
from .database.models import Hotel

class PostgreSQLPipeline:
    """
    Scrapy pipeline for storing hotel data in PostgreSQL
    """
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.db_manager = DatabaseManager()

    @classmethod
    def from_crawler(cls, crawler):
        """
        Retrieve connection string from Scrapy settings
        """
        return cls(
            connection_string=crawler.settings.get('SQLALCHEMY_CONNECTION_STRING')
        )

    def open_spider(self, spider):
        """
        Initialize database connection when spider starts
        """
        self.db_manager.initialize(self.connection_string)
        self.db_manager.create_tables()

    def process_item(self, item, spider):
        """
        Process each item and store in the database
        """
        session = self.db_manager.get_session()
        try:
            # Convert item to dictionary if it's not already
            item_dict = dict(item)

            # Create hotel model instance
            hotel = Hotel(
                city_name=item_dict.get('city_name'),
                property_title=item_dict.get('property_title'),
                hotel_id=item_dict.get('hotel_id'),
                price=item_dict.get('price'),
                rating=item_dict.get('rating'),
                address=item_dict.get('address'),
                latitude=float(item_dict.get('latitude', 0)) if item_dict.get('latitude') else None,
                longitude=float(item_dict.get('longitude', 0)) if item_dict.get('longitude') else None,
                room_type=item_dict.get('room_type'),
                image=item_dict.get('image'),
                local_image_path=item_dict.get('local_image_path')
            )

            # Add and commit the hotel
            session.add(hotel)
            session.commit()
            spider.logger.info(f"Added hotel: {hotel.property_title}")

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error storing hotel: {e}")
        finally:
            session.close()

        return item