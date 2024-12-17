from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a base class for declarative models
Base = declarative_base()

class DatabaseManager:
    """
    Manages database connection and session creation
    """
    _instance = None

    def __new__(cls, connection_string=None):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.connection_string = connection_string
            cls._instance.engine = None
            cls._instance.Session = None
        return cls._instance

    def initialize(self, connection_string):
        """
        Initialize the database engine and session factory
        
        :param connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.engine = create_engine(connection_string, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        Create all defined tables in the database
        """
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Get a new database session
        
        :return: SQLAlchemy session
        """
        if not self.Session:
            raise ValueError("Database not initialized. Call initialize() first.")
        return self.Session()