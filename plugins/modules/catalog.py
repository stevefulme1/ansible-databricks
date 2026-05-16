#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: catalog
short_description: Manage Unity Catalog catalogs
description:
  - Create, update, or delete Unity Catalog catalogs.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Catalog name.
    type: str
    required: true
  comment:
    description: Free-form comment.
    type: str
  properties:
    description: Key-value properties.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a catalog
  stevefulme1.databricks.catalog:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: analytics
    comment: Analytics catalog
"""

RETURN = r"""
catalog:
  description: Catalog object.
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
        comment=dict(type="str"),
        properties=dict(type="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    name = module.params["name"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("unity-catalog/catalogs/{0}".format(name), api_version="2.1")
            module.exit_json(changed=True)

        # Check existence
        existing = None
        try:
            existing = client.get(
                "unity-catalog/catalogs/{0}".format(name), api_version="2.1"
            )
        except DatabricksError as e:
            if e.status_code != 404:
                raise

        payload = {"name": name}
        if module.params.get("comment") is not None:
            payload["comment"] = module.params["comment"]
        if module.params.get("properties"):
            payload["properties"] = module.params["properties"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, catalog=existing)
            updated = client.patch(
                "unity-catalog/catalogs/{0}".format(name),
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, catalog=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("unity-catalog/catalogs", data=payload, api_version="2.1")
        module.exit_json(changed=True, catalog=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
