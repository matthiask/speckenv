from unittest import TestCase

from speckenv_django import django_mailer_url


class DjangoMailerURLTest(TestCase):
    def test_parse_smtp(self):
        self.assertEqual(
            django_mailer_url("smtp://"),
            {
                "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "OPTIONS": {
                    "host": "localhost",
                    "port": 25,
                    "username": "",
                    "password": "",
                    "use_tls": False,
                    "use_ssl": False,
                    "timeout": None,
                },
            },
        )

    def test_parse_submission(self):
        url = "submission://no-reply@example_com:8p7f%21Y%40do6%25%28%29@smtp.mailgun.com:587/"
        self.assertEqual(
            django_mailer_url(url),
            {
                "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "OPTIONS": {
                    "host": "smtp.mailgun.com",
                    "port": 587,
                    "username": "no-reply@example_com",
                    "password": "8p7f!Y@do6%()",
                    "use_tls": True,
                    "use_ssl": False,
                    "timeout": None,
                },
            },
        )

    def test_parse_timeout(self):
        self.assertEqual(
            django_mailer_url("smtp://?timeout=15")["OPTIONS"]["timeout"], 15
        )
        self.assertEqual(
            django_mailer_url("smtp://?timeout=")["OPTIONS"]["timeout"], None
        )
        with self.assertRaises(ValueError):
            django_mailer_url("smtp://?timeout=abc")

    def test_parse_ssl(self):
        options = django_mailer_url("smtp:///?ssl=yes")["OPTIONS"]
        self.assertTrue(options["use_ssl"])
        self.assertFalse(options["use_tls"])

        options = django_mailer_url("smtp:///?tls=yes")["OPTIONS"]
        self.assertTrue(options["use_tls"])
        self.assertFalse(options["use_ssl"])

    def test_parse_ssl_files(self):
        options = django_mailer_url("smtp://")["OPTIONS"]
        self.assertNotIn("ssl_keyfile", options)
        self.assertNotIn("ssl_certfile", options)

        options = django_mailer_url(
            "smtp://?ssl_keyfile=/etc/key.pem&ssl_certfile=/etc/cert.pem"
        )["OPTIONS"]
        self.assertEqual(options["ssl_keyfile"], "/etc/key.pem")
        self.assertEqual(options["ssl_certfile"], "/etc/cert.pem")

    def test_reject_server_email(self):
        with self.assertRaisesRegex(ValueError, "_server_email"):
            django_mailer_url("smtp://?_server_email=info@example.com")

    def test_parse_default_from_email(self):
        self.assertNotIn("default_from_email", django_mailer_url("smtp://")["OPTIONS"])
        config = django_mailer_url("smtp://?_default_from_email=info@example.com")
        self.assertEqual(config["OPTIONS"]["default_from_email"], "info@example.com")

    def test_backend_override(self):
        config = django_mailer_url(
            "submission://smtp.example.com?_default_from_email=info@example.com",
            backend="email_hosts.backends.EmailHostsBackend",
        )
        self.assertEqual(config["BACKEND"], "email_hosts.backends.EmailHostsBackend")
        self.assertEqual(config["OPTIONS"]["host"], "smtp.example.com")
        self.assertEqual(config["OPTIONS"]["default_from_email"], "info@example.com")

    def test_parse_other_backends(self):
        for scheme in ("locmem", "console", "dummy"):
            with self.subTest(scheme=scheme):
                self.assertEqual(
                    django_mailer_url(f"{scheme}://localhost:25?timeout=5"),
                    {
                        "BACKEND": f"django.core.mail.backends.{scheme}.EmailBackend",
                        "OPTIONS": {},
                    },
                )

    def test_parse_unknown(self):
        with self.assertRaises(KeyError):
            django_mailer_url("unknown://")
