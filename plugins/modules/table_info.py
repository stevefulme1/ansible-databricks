#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: table_info
short_description: List or describe Unity Catalog tables
description:
  - List tables in a schema or get details of a specific table.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  catalog_name:
    description: Catalog name.
    type: str
    required: true
  schema_name:
    description: Schema name.
    type: str
    required: true
  table_name:
    description: Specific table name. If omitted, all tables are listed.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
"""

EXAMPLES = r"""
- name: List tables in a schema
  stevefulme1.databricks.table_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    catalog_name: analytics
    schema_name: bronze
"""

RETURN = r"""
tables:
  description: List of tables (when table_name is omitted).
  type: list
  elements: dict
  returned: when table_name is not specified
table:
  description: Single table details.
  type: dict
  returned: when table_name is specified
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
        schema_name=dict(type="str", required=True),
        table_name=dict(type="str"),
    )
    argument_spec.update(
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.params.get("table_name"):
            full_name = "{0}.{1}.{2}".format(
                module.params["catalog_name"],
                module.params["schema_name"],
                module.params["table_name"],
            )
            table = client.get(
                "unity-catalog/tables/{0}".format(full_name), api_version="2.1"
            )
            module.exit_json(changed=False, table=table)

        resp = client.get(
            "unity-catalog/tables",
            params={
                "catalog_name": module.params["catalog_name"],
                "schema_name": module.params["schema_name"],
            },
            api_version="2.1",
        )
        module.exit_json(changed=False, tables=resp.get("tables", []))

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
