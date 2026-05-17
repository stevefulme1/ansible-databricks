#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: pipeline
short_description: Manage Delta Live Tables pipelines
description:
  - Create, update, or delete Delta Live Tables pipelines.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  pipeline_id:
    description: Existing pipeline ID.
    type: str
  name:
    description: Pipeline name.
    type: str
  storage:
    description: Storage location for pipeline output.
    type: str
  target:
    description: Target schema for pipeline tables.
    type: str
  continuous:
    description: Whether the pipeline runs continuously.
    type: bool
  development:
    description: Whether to run in development mode.
    type: bool
  configuration:
    description: Pipeline configuration parameters.
    type: dict
  libraries:
    description: List of library notebooks or files.
    type: list
    elements: dict
  clusters:
    description: Cluster configuration for the pipeline.
    type: list
    elements: dict
  channel:
    description: Release channel.
    type: str
    choices: [CURRENT, PREVIEW]
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a DLT pipeline
  stevefulme1.databricks.pipeline:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: etl-pipeline
    target: bronze_schema
    libraries:
      - notebook:
          path: /Repos/user/etl/bronze
"""

RETURN = r"""
pipeline:
  description: Pipeline object.
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
        pipeline_id=dict(type="str"),
        name=dict(type="str"),
        storage=dict(type="str"),
        target=dict(type="str"),
        continuous=dict(type="bool"),
        development=dict(type="bool"),
        configuration=dict(type="dict"),
        libraries=dict(type="list", elements="dict"),
        clusters=dict(type="list", elements="dict"),
        channel=dict(type="str", choices=["CURRENT", "PREVIEW"]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["pipeline_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    pipeline_id = module.params.get("pipeline_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"pipelines/{pipeline_id}")
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "name",
            "storage",
            "target",
            "continuous",
            "development",
            "configuration",
            "libraries",
            "clusters",
            "channel",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if pipeline_id:
            if module.check_mode:
                module.exit_json(changed=True)
            client.put(f"pipelines/{pipeline_id}", data=payload)
            info = client.get(f"pipelines/{pipeline_id}")
            module.exit_json(changed=True, pipeline=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("pipelines", data=payload)
        pid = resp.get("pipeline_id", "")
        info = client.get(f"pipelines/{pid}")
        module.exit_json(changed=True, pipeline=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
