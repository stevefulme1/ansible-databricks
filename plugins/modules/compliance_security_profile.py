#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r"""
---
module: compliance_security_profile
short_description: Manage compliance security profile
description:
  - Enable or configure the compliance security profile for a workspace.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  is_enabled:
    description: Whether the security profile is enabled.
    type: bool
    required: true
  compliance_standards:
    description: List of compliance standards.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Enable compliance security profile
  stevefulme1.databricks.compliance_security_profile:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    is_enabled: true
    compliance_standards:
      - HIPAA
      - PCI_DSS
"""

RETURN = r"""
profile:
  description: Security profile configuration.
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
        is_enabled=dict(type="bool", required=True),
        compliance_standards=dict(type="list", elements="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    try:
        payload = {"is_enabled": module.params["is_enabled"]}
        if module.params.get("compliance_standards"):
            payload["compliance_standards"] = module.params["compliance_standards"]
        if module.check_mode:
            module.exit_json(changed=True)
        resp = client.patch(
            "settings/types/shield_csp_enablement_ws_db/names/default",
            data={"setting": {"compliance_security_profile_workspace": payload}},
        )
        module.exit_json(changed=True, profile=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
