#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mlflow_webhook
short_description: Manage MLflow registry webhooks
description:
  - Create, update, or delete MLflow model registry webhooks.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  webhook_id:
    description: Existing webhook ID. Required for update or absent.
    type: str
  events:
    description: List of events to trigger the webhook.
    type: list
    elements: str
  model_name:
    description: Model name to scope the webhook to.
    type: str
  http_url_spec:
    description: HTTP endpoint configuration.
    type: dict
  job_spec:
    description: Databricks job specification for webhook action.
    type: dict
  description:
    description: Webhook description.
    type: str
  status:
    description: Webhook status.
    type: str
    choices: [ACTIVE, DISABLED, TEST_MODE]
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a webhook
  stevefulme1.databricks.mlflow_webhook:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    events:
      - MODEL_VERSION_CREATED
      - MODEL_VERSION_TRANSITIONED_STAGE
    model_name: my-model
    http_url_spec:
      url: https://hooks.example.com/mlflow
"""

RETURN = r"""
webhook:
  description: Webhook object.
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
        webhook_id=dict(type="str"),
        events=dict(type="list", elements="str"),
        model_name=dict(type="str"),
        http_url_spec=dict(type="dict"),
        job_spec=dict(type="dict"),
        description=dict(type="str"),
        status=dict(type="str", choices=["ACTIVE", "DISABLED", "TEST_MODE"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["webhook_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    webhook_id = module.params.get("webhook_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(
                "mlflow/registry-webhooks/delete",
                params={"id": webhook_id},
            )
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "events",
            "model_name",
            "http_url_spec",
            "job_spec",
            "description",
            "status",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if webhook_id:
            payload["id"] = webhook_id
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.patch("mlflow/registry-webhooks/update", data=payload)
            module.exit_json(changed=True, webhook=resp.get("webhook", resp))

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("mlflow/registry-webhooks/create", data=payload)
        module.exit_json(changed=True, webhook=resp.get("webhook", resp))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
