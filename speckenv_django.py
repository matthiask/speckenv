from urllib import parse


__all__ = ["django_database_url", "django_cache_url"]


INTERESTING_DATABASE_BACKENDS = {
    "postgres": "django.db.backends.postgresql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "sqlite": "django.db.backends.sqlite3",
    # Not really but I'm feeling generous:
    "mysql": "django.db.backends.mysql",
}


def _unquote(value):
    return parse.unquote(value) if value else value


def django_database_url(s):
    url = parse.urlparse(s)
    qs = parse.parse_qs(url.query)

    config = {
        "ENGINE": INTERESTING_DATABASE_BACKENDS.get(url.scheme, url.scheme),
        "NAME": _unquote(url.path.strip("/")),
        "USER": _unquote(url.username or ""),
        "PASSWORD": _unquote(url.password or ""),
        "HOST": _unquote(url.hostname or ""),
        "PORT": str(url.port) if url.port else "",
    }

    if conn_max_age := qs.get("conn_max_age"):
        config["CONN_MAX_AGE"] = int(conn_max_age[0])

    return config


def _redis_cache_url(url, qs):
    options = {}
    if db := url.path.strip("/"):
        options["db"] = db

    return {
        # No need to set hiredis; redis-py automatically selects hiredis
        # if it's available
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{url.netloc}",
        "KEY_PREFIX": qs["key_prefix"][0] if qs.get("key_prefix") else "",
        "OPTIONS": options,
    }


def _locmem_cache_url(url, qs):
    return {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": url.netloc,
        "KEY_PREFIX": qs["key_prefix"][0] if qs.get("key_prefix") else "",
    }


INTERESTING_CACHE_BACKENDS = {
    "redis": _redis_cache_url,
    "hiredis": _redis_cache_url,
    "locmem": _locmem_cache_url,
    "dummy": lambda *a: {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}


def django_cache_url(s):
    url = parse.urlparse(s)
    qs = parse.parse_qs(url.query)
    return INTERESTING_CACHE_BACKENDS[url.scheme](url, qs)
