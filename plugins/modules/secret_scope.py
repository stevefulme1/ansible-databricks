#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: secret_scope
short_description: Manage Databricks secret scopes
description:
  - Create or delete secret scopes.
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
  initial_manage_principal:
    description: Initial principal that can manage the scope.
    type: str
    default: users
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a secret scope
  stevefulme1.databricks.secret_scope:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    scope: my-scope
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


def scope_exists(client, scope_name):
    """Check if a scope already exists."""
    resp = client.get("secrets/scopes/list")
    for s in resp.get("scopes", []):
        if s.get("name") == scope_name:
            return True
    return False


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        scope=dict(type="str", required=True),
        initial_manage_principal=dict(type="str", default="users"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    scope_name = module.params["scope"]

    try:
        exists = scope_exists(client, scope_name)

        if state == "absent":
            if not exists:
                module.exit_json(changed=False, msg="Scope does not exist")
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("secrets/scopes/delete", data={"scope": scope_name})
            module.exit_json(changed=True, msg="Scope deleted")

        if exists:
            module.exit_json(changed=False, msg="Scope already exists")

        if module.check_mode:
            module.exit_json(changed=True)
        client.post(
            "secrets/scopes/create",
            data={
                "scope": scope_name,
                "initial_manage_principal": module.params["initial_manage_principal"],
            },
        )
        module.exit_json(changed=True, msg="Scope created")

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
