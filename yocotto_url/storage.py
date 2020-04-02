import abc
from dataclasses import asdict
import json
from redis.sentinel import Sentinel
from .datatypes import ShortenedUrl


BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base_encode(num, alphabet=BASE62):
    """Encode a positive number in Base X

    Arguments:
    - `num`: The number to encode
    - `alphabet`: The alphabet to use for encoding
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return "".join(arr)


class UrlAlreadyExists(Exception):
    pass


class StorageError(Exception):
    pass


class Storage:
    @abc.abstractmethod
    def get(self, url_id: str) -> ShortenedUrl:
        pass

    @abc.abstractmethod
    def put(self, shortened_url: ShortenedUrl) -> ShortenedUrl:
        pass

    @abc.abstractmethod
    def save(self, long_url: str, retry_count: int = 5) -> ShortenedUrl:
        pass


class InMemoryStorage(Storage):
    def __init__(self):
        self._storage = {}
        self._counter = 0

    def get(self, url_id: str) -> ShortenedUrl:
        return self._storage.get(url_id)

    def put(self, shortened_url: ShortenedUrl) -> ShortenedUrl:
        url_id = shortened_url.url_id
        if url_id not in self._storage:
            self._storage[url_id] = shortened_url
            return shortened_url
        else:
            raise UrlAlreadyExists(f"The url_id: {url_id} already taken.")

    def save(self, long_url: str, retry_count=5) -> ShortenedUrl:
        if retry_count == 0:
            raise StorageError("Failed to save URL.")
        try:
            shortened_url = ShortenedUrl(url_id=self._next_url_id(), long_url=long_url)
            self.put(shortened_url)
            return shortened_url
        except UrlAlreadyExists:
            return self.save(long_url, retry_count=retry_count - 1)

    def _next_url_id(self):
        url_id = base_encode(self._counter)
        self._counter += 1
        return url_id


class RedisStorage(Storage):
    def __init__(self, env: dict):
        self._redis_service_name = env.get("YOCOTTO_URL_REDIS_SERVICE_NAME", "mymaster")
        self._redis_socket_timeout = float(
            env.get("YOCOTTO_URL_REDIS_SOCKET_TIMEOUT", 0.1)
        )
        self._redis_sentinel = Sentinel(
            json.loads(
                env.get("YOCOTTO_URL_REDIS_SENTINELS", '[["redis-sentinel", 26379]]')
            )
        )

        self._redis_master = self._redis_sentinel.master_for(
            self._redis_service_name, socket_timeout=self._redis_socket_timeout
        )

        self._redis_slave = self._redis_sentinel.slave_for(
            self._redis_service_name, socket_timeout=self._redis_socket_timeout
        )

    def get(self, url_id: str) -> ShortenedUrl:
        return ShortenedUrl(**json.loads(self._redis_slave.get(url_id)))

    def put(self, shortened_url: ShortenedUrl) -> ShortenedUrl:
        url_id = shortened_url.url_id
        res = self._redis_master.setnx(url_id, json.dumps(asdict(shortened_url)))
        if res == 1:
            return shortened_url
        else:
            raise UrlAlreadyExists(f"The url_id: {url_id} already taken.")

    def save(self, long_url: str, retry_count=5) -> ShortenedUrl:
        if retry_count == 0:
            raise StorageError("Failed to save URL.")
        try:
            shortened_url = ShortenedUrl(url_id=self._next_url_id(), long_url=long_url)
            self.put(shortened_url)
            return shortened_url
        except UrlAlreadyExists:
            return self.save(long_url, retry_count=retry_count - 1)

    def _next_url_id(self):
        url_id = base_encode(self._redis_master.incr("yocotto_url_counter"))
        return url_id
