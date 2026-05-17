#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: metastore
short_description: Manage Unity Catalog metastore
description:
  - Create, update, or delete a Unity Catalog metastore.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  metastore_id:
    description: Existing metastore ID. Required for update and delete.
    type: str
  name:
    description: Metastore name.
    type: str
  storage_root:
    description: Cloud storage root for managed tables.
    type: str
  region:
    description: Cloud region for the metastore.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a metastore
  stevefulme1.databricks.metastore:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: primary
    storage_root: s3://my-bucket/unity-catalog
    region: us-east-1
"""

RETURN = r"""
metastore:
  description: Metastore object.
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
        metastore_id=dict(type="str"),
        name=dict(type="str"),
        storage_root=dict(type="str"),
        region=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "absent", ["metastore_id"])],
    )
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    metastore_id = module.params.get("metastore_id")

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"unity-catalog/metastores/{metastore_id}", api_version="2.1")
            module.exit_json(changed=True)

        payload = {}
        for key in ("name", "storage_root", "region"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if metastore_id:
            if module.check_mode:
                module.exit_json(changed=True)
            updated = client.patch(
                f"unity-catalog/metastores/{metastore_id}",
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, metastore=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("unity-catalog/metastores", data=payload, api_version="2.1")
        module.exit_json(changed=True, metastore=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
