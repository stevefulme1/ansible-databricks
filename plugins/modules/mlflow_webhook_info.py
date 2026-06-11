#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: mlflow_webhook_info
short_description: List MLflow registry webhooks
description:
  - Retrieve all MLflow model registry webhooks.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  model_name:
    description:
      - Filter webhooks by model name.
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
- name: List all webhooks
  stevefulme1.databricks.mlflow_webhook_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef

- name: List webhooks for a specific model
  stevefulme1.databricks.mlflow_webhook_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    model_name: my-model
"""

RETURN = r"""
webhooks:
  description: List of webhook objects.
  type: list
  elements: dict
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
        model_name=dict(type="str"),
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
        params = {}
        if module.params.get("model_name"):
            params["model_name"] = module.params["model_name"]
        resp = client.get("mlflow/registry-webhooks/list", params=params)
        module.exit_json(changed=False, webhooks=resp.get("webhooks", []))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
