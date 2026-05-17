#!/usr/bin/python
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = r"""
---
module: data_monitor
short_description: Manage Databricks Lakehouse monitors
description:
  - Create, update, or delete a Lakehouse monitor on a table.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
  table_name:
    description: Full table name (catalog.schema.table).
    type: str
    required: true
  monitor_type:
    description: Type of monitor.
    type: str
    choices: [SNAPSHOT, TIME_SERIES, INFERENCE]
  output_schema_name:
    description: Schema for monitor output tables.
    type: str
  assets_dir:
    description: Directory for monitor assets.
    type: str
  slicing_exprs:
    description: Slicing expressions for analysis.
    type: list
    elements: str
  time_series:
    description: Time series configuration.
    type: dict
  inference_log:
    description: Inference log configuration.
    type: dict
extends_documentation_fragment:
  - stevefulme1.databricks.databricks
"""

EXAMPLES = r"""
- name: Create a snapshot monitor
  stevefulme1.databricks.data_monitor:
    host: https://adb-123.4.azuredatabricks.net
    token: dapi0123456789abcdef
    table_name: catalog.schema.my_table
    monitor_type: SNAPSHOT
    output_schema_name: catalog.schema
"""

RETURN = r"""
monitor:
  description: Monitor object.
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
        table_name=dict(type="str", required=True),
        monitor_type=dict(type="str", choices=["SNAPSHOT", "TIME_SERIES", "INFERENCE"]),
        output_schema_name=dict(type="str"),
        assets_dir=dict(type="str"),
        slicing_exprs=dict(type="list", elements="str"),
        time_series=dict(type="dict"),
        inference_log=dict(type="dict"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    client = DatabricksClient(
        host=module.params["host"],
        token=module.params["token"],
        validate_certs=module.params["validate_certs"],
    )

    state = module.params["state"]
    table_name = module.params["table_name"]

    try:
        if state == "absent":
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete(f"unity-catalog/tables/{table_name}/monitor")
            module.exit_json(changed=True)

        payload = {}
        for key in (
            "monitor_type",
            "output_schema_name",
            "assets_dir",
            "slicing_exprs",
            "time_series",
            "inference_log",
        ):
            val = module.params.get(key)
            if val is not None:
                payload[key] = val

        try:
            existing = client.get(f"unity-catalog/tables/{table_name}/monitor")
            if module.check_mode:
                module.exit_json(changed=True, monitor=existing)
            client.put(
                f"unity-catalog/tables/{table_name}/monitor",
                data=payload,
            )
            info = client.get(f"unity-catalog/tables/{table_name}/monitor")
            module.exit_json(changed=True, monitor=info)
        except DatabricksError:
            if module.check_mode:
                module.exit_json(changed=True)
            resp = client.post(
                f"unity-catalog/tables/{table_name}/monitor",
                data=payload,
            )
            module.exit_json(changed=True, monitor=resp)
    except DatabricksError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
