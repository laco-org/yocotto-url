from dataclasses import asdict
from injector import inject
from jinja2 import Environment, PackageLoader, select_autoescape
from .storage import Storage
from .datatypes import ShortenedUrl

env = Environment(
    loader=PackageLoader("yocotto_url", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def health():
    return {"ok": True}


@inject
def get_short_url(url_id: str, storage: Storage):
    shortened_url = storage.get(url_id)
    template = env.get_template("default_redirect.html")
    return template.render(shortened_url=shortened_url)


@inject
def put_short_url(url_id: str, body: dict, storage: Storage):
    return asdict(storage.put((ShortenedUrl(url_id, body.get("long_url")))))


@inject
def save_short_url(body: dict, storage: Storage):
    long_url = body.get("long_url")
    return asdict(storage.save(long_url))
