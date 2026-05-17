#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: delta_share
short_description: Manage Databricks Delta Sharing shares
description:
  - Create, update, or delete Delta Sharing shares.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Share name.
    type: str
    required: true
  comment:
    description: Share description.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a share
  stevefulme1.databricks.delta_share:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: analytics-share
    comment: Share for analytics team
"""

RETURN = r"""
share:
  description: Share object.
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
            client.delete(f"unity-catalog/shares/{name}")
            module.exit_json(changed=True)

        payload = {"name": name}
        if module.params.get("comment"):
            payload["comment"] = module.params["comment"]

        try:
            existing = client.get(f"unity-catalog/shares/{name}")
            if module.check_mode:
                module.exit_json(changed=True, share=existing)
            client.patch(f"unity-catalog/shares/{name}", data=payload)
            info = client.get(f"unity-catalog/shares/{name}")
            module.exit_json(changed=True, share=info)
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post("unity-catalog/shares", data=payload)
            module.exit_json(changed=True, share=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
