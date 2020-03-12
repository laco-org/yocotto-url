import connexion
from injector import singleton
from flask_injector import FlaskInjector
from .storage import Storage, InMemoryStorage


def configure_storage(binder):
    binder.bind(Storage, to=InMemoryStorage(), scope=singleton)


def setup_app():
    app = connexion.FlaskApp(__name__, specification_dir="../openapi/")
    app.add_api("yocotto_url.yaml")
    FlaskInjector(app.app, [configure_storage])
    return app

