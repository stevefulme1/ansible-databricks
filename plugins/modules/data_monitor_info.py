#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: data_monitor_info
short_description: Get Lakehouse monitor details
description:
  - Retrieve details of a Lakehouse monitor.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  table_name:
    description: Full table name (catalog.schema.table).
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
- name: Get monitor details
  stevefulme1.databricks.data_monitor_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    table_name: catalog.schema.my_table
"""

RETURN = r"""
monitor:
  description: Monitor details.
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
        table_name=dict(type="str", required=True),
    )
    argument_spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        info = client.get("unity-catalog/tables/{}/monitor".format(module.params["table_name"]))
        module.exit_json(changed=False, monitor=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
