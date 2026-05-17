#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: app
short_description: Manage Databricks Apps
description:
  - Create, update, or delete Databricks Apps.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: App name.
    type: str
    required: true
  description:
    description: App description.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an app
  stevefulme1.databricks.app:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-dashboard-app
    description: Internal dashboard application
"""

RETURN = r"""
app:
  description: App object.
  type: dict
  returned: when state is present
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
        name=dict(type="str", required=True),
        description=dict(type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    name = module.params["name"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"apps/{name}")
            module.exit_json(changed=True)

        payload = {"name": name}
        if module.params.get("description"):
            payload["description"] = module.params["description"]

        try:
            existing = client.get(f"apps/{name}")
            if module.check_mode:
                module.exit_json(changed=True, app=existing)
            client.patch(f"apps/{name}", data=payload)
            info = client.get(f"apps/{name}")
            module.exit_json(changed=True, app=info)
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post("apps", data=payload)
            module.exit_json(changed=True, app=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
