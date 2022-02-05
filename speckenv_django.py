from urllib import parse


__all__ = ["django_database_url", "django_cache_url"]


INTERESTING_DATABASE_BACKENDS = {
    "postgres": "django.db.backends.postgresql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "sqlite": "django.db.backends.sqlite3",
    # Not really but I'm feeling generous:
    "mysql": "django.db.backends.mysql",
}

INTERESTING_CACHE_BACKENDS = {
    "redis": "django.core.cache.backends.redis.RedisCache",
    "hiredis": "django.core.cache.backends.redis.RedisCache",
}


def unquote(value):
    return parse.unquote(value) if value else value


def django_database_url(s):
    parsed = parse.urlparse(s)
    qs = parse.parse_qs(parsed.query)

    config = {
        "ENGINE": INTERESTING_DATABASE_BACKENDS.get(parsed.scheme, parsed.scheme),
        "NAME": unquote(parsed.path.strip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": unquote(parsed.hostname or ""),
        "PORT": str(parsed.port) if parsed.port else "",
    }

    if conn_max_age := qs.get("conn_max_age"):
        config["CONN_MAX_AGE"] = int(conn_max_age[0])

    return config


def django_cache_url(s):
    parsed = parse.urlparse(s)
    qs = parse.parse_qs(parsed.query)


    options = {}
    if db := parsed.path.strip("/"):
        options["db"] = db

    config = {
        # No need to set hiredis; redis-py automatically selects hiredis
        # if it's available
        "BACKEND": INTERESTING_CACHE_BACKENDS.get(parsed.scheme, parsed.scheme),
        "LOCATION": f"redis://{parsed.netloc}",
        "KEY_PREFIX": qs["key_prefix"][0] if qs.get("key_prefix") else "",
        "OPTIONS": options,
    }

    return config
