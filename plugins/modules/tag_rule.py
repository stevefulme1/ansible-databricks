#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tag_rule
short_description: Manage tag enforcement rules
description:
  - Create, update, or delete tag enforcement rules in Unity Catalog.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  metastore_id:
    description: Metastore ID.
    type: str
    required: true
  schema_name:
    description: Schema pattern for the rule.
    type: str
  tag_key:
    description: Required tag key.
    type: str
  tag_values:
    description: Allowed tag values.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create tag enforcement rule
  stevefulme1.databricks.tag_rule:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    metastore_id: abc-123-def
    tag_key: environment
    tag_values:
      - production
      - staging
      - development
"""

RETURN = r"""
rule:
  description: Tag rule object.
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
        metastore_id=dict(type="str", required=True),
        schema_name=dict(type="str"),
        tag_key=dict(type="str"),
        tag_values=dict(type="list", elements="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    metastore_id = module.params["metastore_id"]

    try:
        payload = {}
        for key in ("schema_name", "tag_key", "tag_values"):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(
                "unity-catalog/metastores/{0}/tag-rules".format(metastore_id),
                params=payload,
            )
            module.exit_json(changed=True)

        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.post(
            "unity-catalog/metastores/{0}/tag-rules".format(metastore_id),
            data=payload,
        )
        module.exit_json(changed=True, rule=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
