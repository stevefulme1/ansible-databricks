#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: job
short_description: Manage Databricks jobs
description:
  - Create, update (reset), or delete Databricks jobs.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  job_id:
    description: Existing job ID. Required for update and delete.
    type: int
  name:
    description: Job name.
    type: str
  tasks:
    description: List of task definitions.
    type: list
    elements: dict
  schedule:
    description: Cron schedule dict with C(quartz_cron_expression) and C(timezone_id).
    type: dict
  max_concurrent_runs:
    description: Maximum concurrent runs.
    type: int
  tags:
    description: Job tags as key-value pairs.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a job
  stevefulme1.databricks.job:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: etl-pipeline
    tasks:
      - task_key: ingest
        notebook_task:
          notebook_path: /Repos/etl/ingest
"""

RETURN = r"""
job:
  description: Job object.
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
        job_id=dict(type="int"),
        name=dict(type="str"),
        tasks=dict(type="list", elements="dict"),
        schedule=dict(type="dict"),
        max_concurrent_runs=dict(type="int"),
        tags=dict(type="dict"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["job_id"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    job_id = module.params.get("job_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("jobs/delete", data={"job_id": job_id}, api_version="2.1")
            module.exit_json(changed=True)

        settings = {}
        for key in ("name", "tasks", "schedule", "max_concurrent_runs", "tags"):
            val = module.params.get(key)
            if val is not None:
                settings[key] = val

        if job_id:
            if module.check_mode:
                module.exit_json(changed=True)
            client.post(
                "jobs/reset",
                data={"job_id": job_id, "new_settings": settings},
                api_version="2.1",
            )
            info = client.get("jobs/get", params={"job_id": job_id}, api_version="2.1")
            module.exit_json(changed=True, job=info)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post("jobs/create", data=settings, api_version="2.1")
        info = client.get("jobs/get", params={"job_id": resp["job_id"]}, api_version="2.1")
        module.exit_json(changed=True, job=info)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
