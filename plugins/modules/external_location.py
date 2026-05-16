#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: external_location
short_description: Manage Unity Catalog external locations
description:
  - Create, update, or delete external locations.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: External location name.
    type: str
    required: true
  url:
    description: Cloud storage URL for the external location.
    type: str
  credential_name:
    description: Storage credential name to use.
    type: str
  comment:
    description: Free-form comment.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an external location
  stevefulme1.databricks.external_location:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: raw-data
    url: s3://my-bucket/raw
    credential_name: s3-cred
"""

RETURN = r"""
external_location:
  description: External location object.
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
        url=dict(type="str"),
        credential_name=dict(type="str"),
        comment=dict(type="str"),
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
            client.delete(
                "unity-catalog/external-locations/{0}".format(name), api_version="2.1"
            )
            module.exit_json(changed=True)

        existing = None
        try:
            existing = client.get(
                "unity-catalog/external-locations/{0}".format(name), api_version="2.1"
            )
        except DatabricksError as e:
            if e.status_code != 404:
                raise

        payload = {"name": name}
        if module.params.get("url"):
            payload["url"] = module.params["url"]
        if module.params.get("credential_name"):
            payload["credential_name"] = module.params["credential_name"]
        if module.params.get("comment") is not None:
            payload["comment"] = module.params["comment"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, external_location=existing)
            updated = client.patch(
                "unity-catalog/external-locations/{0}".format(name),
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, external_location=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post(
            "unity-catalog/external-locations", data=payload, api_version="2.1"
        )
        module.exit_json(changed=True, external_location=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
