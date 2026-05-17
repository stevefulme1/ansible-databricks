#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: app_deployment
short_description: Deploy or update a Databricks App
description:
  - Create a new deployment for a Databricks App.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  name:
    description: App name.
    type: str
    required: true
  source_code_path:
    description: Workspace path to the app source code.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Deploy an app
  stevefulme1.databricks.app_deployment:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: my-dashboard-app
    source_code_path: /Workspace/apps/dashboard
"""

RETURN = r"""
deployment:
  description: Deployment object.
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
        source_code_path=dict(type="str", required=True),
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
            "apps/{}/deployments".format(module.params["name"]),
            data={"source_code_path": module.params["source_code_path"]},
        )
        module.exit_json(changed=True, deployment=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
