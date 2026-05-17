#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: sql_warehouse_stop
short_description: Stop a Databricks SQL warehouse
description:
  - Stop a running SQL warehouse.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  warehouse_id:
    description: The warehouse ID to stop.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Stop a SQL warehouse
  stevefulme1.databricks.sql_warehouse_stop:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    warehouse_id: abc123def456
"""

RETURN = r"""
warehouse:
  description: Warehouse details after stopping.
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

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    wid = module.params["warehouse_id"]
    try:
        if module.check_mode:
            module.exit_json(changed=True)
        client.post(f"sql/warehouses/{wid}/stop")
        info = client.get(f"sql/warehouses/{wid}")
        module.exit_json(changed=True, warehouse=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
