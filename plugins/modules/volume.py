#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: volume
short_description: Manage Unity Catalog volumes
description:
  - Create, update, or delete Unity Catalog volumes.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Volume name.
    type: str
    required: true
  catalog_name:
    description: Parent catalog name.
    type: str
    required: true
  schema_name:
    description: Parent schema name.
    type: str
    required: true
  volume_type:
    description: Volume type.
    type: str
    choices: [MANAGED, EXTERNAL]
    default: MANAGED
  storage_location:
    description: External storage location URI. Required for EXTERNAL volumes.
    type: str
  comment:
    description: Free-form comment.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a managed volume
  stevefulme1.databricks.volume:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    catalog_name: analytics
    schema_name: bronze
    name: raw_files
"""

RETURN = r"""
volume:
  description: Volume object.
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
        name=dict(type="str", required=True),
        catalog_name=dict(type="str", required=True),
        schema_name=dict(type="str", required=True),
        volume_type=dict(type="str", default="MANAGED", choices=["MANAGED", "EXTERNAL"]),
        storage_location=dict(type="str"),
        comment=dict(type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    full_name = "{}.{}.{}".format(
        module.params["catalog_name"],
        module.params["schema_name"],
        module.params["name"],
    )

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"unity-catalog/volumes/{full_name}", api_version="2.1")
            module.exit_json(changed=True)

        existing = None
        try:
            existing = client.get(f"unity-catalog/volumes/{full_name}", api_version="2.1")
        except DatabricksError as e:
            if e.status_code != 404:
                raise

        payload = {
            "name": module.params["name"],
            "catalog_name": module.params["catalog_name"],
            "schema_name": module.params["schema_name"],
            "volume_type": module.params["volume_type"],
        }
        if module.params.get("storage_location"):
            payload["storage_location"] = module.params["storage_location"]
        if module.params.get("comment") is not None:
            payload["comment"] = module.params["comment"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, volume=existing)
            updated = client.patch(
                f"unity-catalog/volumes/{full_name}",
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, volume=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("unity-catalog/volumes", data=payload, api_version="2.1")
        module.exit_json(changed=True, volume=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
