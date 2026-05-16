#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: schema_info
short_description: List Unity Catalog schemas
description:
  - List all schemas in a catalog.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  catalog_name:
    description: Catalog to list schemas from.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: List schemas
  stevefulme1.databricks.schema_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    catalog_name: analytics
"""

RETURN = r"""
schemas:
  description: List of schema objects.
  type: list
  elements: dict
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        catalog_name=dict(type="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        resp = client.get(
            "unity-catalog/schemas",
            params={"catalog_name": module.params["catalog_name"]},
            api_version="2.1",
        )
        module.exit_json(changed=False, schemas=resp.get("schemas", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
