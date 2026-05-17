#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: cluster_policy
short_description: Manage Databricks cluster policies
description:
  - Create, update, or delete cluster policies.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state of the policy.
    type: str
    choices: [present, absent]
    default: present
  policy_id:
    description: Existing policy ID. Required for updates and deletes.
    type: str
  name:
    description: Policy name.
    type: str
  definition:
    description: Policy definition as a JSON-compatible dict.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a cluster policy
  stevefulme1.databricks.cluster_policy:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: cost-optimized
    definition:
      node_type_id:
        type: fixed
        value: Standard_DS3_v2
"""

RETURN = r"""
policy:
  description: The cluster policy object.
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
        name=dict(type="str"),
        definition=dict(type="dict"),
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
            client.post("policies/clusters/delete", data={"policy_id": policy_id})
            module.exit_json(changed=True)

        import json as _json

        payload = {}
        if module.params.get("name"):
            payload["name"] = module.params["name"]
        if module.params.get("definition"):
            payload["definition"] = _json.dumps(module.params["definition"])

        if policy_id:
            payload["policy_id"] = policy_id
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("policies/clusters/edit", data=payload)
            resp = client.get("policies/clusters/get", params={"policy_id": policy_id})
            module.exit_json(changed=True, policy=resp)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("policies/clusters/create", data=payload)
        policy = client.get("policies/clusters/get", params={"policy_id": resp["policy_id"]})
        module.exit_json(changed=True, policy=policy)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
