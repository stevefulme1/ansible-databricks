#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: sql_warehouse_config
short_description: Manage global SQL warehouse configuration
description:
  - Get or set the global configuration for SQL warehouses.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  security_policy:
    description: Security policy for warehouses.
    type: str
    choices: [DATA_ACCESS_CONTROL, PASSTHROUGH, NONE]
  data_access_config:
    description: Data access configuration key-value pairs.
    type: list
    elements: dict
  sql_configuration_parameters:
    description: Global SQL configuration parameters.
    type: dict
  enable_serverless_compute:
    description: Enable serverless compute globally.
    type: bool
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Set global warehouse config
  stevefulme1.databricks.sql_warehouse_config:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    security_policy: DATA_ACCESS_CONTROL
"""

RETURN = r"""
config:
  description: Global warehouse configuration.
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
        security_policy=dict(
            type="str",
            choices=["DATA_ACCESS_CONTROL", "PASSTHROUGH", "NONE"],
        ),
        data_access_config=dict(type="list", elements="dict"),
        sql_configuration_parameters=dict(type="dict"),
        enable_serverless_compute=dict(type="bool"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        payload = {}
        for key in (
            "security_policy",
            "data_access_config",
            "sql_configuration_parameters",
            "enable_serverless_compute",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if not payload:
            config = client.get("sql/config/warehouses")
            module.exit_json(changed=False, config=config)

        if module.check_mode:
            module.exit_json(changed=True)
        client.put("sql/config/warehouses", data=payload)
        config = client.get("sql/config/warehouses")
        module.exit_json(changed=True, config=config)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
