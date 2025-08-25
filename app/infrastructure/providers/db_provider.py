from infrastructure.interfaces.provider_interface import ProviderInterface
from infrastructure.databases.mysql_connection import MySQLConnection
from infrastructure.databases.redis_connection import RedisConnection
from infrastructure.config.config import get_env


class DBProvider(ProviderInterface):

    def __init__(self):
        self.services = {}

    def bind(self, name: str, callable_fn: callable) -> None:
        self.services[name] = callable_fn

    def make(self, name: str):
        if name not in self.services:
            raise Exception(f"DB service not found: {name}")
        return self.services[name]()

    def has(self, name: str) -> bool:
        return name in self.services

    def register(self, container) -> None:
        self.bind(
            "mysql_connection",
            lambda: MySQLConnection(
                host=get_env("MYSQL_HOST", "localhost"),
                port=3306,
                user=get_env("MYSQL_USER", "root"),
                password=get_env("MYSQL_PASSWORD", "password"),
                database=get_env("MYSQL_DATABASE", "my_database"),
            ),
        )

        self.bind(
            "redis_connection",
            lambda: RedisConnection(
                host=get_env("REDIS_HOST", "localhost"),
                port=get_env("REDIS_PORT", 6379),
                db=get_env("REDIS_DB", 0),
            ),
        )
