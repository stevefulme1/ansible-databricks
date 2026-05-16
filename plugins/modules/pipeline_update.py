#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pipeline_update
short_description: Trigger a Delta Live Tables pipeline update
description:
  - Start a new update for a DLT pipeline.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  pipeline_id:
    description: Pipeline ID.
    type: str
    required: true
  full_refresh:
    description: Perform a full refresh.
    type: bool
    default: false
  refresh_selection:
    description: Tables to selectively refresh.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Trigger pipeline update
  stevefulme1.databricks.pipeline_update:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    pipeline_id: abc123-def456
    full_refresh: true
"""

RETURN = r"""
update:
  description: Update response.
  type: dict
  returned: always
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
        pipeline_id=dict(type="str", required=True),
        full_refresh=dict(type="bool", default=False),
        refresh_selection=dict(type="list", elements="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        if module.check_mode:
            module.exit_json(changed=True)
        payload = {"full_refresh": module.params["full_refresh"]}
        if module.params.get("refresh_selection"):
            payload["refresh_selection"] = module.params["refresh_selection"]
        resp = client.post(
            "pipelines/{0}/updates".format(module.params["pipeline_id"]),
            data=payload,
        )
        module.exit_json(changed=True, update=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
