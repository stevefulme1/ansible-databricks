#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: grant
short_description: Manage Unity Catalog grants
description:
  - Grant or revoke permissions on Unity Catalog securables.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Whether to grant or revoke.
    type: str
    choices: [present, absent]
    default: present
  securable_type:
    description: Type of securable (catalog, schema, table, volume, etc.).
    type: str
    required: true
  securable_name:
    description: Full name of the securable object.
    type: str
    required: true
  principal:
    description: Principal (user, group, or service principal) to grant to.
    type: str
    required: true
  privileges:
    description: List of privileges to grant or revoke.
    type: list
    elements: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Grant SELECT on a table
  stevefulme1.databricks.grant:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    securable_type: table
    securable_name: analytics.bronze.events
    principal: data-readers
    privileges:
      - SELECT
"""

RETURN = r"""
permissions:
  description: Updated permissions.
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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        securable_type=dict(type="str", required=True),
        securable_name=dict(type="str", required=True),
        principal=dict(type="str", required=True),
        privileges=dict(type="list", elements="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    sec_type = module.params["securable_type"]
    sec_name = module.params["securable_name"]
    path = f"unity-catalog/permissions/{sec_type}/{sec_name}"

    changes = [
        {
            "principal": module.params["principal"],
            "add": module.params["privileges"] if module.params["state"] == "present" else [],
            "remove": module.params["privileges"] if module.params["state"] == "absent" else [],
        }
    ]

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.patch(path, data={"changes": changes}, api_version="2.1")
        module.exit_json(changed=True, permissions=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
