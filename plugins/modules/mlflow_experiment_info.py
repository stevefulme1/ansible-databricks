#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: mlflow_experiment_info
short_description: Get MLflow experiment details
description:
  - Retrieve information about an MLflow experiment.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  experiment_id:
    description: The experiment ID to query.
    type: str
  name:
    description: The experiment name to query.
    type: str

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
- name: Get experiment by ID
  stevefulme1.databricks.mlflow_experiment_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    experiment_id: "12345"
"""

RETURN = r"""
experiment:
  description: Experiment details.
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
        experiment_id=dict(type="str"),
        name=dict(type="str"),
    )
    argument_spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["experiment_id", "name"]],
    )
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.params.get("experiment_id"):
            info = client.get(
                "mlflow/experiments/get",
                params={"experiment_id": module.params["experiment_id"]},
            )
        else:
            info = client.get(
                "mlflow/experiments/get-by-name",
                params={"experiment_name": module.params["name"]},
            )
        module.exit_json(changed=False, experiment=info.get("experiment", info))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
