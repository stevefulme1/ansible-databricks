#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: sql_warehouse
short_description: Manage Databricks SQL warehouses
description:
  - Create, update, or delete a Databricks SQL warehouse.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state of the warehouse.
    type: str
    choices: [present, absent]
    default: present
  warehouse_id:
    description: Existing warehouse ID.
    type: str
  name:
    description: Warehouse display name.
    type: str
  cluster_size:
    description: T-shirt size of the warehouse cluster.
    type: str
  min_num_clusters:
    description: Minimum number of clusters.
    type: int
  max_num_clusters:
    description: Maximum number of clusters.
    type: int
  auto_stop_mins:
    description: Auto-stop idle minutes.
    type: int
  warehouse_type:
    description: Type of warehouse.
    type: str
    choices: [PRO, CLASSIC]
  enable_serverless_compute:
    description: Enable serverless compute.
    type: bool
  channel:
    description: Release channel for the warehouse.
    type: str
    choices: [CHANNEL_NAME_CURRENT, CHANNEL_NAME_PREVIEW]
  tags:
    description: Custom tags as key-value pairs.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a SQL warehouse
  stevefulme1.databricks.sql_warehouse:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: analytics-warehouse
    cluster_size: Small
    max_num_clusters: 2

- name: Delete a SQL warehouse
  stevefulme1.databricks.sql_warehouse:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    warehouse_id: abc123def456
    state: absent
"""

RETURN = r"""
warehouse:
  description: Warehouse object returned by the API.
  type: dict
  returned: when state is present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def find_warehouse_by_name(client, name):
    """Return the first warehouse matching *name*, or None."""
    resp = client.get("sql/warehouses")
    for w in resp.get("warehouses", []):
        if w.get("name") == name:
            return w
    return None


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        warehouse_id=dict(type="str"),
        name=dict(type="str"),
        cluster_size=dict(type="str"),
        min_num_clusters=dict(type="int"),
        max_num_clusters=dict(type="int"),
        auto_stop_mins=dict(type="int"),
        warehouse_type=dict(type="str", choices=["PRO", "CLASSIC"]),
        enable_serverless_compute=dict(type="bool"),
        channel=dict(
            type="str",
            choices=["CHANNEL_NAME_CURRENT", "CHANNEL_NAME_PREVIEW"],
        ),
        tags=dict(type="dict"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["warehouse_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    warehouse_id = module.params.get("warehouse_id")
    name = module.params.get("name")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"sql/warehouses/{warehouse_id}")
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "name",
            "cluster_size",
            "min_num_clusters",
            "max_num_clusters",
            "auto_stop_mins",
            "warehouse_type",
            "enable_serverless_compute",
            "channel",
            "tags",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        existing = None
        if warehouse_id:
            existing = client.get(f"sql/warehouses/{warehouse_id}")
        elif name:
            existing = find_warehouse_by_name(client, name)

        if existing:
            wid = existing["id"]
            if module.check_mode:
                module.exit_json(changed=True, warehouse=existing)
            client.post(f"sql/warehouses/{wid}/edit", data=payload)
            info = client.get(f"sql/warehouses/{wid}")
            module.exit_json(changed=True, warehouse=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("sql/warehouses", data=payload)
        info = client.get("sql/warehouses/{}".format(resp["id"]))
        module.exit_json(changed=True, warehouse=info)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
