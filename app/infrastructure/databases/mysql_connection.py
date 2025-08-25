from infrastructure.interfaces.db_connection_interface import DBConnectionInterface
import pymysql


class MySQLConnection(DBConnectionInterface):

    def __init__(self, host: str, port: str, user: str, password: str, database: str):
        """
        Initialize the MySQL connection with the given parameters.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self) -> None:
        """Establish a connection to the MySQL database using PyMySQL."""
        print("Connecting to MySQL database...")
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,  # Optional: returns results as dictionaries
            )
            print("MySQL connection established successfully.")
        except pymysql.Error as err:
            print(f"Error: {err}")
            print(f"Trying to connect to MySQL database failed on {self.host}:{self.port} and user {self.user} and database {self.database} and password {self.password}")
            raise Exception(f"Failed to connect to MySQL database: {err}")

    def disconnect(self) -> None:
        print("Disconnecting from MySQL database...")
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Disconnected from MySQL database.")

    def get_connection(self):
        """Get the current MySQL database connection."""
        print("Returning MySQL database connection...")
        if self.connection is None:
            raise Exception("No active MySQL connection found.")
        return self.connection

    def is_connected(self) -> bool:
        """Check if the MySQL database connection is active."""
        if self.connection:
            try:
                self.connection.ping(reconnect=False)
                return True
            except pymysql.Error as err:
                print(f"Error checking connection status: {err}")
                return False
        return False
