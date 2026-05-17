#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mlflow_model_version
short_description: Manage MLflow model versions
description:
  - Create or delete MLflow model versions.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Registered model name.
    type: str
    required: true
  version:
    description: Model version number. Required for absent.
    type: str
  source:
    description: URI of the model artifacts. Required for present.
    type: str
  run_id:
    description: MLflow run ID that generated this version.
    type: str
  description:
    description: Version description.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a model version
  stevefulme1.databricks.mlflow_model_version:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-model
    source: dbfs:/models/my-model/artifacts
"""

RETURN = r"""
model_version:
  description: Model version object.
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
        version=dict(type="str"),
        source=dict(type="str"),
        run_id=dict(type="str"),
        description=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ["version"]),
            ("state", "present", ["source"]),
        ],
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
            client.delete(
                "mlflow/model-versions/delete",
                params={
                    "name": module.params["name"],
                    "version": module.params["version"],
                },
            )
            module.exit_json(changed=True)

        payload = {"name": module.params["name"], "source": module.params["source"]}
        for key in ("run_id", "description"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("mlflow/model-versions/create", data=payload)
        module.exit_json(changed=True, model_version=resp.get("model_version", resp))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
