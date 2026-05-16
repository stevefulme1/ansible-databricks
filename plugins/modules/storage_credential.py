#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: storage_credential
short_description: Manage Unity Catalog storage credentials
description:
  - Create, update, or delete storage credentials.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  name:
    description: Credential name.
    type: str
    required: true
  aws_iam_role:
    description: AWS IAM role configuration dict with C(role_arn).
    type: dict
  azure_managed_identity:
    description: Azure managed identity configuration dict with C(access_connector_id).
    type: dict
  comment:
    description: Free-form comment.
    type: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create an AWS storage credential
  stevefulme1.databricks.storage_credential:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    name: s3-cred
    aws_iam_role:
      role_arn: arn:aws:iam::123456789012:role/unity-catalog
"""

RETURN = r"""
credential:
  description: Storage credential object.
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
        aws_iam_role=dict(type="dict"),
        azure_managed_identity=dict(type="dict"),
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
                "unity-catalog/storage-credentials/{0}".format(name), api_version="2.1"
            )
            module.exit_json(changed=True)

        existing = None
        try:
            existing = client.get(
                "unity-catalog/storage-credentials/{0}".format(name), api_version="2.1"
            )
        except DatabricksError as e:
            if e.status_code != 404:
                raise

        payload = {"name": name}
        if module.params.get("aws_iam_role"):
            payload["aws_iam_role"] = module.params["aws_iam_role"]
        if module.params.get("azure_managed_identity"):
            payload["azure_managed_identity"] = module.params["azure_managed_identity"]
        if module.params.get("comment") is not None:
            payload["comment"] = module.params["comment"]

        if existing:
            if module.check_mode:
                module.exit_json(changed=True, credential=existing)
            updated = client.patch(
                "unity-catalog/storage-credentials/{0}".format(name),
                data=payload,
                api_version="2.1",
            )
            module.exit_json(changed=True, credential=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post(
            "unity-catalog/storage-credentials", data=payload, api_version="2.1"
        )
        module.exit_json(changed=True, credential=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
