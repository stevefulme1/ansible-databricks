#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: secret
short_description: Manage Databricks secrets
description:
  - Put or delete secrets in a secret scope.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  scope:
    description: Secret scope name.
    type: str
    required: true
  key:
    description: Secret key name.
    type: str
    required: true
  string_value:
    description: Secret value as a string.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Set a secret
  stevefulme1.databricks.secret:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    scope: my-scope
    key: db-password
    string_value: supersecret
"""

RETURN = r"""
msg:
  description: Result message.
  type: str
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
        scope=dict(type="str", required=True),
        key=dict(type="str", required=True, no_log=False),
        string_value=dict(type="str", no_log=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["string_value"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post(
                "secrets/delete",
                data={
                    "scope": module.params["scope"],
                    "key": module.params["key"],
                },
            )
            module.exit_json(changed=True, msg="Secret deleted")

        if module.check_mode:
            module.exit_json(changed=True)
        client.post(
            "secrets/put",
            data={
                "scope": module.params["scope"],
                "key": module.params["key"],
                "string_value": module.params["string_value"],
            },
        )
        module.exit_json(changed=True, msg="Secret set")

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
