# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock

from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


class TestDatabricksArgumentSpec:
    """Verify the shared argument spec exposes required options."""

    def test_has_host(self):
        spec = databricks_argument_spec()
        assert "host" in spec

    def test_has_token(self):
        spec = databricks_argument_spec()
        assert "token" in spec

    def test_has_validate_certs(self):
        spec = databricks_argument_spec()
        assert "validate_certs" in spec

    def test_token_is_no_log(self):
        spec = databricks_argument_spec()
        assert spec["token"].get("no_log") is True


class TestDatabricksClient:
    """Basic DatabricksClient construction tests."""

    def test_init_stores_host(self):
        client = DatabricksClient(
            host="https://example.cloud.databricks.com", token="tok"
        )
        assert client.host == "https://example.cloud.databricks.com"

    def test_init_strips_trailing_slash(self):
        client = DatabricksClient(
            host="https://example.cloud.databricks.com/", token="tok"
        )
        assert not client.host.endswith("/")

    def test_init_stores_token(self):
        client = DatabricksClient(
            host="https://example.cloud.databricks.com", token="dapi-xyz"
        )
        assert client.token == "dapi-xyz"

    def test_init_with_mock_module(self):
        module = MagicMock()
        module.params = {
            "host": "https://db.example.com",
            "token": "dapi-test",
            "validate_certs": True,
        }
        client = DatabricksClient(
            host=module.params["host"],
            token=module.params["token"],
            validate_certs=module.params["validate_certs"],
        )
        assert client.host == "https://db.example.com"
        assert client.validate_certs is True


class TestDatabricksError:
    """Verify DatabricksError carries the expected message."""

    def test_message(self):
        err = DatabricksError("something went wrong")
        assert str(err) == "something went wrong"

    def test_status_code(self):
        err = DatabricksError("fail", status_code=404)
        assert err.status_code == 404

    def test_error_code(self):
        err = DatabricksError("fail", error_code="RESOURCE_NOT_FOUND")
        assert err.error_code == "RESOURCE_NOT_FOUND"
