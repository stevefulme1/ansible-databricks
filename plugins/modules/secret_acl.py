#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: secret_acl
short_description: Manage Databricks secret ACLs
description:
  - Set or delete ACLs on a secret scope.
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
  principal:
    description: Principal (user or group) to grant.
    type: str
    required: true
  permission:
    description: Permission level.
    type: str
    choices: [READ, WRITE, MANAGE]
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Grant READ on a scope
  stevefulme1.databricks.secret_acl:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    scope: my-scope
    principal: data-readers
    permission: READ
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
        principal=dict(type="str", required=True),
        permission=dict(type="str", choices=["READ", "WRITE", "MANAGE"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["permission"])],
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
                "secrets/acls/delete",
                data={
                    "scope": module.params["scope"],
                    "principal": module.params["principal"],
                },
            )
            module.exit_json(changed=True, msg="ACL deleted")

        if module.check_mode:
            module.exit_json(changed=True)
        client.post(
            "secrets/acls/put",
            data={
                "scope": module.params["scope"],
                "principal": module.params["principal"],
                "permission": module.params["permission"],
            },
        )
        module.exit_json(changed=True, msg="ACL set")

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
