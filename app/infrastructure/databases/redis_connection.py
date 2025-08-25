import redis
from infrastructure.interfaces.db_connection_interface import DBConnectionInterface


class RedisConnection(DBConnectionInterface):

    def __init__(self, host: str, port: int, db: int):
        """
        Initialize the Redis connection with the given parameters.
        """
        self.host = host
        self.port = port
        self.db = db
        self.connection = None

    def connect(self) -> None:
        """Establish a connection to the Redis database."""
        print("Connecting to Redis database...")
        try:
            self.connection = redis.Redis(host=self.host, port=self.port, db=self.db)
            self.connection.ping()  # Test the connection
            print("Connection to Redis established successfully.")
        except redis.ConnectionError as err:
            print(f"Error: {err}")
            raise Exception(f"Failed to connect to Redis database: {err}")

    def disconnect(self):
        if self.connection:
            print("Disconnecting from Redis database...")
            self.connection.close()
            self.connection = None
            print("Disconnected from Redis database.")

    def get_connection(self):
        """Get the current Redis database connection."""
        print("Getting Redis database connection...")
        if self.connection is None:
            raise Exception("No active Redis connection found.")
        return self.connection

    def is_connected(self) -> bool:
        """Check if the Redis database connection is active."""
        if self.connection:
            try:
                return (
                    self.connection.ping()
                )
            except redis.ConnectionError as err:
                print(f"Error checking connection status: {err}")
                return False
        return False
