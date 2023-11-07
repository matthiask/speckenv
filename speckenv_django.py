from urllib import parse


class InvalidURLError(Exception):
    pass


__all__ = [
    "django_cache_url",
    "django_database_url",
    "django_email_url",
    "django_storage_url",
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
    qs = dict(parse.parse_qsl(url.query))

    config = {
        "ENGINE": INTERESTING_DATABASE_BACKENDS[url.scheme],
        "NAME": _unquote(url.path.strip("/")),
        "USER": _unquote(url.username or ""),
        "PASSWORD": _unquote(url.password or ""),
        "HOST": _unquote(url.hostname or ""),
        "PORT": str(url.port) if url.port else "",
    }

    if conn_max_age := qs.get("conn_max_age"):
        config["CONN_MAX_AGE"] = int(conn_max_age)

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
        "KEY_PREFIX": qs.get("key_prefix", ""),
        "OPTIONS": options,
    }


def _locmem_cache_url(url, qs):
    return {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": url.netloc,
        "KEY_PREFIX": qs.get("key_prefix", ""),
    }


INTERESTING_CACHE_BACKENDS = {
    "redis": _redis_cache_url,
    "hiredis": _redis_cache_url,
    "locmem": _locmem_cache_url,
    "dummy": lambda *a: {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}


def django_cache_url(s, /):
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))
    return INTERESTING_CACHE_BACKENDS[url.scheme](url, qs)


INTERESTING_MAIL_BACKENDS = {
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
    "submission": "django.core.mail.backends.smtp.EmailBackend",
    "locmem": "django.core.mail.backends.locmem.EmailBackend",
    "console": "django.core.mail.backends.console.EmailBackend",
    "dummy": "django.core.mail.backends.dummy.EmailBackend",
}


def django_email_url(s, /):
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))

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
        config["EMAIL_HOST"] = url.hostname or "localhost"
        config["EMAIL_PORT"] = url.port or 25
    if url.scheme == "submission":
        config["EMAIL_USE_TLS"] = True
        config["EMAIL_PORT"] = url.port or 587
    if "ssl" in qs:
        config["EMAIL_USE_SSL"] = True
        config["EMAIL_USE_TLS"] = False
    if "tls" in qs:
        config["EMAIL_USE_SSL"] = False
        config["EMAIL_USE_TLS"] = True
    if timeout := qs.get("timeout"):
        config["EMAIL_TIMEOUT"] = int(timeout)
    if email := qs.get("_default_from_email"):
        config["DEFAULT_FROM_EMAIL"] = email
    if email := qs.get("_server_email"):
        config["SERVER_EMAIL"] = email
    return config


def _file_storage_url(url, qs):
    return {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": _unquote(url.path), "base_url": None} | qs,
    }


def _s3_storage_url(url, qs):
    parts = _unquote(url.netloc).rsplit("@", 1)[-1].split(".")
    if parts[1] != "s3" or parts[3] != "amazonaws" or parts[4] != "com":
        raise InvalidURLError(
            "Unexpected domain part. Should be bucket.s3.region.amazonaws.com."
        )
    return {
        "BACKEND": "django_s3_storage.storage.S3Storage",
        "OPTIONS": {
            "aws_region": parts[2],
            "aws_access_key_id": _unquote(url.username or ""),
            "aws_secret_access_key": _unquote(url.password or ""),
            "aws_s3_bucket_name": parts[0],
            "aws_s3_key_prefix": _unquote(url.path.strip("/")),
        }
        | qs,
    }


INTERESTING_STORAGE_BACKENDS = {
    "file": _file_storage_url,
    "s3": _s3_storage_url,
}


def django_storage_url(s, /):
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))
    return INTERESTING_STORAGE_BACKENDS[url.scheme](url, qs)
