#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: budget_policy
short_description: Manage Databricks budget policies
description:
  - Create, update, or delete budget policies.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  policy_id:
    description: Existing policy ID.
    type: str
  policy_name:
    description: Policy name.
    type: str
  custom_tags:
    description: Custom tags for budget filtering.
    type: list
    elements: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a budget policy
  stevefulme1.databricks.budget_policy:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    policy_name: dev-team-budget
    custom_tags:
      - key: team
        value: development
"""

RETURN = r"""
policy:
  description: Budget policy object.
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
        policy_id=dict(type="str"),
        policy_name=dict(type="str"),
        custom_tags=dict(type="list", elements="dict"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["policy_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    policy_id = module.params.get("policy_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"budget-policies/{policy_id}")
            module.exit_json(changed=True)

        payload = {}
        if module.params.get("policy_name"):
            payload["policy_name"] = module.params["policy_name"]
        if module.params.get("custom_tags"):
            payload["custom_tags"] = module.params["custom_tags"]

        if policy_id:
            if module.check_mode:
                module.exit_json(changed=True)
            client.patch(f"budget-policies/{policy_id}", data=payload)
            info = client.get(f"budget-policies/{policy_id}")
            module.exit_json(changed=True, policy=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("budget-policies", data=payload)
        module.exit_json(changed=True, policy=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
