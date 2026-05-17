#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: dbfs_file
short_description: Manage DBFS files
description:
  - Create or delete files in the Databricks File System.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  path:
    description: DBFS path for the file.
    type: str
    required: true
  src:
    description: Local file path to upload. Required for present.
    type: path
  overwrite:
    description: Overwrite existing file.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Upload a file to DBFS
  stevefulme1.databricks.dbfs_file:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /mnt/data/config.json
    src: /tmp/config.json

- name: Delete a DBFS file
  stevefulme1.databricks.dbfs_file:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /mnt/data/config.json
    state: absent
"""

RETURN = r"""
file:
  description: File metadata.
  type: dict
  returned: when state is present
"""

import base64

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
        src=dict(type="path"),
        overwrite=dict(type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["src"])],
    )

    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    dbfs_path = module.params["path"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.post("dbfs/delete", data={"path": dbfs_path})
            module.exit_json(changed=True)

        if module.check_mode:
            module.exit_json(changed=True)

        with open(module.params["src"], "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        client.post(
            "dbfs/put",
            data={
                "path": dbfs_path,
                "contents": content,
                "overwrite": module.params["overwrite"],
            },
        )
        info = client.get("dbfs/get-status", params={"path": dbfs_path})
        module.exit_json(changed=True, file=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
