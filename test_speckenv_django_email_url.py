from unittest import TestCase

from speckenv_django import django_email_url


class DjangoEmailURLTest(TestCase):
    def test_parse_smtp(self):
        self.assertEqual(
            django_email_url("smtp://"),
            {
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "EMAIL_HOST": "localhost",
                "EMAIL_HOST_PASSWORD": "",
                "EMAIL_HOST_USER": "",
                "EMAIL_PORT": 25,
                "EMAIL_TIMEOUT": None,
                "EMAIL_USE_SSL": False,
                "EMAIL_USE_TLS": False,
            },
        )

    def test_parse_submission(self):
        url = "submission://no-reply@example_com:8p7f%21Y%40do6%25%28%29@smtp.mailgun.com:587/"
        self.assertEqual(
            django_email_url(url),
            {
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "EMAIL_HOST": "smtp.mailgun.com",
                "EMAIL_HOST_PASSWORD": "8p7f!Y@do6%()",
                "EMAIL_HOST_USER": "no-reply@example_com",
                "EMAIL_PORT": 587,
                "EMAIL_TIMEOUT": None,
                "EMAIL_USE_SSL": False,
                "EMAIL_USE_TLS": True,
            },
        )

    def test_parse_timeout(self):
        self.assertEqual(django_email_url("smtp://?timeout=15")["EMAIL_TIMEOUT"], 15)
        self.assertEqual(django_email_url("smtp://?timeout=")["EMAIL_TIMEOUT"], None)
        with self.assertRaises(ValueError):
            django_email_url("smtp://?timeout=abc")

    def test_parse_default_from_email(self):
        self.assertNotIn("DEFAULT_FROM_EMAIL", django_email_url("smtp://"))
        config = django_email_url("smtp://?_default_from_email=info@example.com")
        self.assertEqual(config["DEFAULT_FROM_EMAIL"], "info@example.com")

    def test_parse_server_email(self):
        self.assertNotIn("SERVER_EMAIL", django_email_url("smtp://"))
        config = django_email_url("smtp://?_server_email=info@example.com")
        self.assertEqual(config["SERVER_EMAIL"], "info@example.com")

    def test_parse_ssl(self):
        config = django_email_url("smtp:///?ssl=yes")
        self.assertTrue(config["EMAIL_USE_SSL"])
        self.assertFalse(config["EMAIL_USE_TLS"])

        config = django_email_url("smtp:///?tls=yes")
        self.assertTrue(config["EMAIL_USE_TLS"])
        self.assertFalse(config["EMAIL_USE_SSL"])

    def test_parse_locmem(self):
        self.assertEqual(
            django_email_url("locmem://")["EMAIL_BACKEND"],
            "django.core.mail.backends.locmem.EmailBackend",
        )

    def test_parse_console(self):
        self.assertEqual(
            django_email_url("console://")["EMAIL_BACKEND"],
            "django.core.mail.backends.console.EmailBackend",
        )

    def test_parse_dummy(self):
        self.assertEqual(
            django_email_url("dummy://")["EMAIL_BACKEND"],
            "django.core.mail.backends.dummy.EmailBackend",
        )

    def test_parse_unknown(self):
        with self.assertRaises(KeyError):
            django_email_url("unknown://")
