from urllib import parse


__all__ = [
    "django_cache_url",
    "django_database_url",
    "django_email_url",
]


INTERESTING_DATABASE_BACKENDS = {
    "postgres": "django.db.backends.postgresql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "sqlite": "django.db.backends.sqlite3",
    # Not really but I'm feeling generous:
    "mysql": "django.db.backends.mysql",
}


def _unquote(value):
    return parse.unquote(value) if value else value


def django_database_url(s, /):
    url = parse.urlparse(s)
    qs = parse.parse_qs(url.query)

    config = {
        "ENGINE": INTERESTING_DATABASE_BACKENDS[url.scheme],
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


def django_cache_url(s, /):
    url = parse.urlparse(s)
    qs = parse.parse_qs(url.query)
    return INTERESTING_CACHE_BACKENDS[url.scheme](url, qs)


INTERESTING_MAIL_BACKENDS = {
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
    "submission": "django.core.mail.backends.smtp.EmailBackend",
    "locmem": "django.core.mail.backends.locmem.EmailBackend",
    "console": "django.core.mail.backends.console.EmailBackend",
    "dummy": "django.core.mail.backends.dummy.EmailBackend",
}


def _setif(dict, key, value):
    if not dict.get(key):
        dict[key] = value


def django_email_url(s, /):
    url = parse.urlparse(s)
    qs = parse.parse_qs(url.query)

    config = {
        "EMAIL_BACKEND": INTERESTING_MAIL_BACKENDS[url.scheme],
        "EMAIL_HOST_USER": _unquote(url.username or ""),
        "EMAIL_HOST_PASSWORD": _unquote(url.password or ""),
        "EMAIL_HOST": url.hostname,
        "EMAIL_PORT": url.port,
        "EMAIL_TIMEOUT": None,
        "EMAIL_USE_SSL": False,
        "EMAIL_USE_TLS": False,
    }

    if url.scheme == "smtp":
        _setif(config, "EMAIL_HOST", "localhost")
        _setif(config, "EMAIL_PORT", 25)
    if url.scheme == "submission":
        config["EMAIL_USE_TLS"] = True
        _setif(config, "EMAIL_PORT", 587)
    if "ssl" in qs:
        config["EMAIL_USE_SSL"] = True
        config["EMAIL_USE_TLS"] = False
    if "tls" in qs:
        config["EMAIL_USE_SSL"] = False
        config["EMAIL_USE_TLS"] = True
    if "timeout" in qs:
        config["EMAIL_TIMEOUT"] = int(qs["timeout"][0])
    if "_default_from_email" in qs:
        config["DEFAULT_FROM_EMAIL"] = qs["_default_from_email"][0]
    return config
