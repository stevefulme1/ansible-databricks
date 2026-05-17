#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: instance_pool
short_description: Manage Databricks instance pools
description:
  - Create, edit, or delete instance pools.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  instance_pool_id:
    description: Existing pool ID. Required for edit and delete.
    type: str
  instance_pool_name:
    description: Pool name.
    type: str
  node_type_id:
    description: Node type for the pool.
    type: str
  min_idle_instances:
    description: Minimum idle instances to keep ready.
    type: int
    default: 0
  max_capacity:
    description: Maximum number of instances in the pool.
    type: int
  idle_instance_autotermination_minutes:
    description: Minutes before idle instances are terminated.
    type: int
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an instance pool
  stevefulme1.databricks.instance_pool:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    instance_pool_name: gpu-pool
    node_type_id: Standard_NC6
    min_idle_instances: 1
"""

RETURN = r"""
instance_pool:
  description: Instance pool object.
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
        instance_pool_id=dict(type="str"),
        instance_pool_name=dict(type="str"),
        node_type_id=dict(type="str"),
        min_idle_instances=dict(type="int", default=0),
        max_capacity=dict(type="int"),
        idle_instance_autotermination_minutes=dict(type="int"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["instance_pool_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    pool_id = module.params.get("instance_pool_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("instance-pools/delete", data={"instance_pool_id": pool_id})
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "instance_pool_name",
            "node_type_id",
            "min_idle_instances",
            "max_capacity",
            "idle_instance_autotermination_minutes",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if pool_id:
            payload["instance_pool_id"] = pool_id
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("instance-pools/edit", data=payload)
            info = client.get("instance-pools/get", params={"instance_pool_id": pool_id})
            module.exit_json(changed=True, instance_pool=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("instance-pools/create", data=payload)
        info = client.get("instance-pools/get", params={"instance_pool_id": resp["instance_pool_id"]})
        module.exit_json(changed=True, instance_pool=info)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
