#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: mlflow_model_version_info
short_description: Get MLflow model version details
description:
  - Retrieve details of a specific model version.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: Registered model name.
    type: str
    required: true
  version:
    description: Model version number.
    type: str
    required: true

  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get model version details
  stevefulme1.databricks.mlflow_model_version_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-model
    version: "1"
"""

RETURN = r"""
model_version:
  description: Model version details.
  type: dict
  returned: always
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
        name=dict(type="str", required=True),
        version=dict(type="str", required=True),
    )
    argument_spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        info = client.get(
            "mlflow/model-versions/get",
            params={
                "name": module.params["name"],
                "version": module.params["version"],
            },
        )
        module.exit_json(changed=False, model_version=info.get("model_version", info))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
