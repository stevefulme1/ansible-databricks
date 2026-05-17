#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: mlflow_experiment
short_description: Manage MLflow experiments
description:
  - Create, update, or delete MLflow experiments in Databricks.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  experiment_id:
    description: Existing experiment ID.
    type: str
  name:
    description: Experiment name (unique path).
    type: str
  artifact_location:
    description: Default artifact storage location.
    type: str
  tags:
    description: Experiment tags as key-value pairs.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an MLflow experiment
  stevefulme1.databricks.mlflow_experiment:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: /Users/user@example.com/my-experiment

- name: Delete an experiment
  stevefulme1.databricks.mlflow_experiment:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    experiment_id: "12345"
    state: absent
"""

RETURN = r"""
experiment:
  description: Experiment object.
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
        experiment_id=dict(type="str"),
        name=dict(type="str"),
        artifact_location=dict(type="str"),
        tags=dict(type="dict"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["experiment_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    experiment_id = module.params.get("experiment_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post(
                "mlflow/experiments/delete",
                data={"experiment_id": experiment_id},
            )
            module.exit_json(changed=True)

        if experiment_id:
            if module.check_mode:
                module.exit_json(changed=True)
            payload = {"experiment_id": experiment_id}
            if module.params.get("name"):
                client.post(
                    "mlflow/experiments/update",
                    data={
                        "experiment_id": experiment_id,
                        "new_name": module.params["name"],
                    },
                )
            info = client.get("mlflow/experiments/get", params={"experiment_id": experiment_id})
            module.exit_json(changed=True, experiment=info.get("experiment", info))

        payload = {"name": module.params["name"]}
        if module.params.get("artifact_location"):
            payload["artifact_location"] = module.params["artifact_location"]
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("mlflow/experiments/create", data=payload)
        eid = resp.get("experiment_id", "")
        if module.params.get("tags"):
            for k, v in module.params["tags"].items():
                client.post(
                    "mlflow/experiments/set-experiment-tag",
                    data={"experiment_id": eid, "key": k, "value": v},
                )
        info = client.get("mlflow/experiments/get", params={"experiment_id": eid})
        module.exit_json(changed=True, experiment=info.get("experiment", info))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
