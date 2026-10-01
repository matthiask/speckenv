import ast
from pathlib import Path
from urllib import parse


__all__ = [
    "django_cache_url",
    "django_database_url",
    "django_email_url",
    "django_mailer_url",
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

    locations = [f"redis://{netloc}" for netloc in url.netloc.split(",")]

    return {
        # No need to set hiredis; redis-py automatically selects hiredis
        # if it's available
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": locations[0] if len(locations) == 1 else locations,
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


def _smtp_options(url, qs):
    options = {
        "host": url.hostname,
        "port": url.port,
        "username": _unquote(url.username or ""),
        "password": _unquote(url.password or ""),
        "use_tls": False,
        "use_ssl": False,
        "timeout": None,
    }

    if url.scheme == "smtp":
        options["host"] = url.hostname or "localhost"
        options["port"] = url.port or 25
    if url.scheme == "submission":
        options["use_tls"] = True
        options["port"] = url.port or 587
    if "ssl" in qs:
        options["use_ssl"] = True
        options["use_tls"] = False
    if "tls" in qs:
        options["use_ssl"] = False
        options["use_tls"] = True
    if timeout := qs.get("timeout"):
        options["timeout"] = int(timeout)
    return options


def django_email_url(s, /):
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))
    options = _smtp_options(url, qs)

    config = {
        "EMAIL_BACKEND": INTERESTING_MAIL_BACKENDS[url.scheme],
        "EMAIL_HOST_USER": options["username"],
        "EMAIL_HOST_PASSWORD": options["password"],
        "EMAIL_HOST": options["host"],
        "EMAIL_PORT": options["port"],
        "EMAIL_TIMEOUT": options["timeout"],
        "EMAIL_USE_SSL": options["use_ssl"],
        "EMAIL_USE_TLS": options["use_tls"],
    }

    if email := qs.get("_default_from_email"):
        config["DEFAULT_FROM_EMAIL"] = email
    if email := qs.get("_server_email"):
        config["SERVER_EMAIL"] = email
    return config


def _smtp_mailer_url(url, qs):
    options = _smtp_options(url, qs)
    for key in ("ssl_keyfile", "ssl_certfile"):
        if value := qs.get(key):
            options[key] = value
    return {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": options,
    }


def _optionless_mailer_url(backend):
    return lambda url, qs: {"BACKEND": backend, "OPTIONS": {}}


INTERESTING_MAILER_BACKENDS = {
    "smtp": _smtp_mailer_url,
    "submission": _smtp_mailer_url,
    "locmem": _optionless_mailer_url("django.core.mail.backends.locmem.EmailBackend"),
    "console": _optionless_mailer_url("django.core.mail.backends.console.EmailBackend"),
    "dummy": _optionless_mailer_url("django.core.mail.backends.dummy.EmailBackend"),
}


def django_mailer_url(s, /, *, backend=None):
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))

    if "_server_email" in qs:
        raise ValueError(
            "_server_email cannot be part of a MAILERS entry,"
            " set SERVER_EMAIL separately."
        )

    config = INTERESTING_MAILER_BACKENDS[url.scheme](url, qs)
    # Only supported by custom backends, Django rejects it otherwise
    if email := qs.get("_default_from_email"):
        config["OPTIONS"]["default_from_email"] = email
    if backend:
        config["BACKEND"] = backend
    return config


def _file_storage_url(url, qs, *, base_dir):
    return {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": base_dir / _unquote(url.path), "base_url": None} | qs,
    }


def _s3_bucket_name_key_prefix_from_path(path):
    path = _unquote(path.strip("/")).split("/")
    return {
        "aws_s3_bucket_name": path[0],
        "aws_s3_key_prefix": "/".join(path[1:]),
    }


def _try_eval(value):
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


def _s3_storage_url(url, qs, *, base_dir):
    parts = _unquote(url.netloc).rsplit("@", 1)[-1].split(".")
    options = {
        "aws_access_key_id": _unquote(url.username or ""),
        "aws_secret_access_key": _unquote(url.password or ""),
        "aws_s3_key_prefix": _unquote(url.path.strip("/")),
    }
    if parts[-2:] == ["amazonaws", "com"]:
        options["aws_region"] = parts[-3]
        if parts[0] == "s3":
            options |= _s3_bucket_name_key_prefix_from_path(url.path)
        else:
            options["aws_s3_bucket_name"] = ".".join(parts[:-4])
    else:
        # Assume another S3 service
        options["aws_s3_endpoint_url"] = "https://" + ".".join(parts)
        options |= _s3_bucket_name_key_prefix_from_path(url.path)

    return {
        "BACKEND": "django_s3_storage.storage.S3Storage",
        "OPTIONS": options | {key: _try_eval(value) for key, value in qs.items()},
    }


INTERESTING_STORAGE_BACKENDS = {
    "file": _file_storage_url,
    "s3": _s3_storage_url,
}


def django_storage_url(s, /, base_dir=None):
    if base_dir is None:
        base_dir = Path.cwd().resolve()
    url = parse.urlparse(s)
    qs = dict(parse.parse_qsl(url.query))
    return INTERESTING_STORAGE_BACKENDS[url.scheme](url, qs, base_dir=base_dir)
