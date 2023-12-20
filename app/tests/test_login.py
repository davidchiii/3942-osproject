import unittest
from unittest import mock

import google.auth.credentials
import google_auth_httplib2
import httplib2

try:
    import oauth2client.client

    HAS_OAUTH2CLIENT = True
except ImportError:
    HAS_OAUTH2CLIENT = False

from googleapiclient import _auth


class TestAuthWithGoogleAuth(unittest.TestCase):
    def setUp(self):
        _auth.HAS_GOOGLE_AUTH = True
        _auth.HAS_OAUTH2CLIENT = False

    def tearDown(self):
        _auth.HAS_GOOGLE_AUTH = True
        _auth.HAS_OAUTH2CLIENT = True

    def test_default_credentials(self):
        with mock.patch("google.auth.default", autospec=True) as default:
            default.return_value = (mock.sentinel.credentials, mock.sentinel.project)

            credentials = _auth.default_credentials()

            self.assertEqual(credentials, mock.sentinel.credentials)

    def test_credentials_from_file(self):
        with mock.patch(
            "google.auth.load_credentials_from_file", autospec=True
        ) as default:
            default.return_value = (mock.sentinel.credentials, mock.sentinel.project)

            credentials = _auth.credentials_from_file("credentials.json")

            self.assertEqual(credentials, mock.sentinel.credentials)
            default.assert_called_once_with(
                "credentials.json", scopes=None, quota_project_id=None
            )

    def test_default_credentials_with_scopes(self):
        with mock.patch("google.auth.default", autospec=True) as default:
            default.return_value = (mock.sentinel.credentials, mock.sentinel.project)
            credentials = _auth.default_credentials(scopes=["1", "2"])

            default.assert_called_once_with(scopes=["1", "2"], quota_project_id=None)
            self.assertEqual(credentials, mock.sentinel.credentials)

    def test_default_credentials_with_quota_project(self):
        with mock.patch("google.auth.default", autospec=True) as default:
            default.return_value = (mock.sentinel.credentials, mock.sentinel.project)
            credentials = _auth.default_credentials(quota_project_id="my-project")

            default.assert_called_once_with(scopes=None, quota_project_id="my-project")
            self.assertEqual(credentials, mock.sentinel.credentials)

    def test_with_scopes_non_scoped(self):
        credentials = mock.Mock(spec=google.auth.credentials.Credentials)

        returned = _auth.with_scopes(credentials, mock.sentinel.scopes)

        self.assertEqual(credentials, returned)

    def test_with_scopes_scoped(self):
        class CredentialsWithScopes(
            google.auth.credentials.Credentials, google.auth.credentials.Scoped
        ):
            pass

        credentials = mock.Mock(spec=CredentialsWithScopes)
        credentials.requires_scopes = True

        returned = _auth.with_scopes(credentials, mock.sentinel.scopes)

        self.assertNotEqual(credentials, returned)
        self.assertEqual(returned, credentials.with_scopes.return_value)
        credentials.with_scopes.assert_called_once_with(
            mock.sentinel.scopes, default_scopes=None
        )

    def test_authorized_http(self):
        credentials = mock.Mock(spec=google.auth.credentials.Credentials)

        authorized_http = _auth.authorized_http(credentials)

        self.assertIsInstance(authorized_http, google_auth_httplib2.AuthorizedHttp)
        self.assertEqual(authorized_http.credentials, credentials)
        self.assertIsInstance(authorized_http.http, httplib2.Http)
        self.assertIsInstance(authorized_http.http.timeout, int)
        self.assertGreater(authorized_http.http.timeout, 0)
