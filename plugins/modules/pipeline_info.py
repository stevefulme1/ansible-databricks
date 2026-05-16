#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: pipeline_info
short_description: Get Delta Live Tables pipeline details
description:
  - Retrieve details of a DLT pipeline.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  pipeline_id:
    description: Pipeline ID to query.
    type: str
    required: true
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Get pipeline details
  stevefulme1.databricks.pipeline_info:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    pipeline_id: abc123-def456
"""

RETURN = r"""
pipeline:
  description: Pipeline details.
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
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        info = client.get("pipelines/{0}".format(module.params["pipeline_id"]))
        module.exit_json(changed=False, pipeline=info)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
