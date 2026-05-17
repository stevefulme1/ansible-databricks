#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: mlflow_registered_model
short_description: Manage MLflow registered models
description:
  - Create, update, or delete MLflow registered models.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Model name.
    type: str
    required: true
  description:
    description: Model description.
    type: str
  tags:
    description: Model tags as key-value pairs.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Register a model
  stevefulme1.databricks.mlflow_registered_model:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-model
    description: Production fraud model
"""

RETURN = r"""
model:
  description: Registered model object.
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
        tags=dict(type="dict"),
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
            client.delete("mlflow/registered-models/delete", params={"name": name})
            module.exit_json(changed=True)

        payload = {"name": name}
        if module.params.get("description"):
            payload["description"] = module.params["description"]

        try:
            existing = client.get("mlflow/registered-models/get", params={"name": name})
            if module.check_mode:
                module.exit_json(
                    changed=True,
                    model=existing.get("registered_model", existing),
                )
            if module.params.get("description"):
                client.patch(
                    "mlflow/registered-models/update",
                    data={"name": name, "description": module.params["description"]},
                )
            info = client.get("mlflow/registered-models/get", params={"name": name})
            module.exit_json(changed=True, model=info.get("registered_model", info))
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post("mlflow/registered-models/create", data=payload)
            module.exit_json(changed=True, model=resp.get("registered_model", resp))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
