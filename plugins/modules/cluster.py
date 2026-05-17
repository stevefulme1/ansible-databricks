#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: cluster
short_description: Manage Databricks clusters
description:
  - Create, edit, start, terminate, or permanently delete Databricks clusters.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state of the cluster.
    type: str
    choices: [present, absent, started, terminated]
    default: present
  cluster_id:
    description: Existing cluster ID. Required for edit, absent, started, terminated.
    type: str
  cluster_name:
    description: Human-readable cluster name.
    type: str
  spark_version:
    description: Spark runtime version key.
    type: str
  node_type_id:
    description: Node type for worker and driver nodes.
    type: str
  num_workers:
    description: Fixed number of workers.
    type: int
  autoscale:
    description: Autoscale configuration with min_workers and max_workers.
    type: dict
  spark_conf:
    description: Spark configuration key-value pairs.
    type: dict
  autotermination_minutes:
    description: Idle minutes before auto-termination.
    type: int
  custom_tags:
    description: Custom tags as key-value pairs.
    type: dict
  cluster_policy_id:
    description: Cluster policy ID to apply.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a cluster
  stevefulme1.databricks.cluster:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    cluster_name: my-cluster
    spark_version: "13.3.x-scala2.12"
    node_type_id: Standard_DS3_v2
    num_workers: 2

- name: Terminate a cluster
  stevefulme1.databricks.cluster:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    cluster_id: 0101-010101-abcde123
    state: terminated
"""

RETURN = r"""
cluster:
  description: Cluster object returned by the API.
  type: dict
  returned: when state is present or started
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.databricks.plugins.module_utils.databricks_client import (
    DatabricksClient,
    DatabricksError,
    databricks_argument_spec,
)


def find_cluster_by_name(client, name):
    """Return the first cluster matching *name*, or None."""
    resp = client.get("clusters/list")
    for c in resp.get("clusters", []):
        if c.get("cluster_name") == name:
            return c
    return None


def main():
    argument_spec = databricks_argument_spec()
    argument_spec.update(
        state=dict(
            type="str",
            default="present",
            choices=["present", "absent", "started", "terminated"],
        ),
        cluster_id=dict(type="str"),
        cluster_name=dict(type="str"),
        spark_version=dict(type="str"),
        node_type_id=dict(type="str"),
        num_workers=dict(type="int"),
        autoscale=dict(type="dict"),
        spark_conf=dict(type="dict"),
        autotermination_minutes=dict(type="int"),
        custom_tags=dict(type="dict"),
        cluster_policy_id=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ["cluster_id"]),
            ("state", "terminated", ["cluster_id"]),
            ("state", "started", ["cluster_id"]),
        ],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    cluster_id = module.params.get("cluster_id")
    cluster_name = module.params.get("cluster_name")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("clusters/permanent-delete", data={"cluster_id": cluster_id})
            module.exit_json(changed=True)

        if state == "terminated":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("clusters/delete", data={"cluster_id": cluster_id})
            module.exit_json(changed=True)

        if state == "started":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("clusters/start", data={"cluster_id": cluster_id})
            info = client.get("clusters/get", params={"cluster_id": cluster_id})
            module.exit_json(changed=True, cluster=info)

        # state == present
        payload = {}
        for key in (
            "cluster_name",
            "spark_version",
            "node_type_id",
            "num_workers",
            "autoscale",
            "spark_conf",
            "autotermination_minutes",
            "custom_tags",
            "cluster_policy_id",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        existing = None
        if cluster_id:
            existing = client.get("clusters/get", params={"cluster_id": cluster_id})
        elif cluster_name:
            existing = find_cluster_by_name(client, cluster_name)

        if existing:
            payload["cluster_id"] = existing["cluster_id"]
            if module.check_mode:
                module.exit_json(changed=True, cluster=existing)
            client.post("clusters/edit", data=payload)
            info = client.get("clusters/get", params={"cluster_id": existing["cluster_id"]})
            module.exit_json(changed=True, cluster=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("clusters/create", data=payload)
        info = client.get("clusters/get", params={"cluster_id": resp["cluster_id"]})
        module.exit_json(changed=True, cluster=info)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
