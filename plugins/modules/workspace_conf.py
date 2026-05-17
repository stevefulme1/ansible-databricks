#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: workspace_conf
short_description: Manage Databricks workspace configuration
description:
  - Get or set workspace-level configuration flags.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  keys:
    description: List of configuration keys to retrieve (for info mode).
    type: list
    elements: str
  config:
    description: Dict of configuration key-value pairs to set.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Enable table access control
  stevefulme1.databricks.workspace_conf:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    config:
      enableTableAccessControl: "true"

- name: Read workspace config
  stevefulme1.databricks.workspace_conf:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    keys:
      - enableTableAccessControl
"""

RETURN = r"""
configuration:
  description: Current configuration values.
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
        keys=dict(type="list", elements="str", no_log=False),
        config=dict(type="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.params.get("config"):
            if module.check_mode:
                module.exit_json(changed=True)
            client.patch("workspace-conf", data=module.params["config"])
            # Read back the keys we just set
            resp = client.get(
                "workspace-conf",
                params={
                    "keys": ",".join(module.params["config"].keys()),
                },
            )
            module.exit_json(changed=True, configuration=resp)

        if module.params.get("keys"):
            resp = client.get(
                "workspace-conf",
                params={
                    "keys": ",".join(module.params["keys"]),
                },
            )
            module.exit_json(changed=False, configuration=resp)

        module.exit_json(changed=False, configuration={})

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
