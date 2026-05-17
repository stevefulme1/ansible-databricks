#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: notebook
short_description: Manage workspace notebooks
description:
  - Import, export, or delete notebooks in a Databricks workspace.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  path:
    description: Workspace path for the notebook.
    type: str
    required: true
  content:
    description:
      - Base64-encoded notebook content for import.
      - Required when state is present.
    type: str
  language:
    description: Notebook language.
    type: str
    choices: [PYTHON, SCALA, SQL, R]
  format:
    description: Notebook format for import/export.
    type: str
    choices: [SOURCE, HTML, JUPYTER, DBC]
    default: SOURCE
  overwrite:
    description: Whether to overwrite an existing notebook.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Import a notebook
  stevefulme1.databricks.notebook:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /Users/user@example.com/my_notebook
    content: "{{ lookup('file', 'notebook.py') | b64encode }}"
    language: PYTHON
    format: SOURCE
    overwrite: true

- name: Delete a notebook
  stevefulme1.databricks.notebook:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /Users/user@example.com/my_notebook
    state: absent
"""

RETURN = r"""
notebook:
  description: Notebook object details.
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
        path=dict(type="str", required=True),
        content=dict(type="str"),
        language=dict(type="str", choices=["PYTHON", "SCALA", "SQL", "R"]),
        format=dict(type="str", default="SOURCE", choices=["SOURCE", "HTML", "JUPYTER", "DBC"]),
        overwrite=dict(type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[("state", "present", ["content"])],
        supports_check_mode=True,
    )
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    path = module.params["path"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post(
                "workspace/delete",
                data={"path": path, "recursive": False},
                api_version="2.0",
            )
            module.exit_json(changed=True)

        payload = {
            "path": path,
            "content": module.params["content"],
            "format": module.params["format"],
            "overwrite": module.params["overwrite"],
        }
        if module.params.get("language"):
            payload["language"] = module.params["language"]

        if module.check_mode:
            module.exit_json(changed=True)
        client.post("workspace/import", data=payload, api_version="2.0")

        # Fetch the notebook status to return
        info = client.get(
            "workspace/get-status",
            params={"path": path},
            api_version="2.0",
        )
        module.exit_json(changed=True, notebook=info)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
