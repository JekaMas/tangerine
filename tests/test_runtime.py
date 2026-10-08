"""Actual local runtime checks; no substituted database/media/provider owner.

Run explicitly only after Compose readiness, with TANGERINE_RUN_LIVE=1. The
configured bootstrap account is the real local owner, not a reviewer signature.
No published exercise, answer or human annotation is created by this suite.
"""
import http.cookiejar
import json
import os
from pathlib import Path
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'http://localhost:3000'


@unittest.skipUnless(os.environ.get('TANGERINE_RUN_LIVE') == '1', 'Actual Compose runtime not selected')
class RuntimeTests(unittest.TestCase):
    def setUp(self):
        values = dict(line.split('=', 1) for line in (ROOT / 'deploy/local/.env').read_text().splitlines()
                      if line and not line.startswith('#'))
        self.email = values['INITIAL_EMAIL']
        self.password = values['INITIAL_PASSWORD']
        self.cookies = http.cookiejar.CookieJar()
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))

    def call(self, path, *, payload=None, method='GET', origin=ORIGIN):
        headers = {'Origin': origin}
        data = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload).encode()
        request = urllib.request.Request(ORIGIN + path, data=data, method=method, headers=headers)
        try:
            response = self.client.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def login(self):
        status, data = self.call('/api/auth/login', method='POST',
                                 payload={'email': self.email, 'password': self.password})
        self.assertEqual(status, 200)
        self.assertEqual(data['status'], 'authenticated')

    def test_authentication_positive(self):
        self.login()
        status, data = self.call('/api/auth/session')
        self.assertEqual(status, 200)
        self.assertEqual(data, {'email': self.email})
        cookie = next(iter(self.cookies))
        self.assertEqual(cookie.name, 'tangerine_session')
        self.assertTrue(cookie.has_nonstandard_attr('HttpOnly'))
        self.assertEqual(cookie.get_nonstandard_attr('SameSite'), 'Strict')

    def test_authentication_negative(self):
        status, data = self.call('/api/auth/login', method='POST',
                                 payload={'email': self.email, 'password': 'deliberately-wrong-local-password'})
        self.assertEqual(status, 401)
        self.assertEqual(data['error'], 'invalid_credentials')
        self.login()
        self.assertEqual(self.call('/api/auth/logout', method='POST')[0], 200)
        self.assertEqual(self.call('/api/auth/session')[0], 401)

    def test_library_empty_positive(self):
        self.login()
        status, data = self.call('/api/exercises')
        self.assertEqual(status, 200)
        self.assertEqual(data, {'exercises': []})

    def test_library_access_negative(self):
        status, data = self.call('/api/exercises')
        self.assertEqual(status, 401)
        self.assertEqual(data['error'], 'authentication_required')

    def test_origin_positive(self):
        self.login()
        self.assertEqual(self.call('/api/auth/logout', method='POST')[0], 200)

    def test_origin_negative(self):
        self.assertEqual(self.call('/api/auth/login', method='POST', origin='http://untrusted.invalid',
                                  payload={'email': self.email, 'password': self.password})[0], 403)
        self.assertEqual(self.call('/api/ground-truth')[0], 404)

    def test_ready_positive(self):
        self.assertEqual(self.call('/health/ready')[0], 200)

    def test_secret_and_unimplemented_routes_negative(self):
        self.login()
        _, data = self.call('/api/auth/session')
        self.assertNotIn('password', data)
        self.assertNotIn('password_hash', data)
        self.assertNotIn('token', data)
        self.assertEqual(self.call('/api/attempts', method='POST', payload={})[0], 404)


if __name__ == '__main__':
    unittest.main()
