import os
import connexion
from dotenv import load_dotenv
from injector import singleton
from flask_injector import FlaskInjector

from .storage import Storage, InMemoryStorage, RedisStorage
from .logging import setup_logging

from structlog import getLogger

log = getLogger(__name__)


def configure_storage(binder):
    if os.getenv("YOCOTTO_URL_STORAGE") == "redis":
        log.info("Starting with redis storage.")
        binder.bind(Storage, to=RedisStorage(os.environ), scope=singleton)
    else:
        binder.bind(Storage, to=InMemoryStorage(), scope=singleton)


def load_environment_file():
    ENVFILE_PATH = os.getenv("ENVFILE_PATH", ".env")
    load_dotenv(ENVFILE_PATH, override=True)


def setup_app():
    load_environment_file()
    setup_logging()
    app = connexion.FlaskApp(__name__, specification_dir="../openapi/")
    app.add_api("yocotto_url.yaml")
    FlaskInjector(app.app, [configure_storage])
    return app

