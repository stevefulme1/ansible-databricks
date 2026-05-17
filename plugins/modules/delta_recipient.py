#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: delta_recipient
short_description: Manage Delta Sharing recipients
description:
  - Create, update, or delete Delta Sharing recipients.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Recipient name.
    type: str
    required: true
  comment:
    description: Recipient description.
    type: str
  authentication_type:
    description: Authentication type.
    type: str
    choices: [TOKEN, DATABRICKS]
  sharing_code:
    description: One-time sharing code for TOKEN auth.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a recipient
  stevefulme1.databricks.delta_recipient:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: partner-team
    authentication_type: TOKEN
"""

RETURN = r"""
recipient:
  description: Recipient object.
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
        comment=dict(type="str"),
        authentication_type=dict(type="str", choices=["TOKEN", "DATABRICKS"]),
        sharing_code=dict(type="str", no_log=False),
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
            client.delete(f"unity-catalog/recipients/{name}")
            module.exit_json(changed=True)

        payload = {"name": name}
        for key in ("comment", "authentication_type", "sharing_code"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        try:
            existing = client.get(f"unity-catalog/recipients/{name}")
            if module.check_mode:
                module.exit_json(changed=True, recipient=existing)
            client.patch(f"unity-catalog/recipients/{name}", data=payload)
            info = client.get(f"unity-catalog/recipients/{name}")
            module.exit_json(changed=True, recipient=info)
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post("unity-catalog/recipients", data=payload)
            module.exit_json(changed=True, recipient=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
