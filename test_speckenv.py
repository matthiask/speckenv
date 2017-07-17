from __future__ import unicode_literals

import os
import speckenv
import tempfile
from unittest import TestCase


class EnvTestCase(TestCase):
    def test_read(self):
        self.assertNotIn(
            'ALLOWED_HOSTS',
            os.environ,
        )

        with tempfile.NamedTemporaryFile() as f:
            f.write(b'''
DATABASE_URL=postgres://localhost:5432/example_com
ALLOWED_HOSTS=['*']

# COMMENTED=yes
COMMENTED=no
COMMENTED=ignored
''')

            f.seek(0)

            speckenv.read_speckenv(f.name)

        # Bare value
        self.assertEqual(
            os.environ.get('ALLOWED_HOSTS'),
            "['*']",
        )

        # literal_eval'ed value
        self.assertEqual(
            speckenv.env('ALLOWED_HOSTS'),
            ['*'],
        )

        # First not-commented out value
        self.assertEqual(
            speckenv.env('COMMENTED'),
            'no',
        )

        # Not defined values
        self.assertEqual(
            speckenv.env('UNDEFINED'),
            None,
        )
        self.assertRaises(
            Exception,
            speckenv.env,
            'UNDEFINED',
            required=True,
        )

        # Defaults
        self.assertEqual(
            speckenv.env('DEFAULT'),
            None,
        )
        self.assertEqual(
            speckenv.env('DEFAULT', default=42),
            42,
        )
        self.assertEqual(
            speckenv.env('COMMENTED', default=42),
            'no',
        )


class CustomMappingTestCase(TestCase):
    def test_custom_mapping(self):
        mapping = {}
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'''
CUSTOM_MAPPING=yes
''')

            f.seek(0)

            speckenv.read_speckenv(f.name, mapping=mapping)

        self.assertNotIn(
            'CUSTOM_MAPPING',
            os.environ,
        )

        self.assertEqual(
            speckenv.env('CUSTOM_MAPPING', mapping=mapping),
            'yes',
        )
