#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: sql_warehouse_info
short_description: Get Databricks SQL warehouse details
description:
  - Retrieve detailed information about a specific SQL warehouse.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  warehouse_id:
    description: The warehouse ID to query.
    type: str
    required: true

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
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get warehouse details
  stevefulme1.databricks.sql_warehouse_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    warehouse_id: abc123def456
"""

RETURN = r"""
warehouse:
  description: Warehouse details.
  type: dict
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
        warehouse_id=dict(type="str", required=True),
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
        info = client.get("sql/warehouses/{0}".format(module.params["warehouse_id"]))
        module.exit_json(changed=False, warehouse=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
