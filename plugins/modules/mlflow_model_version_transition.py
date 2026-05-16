#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mlflow_model_version_transition
short_description: Transition MLflow model version stage
description:
  - Transition a model version between stages.
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
  stage:
    description: Target stage.
    type: str
    required: true
    choices: [None, Staging, Production, Archived]
  archive_existing_versions:
    description: Archive existing versions in the target stage.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Promote model to Production
  stevefulme1.databricks.mlflow_model_version_transition:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-model
    version: "3"
    stage: Production
    archive_existing_versions: true
"""

RETURN = r"""
model_version:
  description: Model version after transition.
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
        stage=dict(
            type="str",
            required=True,
            choices=["None", "Staging", "Production", "Archived"],
        ),
        archive_existing_versions=dict(type="bool", default=False),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post(
            "mlflow/model-versions/transition-stage",
            data={
                "name": module.params["name"],
                "version": module.params["version"],
                "stage": module.params["stage"],
                "archive_existing_versions": module.params["archive_existing_versions"],
            },
        )
        module.exit_json(changed=True, model_version=resp.get("model_version", resp))
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
