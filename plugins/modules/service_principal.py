#!/usr/bin/python
# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: service_principal
short_description: Manage Databricks service principals
description:
  - Create, update, or delete service principals via the SCIM API.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  service_principal_id:
    description: Existing SCIM ID.
    type: str
  application_id:
    description: Application / client ID for the service principal.
    type: str
  display_name:
    description: Display name.
    type: str
  active:
    description: Whether the service principal is active.
    type: bool
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a service principal
  stevefulme1.databricks.service_principal:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    application_id: 00000000-0000-0000-0000-000000000001
    display_name: cicd-bot
"""

RETURN = r"""
service_principal:
  description: Service principal object.
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
        service_principal_id=dict(type="str"),
        application_id=dict(type="str"),
        display_name=dict(type="str"),
        active=dict(type="bool"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    sp_id = module.params.get("service_principal_id")

    try:
        if state == "absent":
            if not sp_id:
                module.fail_json(msg="service_principal_id required for absent")
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"preview/scim/v2/ServicePrincipals/{sp_id}")
            module.exit_json(changed=True)

        payload = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServicePrincipal"],
        }
        if module.params.get("application_id"):
            payload["applicationId"] = module.params["application_id"]
        if module.params.get("display_name"):
            payload["displayName"] = module.params["display_name"]
        if module.params.get("active") is not None:
            payload["active"] = module.params["active"]

        if sp_id:
            if module.check_mode:
                module.exit_json(changed=True)
            updated = client.put(f"preview/scim/v2/ServicePrincipals/{sp_id}", data=payload)
            module.exit_json(changed=True, service_principal=updated)

        if module.check_mode:
            module.exit_json(changed=True)
        created = client.post("preview/scim/v2/ServicePrincipals", data=payload)
        module.exit_json(changed=True, service_principal=created)

    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
