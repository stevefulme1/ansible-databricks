# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Databricks REST API client and shared argument spec."""

import json

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url


class DatabricksError(Exception):
    """Exception raised by Databricks API calls."""

    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class DatabricksClient:
    """REST client for the Databricks API."""

    def __init__(self, host, token, validate_certs=True, timeout=30):
        self.host = host.rstrip("/")
        self.token = token
        self.validate_certs = validate_certs
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path, api_version="2.0"):
        """Build a full URL for *path* under the given API version."""
        path = path.lstrip("/")
        return f"{self.host}/api/{api_version}/{path}"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method, url, data=None, params=None):
        """Send an HTTP request and return the parsed JSON response."""
        if params:
            url = f"{url}?{urlencode(params)}"

        body = json.dumps(data) if data is not None else None

        try:
            resp = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                validate_certs=self.validate_certs,
                timeout=self.timeout,
            )
            raw = resp.read()
            if raw:
                return json.loads(raw)
            return {}
        except HTTPError as e:
            try:
                detail = json.loads(e.read())
                msg = detail.get("message", str(e))
                error_code = detail.get("error_code", "UNKNOWN")
            except Exception:
                msg = str(e)
                error_code = "UNKNOWN"
            raise DatabricksError(msg, status_code=e.code, error_code=error_code)
        except URLError as e:
            raise DatabricksError(f"Connection error: {str(e)}")

    # ------------------------------------------------------------------
    # Public HTTP verbs
    # ------------------------------------------------------------------

    def get(self, path, params=None, api_version="2.0"):
        """HTTP GET."""
        return self._request("GET", self._url(path, api_version), params=params)

    def post(self, path, data=None, api_version="2.0"):
        """HTTP POST."""
        return self._request("POST", self._url(path, api_version), data=data)

    def put(self, path, data=None, api_version="2.0"):
        """HTTP PUT."""
        return self._request("PUT", self._url(path, api_version), data=data)

    def patch(self, path, data=None, api_version="2.0"):
        """HTTP PATCH."""
        return self._request("PATCH", self._url(path, api_version), data=data)

    def delete(self, path, data=None, api_version="2.0"):
        """HTTP DELETE."""
        return self._request("DELETE", self._url(path, api_version), data=data)

    def list_paginated(
        self,
        path,
        params=None,
        api_version="2.0",
        results_key=None,
        token_key="next_page_token",
        token_param="page_token",
    ):
        """Auto-paginate a list endpoint that uses page tokens.

        *results_key* is the JSON key containing the list of items.  When
        ``None``, the full response dict is yielded on each page (useful when
        the caller needs to inspect sibling keys).
        """
        params = dict(params) if params else {}
        while True:
            resp = self.get(path, params=params, api_version=api_version)
            if results_key:
                yield from resp.get(results_key, [])
            else:
                yield resp

            next_token = resp.get(token_key)
            if not next_token:
                break
            params[token_param] = next_token


def databricks_argument_spec():
    """Return the common argument spec shared by all Databricks modules."""
    return dict(
        host=dict(type="str", required=True),
        token=dict(type="str", required=True, no_log=True),
        validate_certs=dict(type="bool", default=True),
    )
