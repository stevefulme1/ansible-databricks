#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: notebook_info
short_description: Get notebook info
description:
  - Retrieve notebook status or list workspace contents.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  path:
    description:
      - Workspace path to query.
      - Returns status for a notebook or lists contents for a directory.
    type: str
    required: true
  format:
    description: Export format when retrieving notebook content.
    type: str
    choices: [SOURCE, HTML, JUPYTER, DBC]
  export_content:
    description: Whether to export the notebook content.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get notebook status
  stevefulme1.databricks.notebook_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /Users/user@example.com/my_notebook

- name: List directory contents
  stevefulme1.databricks.notebook_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /Users/user@example.com
"""

RETURN = r"""
notebook:
  description: Notebook status object.
  type: dict
  returned: when path is a notebook
notebooks:
  description: List of workspace objects when path is a directory.
  type: list
  elements: dict
  returned: when path is a directory
content:
  description: Exported notebook content (base64-encoded).
  type: str
  returned: when export_content is true
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
        path=dict(type="str", required=True),
        format=dict(type="str", choices=["SOURCE", "HTML", "JUPYTER", "DBC"]),
        export_content=dict(type="bool", default=False),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    path = module.params["path"]

    try:
        status = client.get(
            "workspace/get-status",
            params={"path": path},
            api_version="2.0",
        )

        result = dict(changed=False)

        if status.get("object_type") == "DIRECTORY":
            resp = client.get(
                "workspace/list",
                params={"path": path},
                api_version="2.0",
            )
            result["notebooks"] = resp.get("objects", [])
        else:
            result["notebook"] = status
            if module.params.get("export_content"):
                params = {"path": path}
                if module.params.get("format"):
                    params["format"] = module.params["format"]
                export = client.get(
                    "workspace/export",
                    params=params,
                    api_version="2.0",
                )
                result["content"] = export.get("content", "")

        module.exit_json(**result)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
