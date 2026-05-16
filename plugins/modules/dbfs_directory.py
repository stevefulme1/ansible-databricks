#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: dbfs_directory
short_description: Manage DBFS directories
description:
  - Create or delete directories in the Databricks File System.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  path:
    description: DBFS directory path.
    type: str
    required: true
  recursive:
    description: Recursively delete directory contents.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a DBFS directory
  stevefulme1.databricks.dbfs_directory:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /mnt/data/output

- name: Delete a DBFS directory
  stevefulme1.databricks.dbfs_directory:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    path: /mnt/data/output
    state: absent
    recursive: true
"""

RETURN = r"""
directory:
  description: Directory metadata.
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
        recursive=dict(type="bool", default=False),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
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
                "dbfs/delete",
                data={"path": path, "recursive": module.params["recursive"]},
            )
            module.exit_json(changed=True)

        if module.check_mode:
            module.exit_json(changed=True)
        client.post("dbfs/mkdirs", data={"path": path})
        info = client.get("dbfs/get-status", params={"path": path})
        module.exit_json(changed=True, directory=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
