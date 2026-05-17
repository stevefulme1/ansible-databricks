# Ansible Collection - stevefulme1.databricks

Manage Databricks workspaces, clusters, Unity Catalog, MLflow, jobs, SQL warehouses, Delta Sharing, and secrets with Ansible.

This collection provides **100 modules** and an **Event-Driven Ansible (EDA) event source** for full lifecycle automation of Databricks resources across Azure, AWS, and GCP workspaces.

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.10 |
| Ansible Core | >= 2.16 |

No additional Python libraries are required beyond what Ansible provides -- all API calls use `ansible.module_utils.urls`.

## Installation

```bash
ansible-galaxy collection install stevefulme1.databricks
```

Install from source:

```bash
ansible-galaxy collection install git+https://github.com/stevefulme1/ansible-databricks.git
```

## Authentication

Every module requires `host` (workspace URL) and `token` (personal access token or service principal token).

You can pass them as module parameters or set them in a `group_vars` file:

```yaml
# group_vars/all.yml
databricks_host: "https://adb-123456789.12.azuredatabricks.net"
databricks_token: "{{ vault_databricks_token }}"
```

| Parameter | Description | Required |
|---|---|---|
| `host` | Databricks workspace URL | Yes |
| `token` | Personal access token or service principal token | Yes |
| `validate_certs` | Validate SSL certificates (default: `true`) | No |

## Quick Start

### Create a cluster

```yaml
- name: Create an interactive cluster
  stevefulme1.databricks.cluster:
    host: "{{ databricks_host }}"
    token: "{{ databricks_token }}"
    state: present
    cluster_name: analytics-cluster
    spark_version: "14.3.x-scala2.12"
    node_type_id: Standard_DS3_v2
    num_workers: 4
```

### Create a Unity Catalog schema and grant access

```yaml
- name: Create schema in Unity Catalog
  stevefulme1.databricks.schema:
    host: "{{ databricks_host }}"
    token: "{{ databricks_token }}"
    state: present
    catalog_name: production
    name: analytics
    comment: "Analytics team schema"

- name: Grant usage on schema
  stevefulme1.databricks.grant:
    host: "{{ databricks_host }}"
    token: "{{ databricks_token }}"
    securable_type: schema
    full_name: production.analytics
    principal: data-engineers
    privileges:
      - USE_SCHEMA
      - SELECT
```

### Submit a job run

```yaml
- name: Run a Databricks notebook job
  stevefulme1.databricks.job_run:
    host: "{{ databricks_host }}"
    token: "{{ databricks_token }}"
    job_id: 12345
    notebook_params:
      date: "2025-01-15"
      environment: production
  register: run_result

- name: Display run URL
  ansible.builtin.debug:
    msg: "Run URL: {{ run_result.run_page_url }}"
```

## Module Index

### Compute

| Module | Description |
|---|---|
| `cluster` | Manage Databricks clusters |
| `cluster_info` | Get Databricks cluster details |
| `cluster_list_info` | List all Databricks clusters |
| `cluster_event_info` | Get Databricks cluster events |
| `cluster_policy` | Manage Databricks cluster policies |
| `cluster_policy_info` | List Databricks cluster policies |
| `instance_pool` | Manage Databricks instance pools |
| `instance_pool_info` | List Databricks instance pools |
| `node_type_info` | List available Databricks node types |
| `spark_version_info` | List Databricks Spark runtime versions |

### Jobs & Pipelines

| Module | Description |
|---|---|
| `job` | Manage Databricks jobs |
| `job_info` | Get Databricks job details |
| `job_list_info` | List Databricks jobs |
| `job_run` | Trigger a Databricks job run |
| `job_run_info` | Get Databricks job run details |
| `job_run_list_info` | List Databricks job runs |
| `job_run_output_info` | Get Databricks job run output |
| `job_run_cancel` | Cancel a Databricks job run |
| `pipeline` | Manage Delta Live Tables pipelines |
| `pipeline_info` | Get Delta Live Tables pipeline details |
| `pipeline_update` | Trigger a Delta Live Tables pipeline update |

### Unity Catalog

| Module | Description |
|---|---|
| `catalog` | Manage Unity Catalog catalogs |
| `catalog_info` | List Unity Catalog catalogs |
| `schema` | Manage Unity Catalog schemas |
| `schema_info` | List Unity Catalog schemas |
| `table_info` | List or describe Unity Catalog tables |
| `volume` | Manage Unity Catalog volumes |
| `volume_info` | List Unity Catalog volumes |
| `external_location` | Manage Unity Catalog external locations |
| `external_location_info` | List Unity Catalog external locations |
| `storage_credential` | Manage Unity Catalog storage credentials |
| `storage_credential_info` | List Unity Catalog storage credentials |
| `function_info` | List Unity Catalog registered functions |
| `metastore` | Manage Unity Catalog metastore |
| `metastore_assignment` | Assign a metastore to a workspace |
| `grant` | Manage Unity Catalog grants |
| `system_schema` | Enable Databricks system schemas |

### MLflow

| Module | Description |
|---|---|
| `mlflow_experiment` | Manage MLflow experiments |
| `mlflow_experiment_info` | Get MLflow experiment details |
| `mlflow_registered_model` | Manage MLflow registered models |
| `mlflow_registered_model_info` | Get MLflow registered model details |
| `mlflow_model_version` | Manage MLflow model versions |
| `mlflow_model_version_info` | Get MLflow model version details |
| `mlflow_model_version_transition` | Transition MLflow model version stage |
| `mlflow_run_info` | Get MLflow run details |
| `mlflow_webhook` | Manage MLflow registry webhooks |

### Model Serving

| Module | Description |
|---|---|
| `serving_endpoint` | Manage Databricks serving endpoints |
| `serving_endpoint_info` | Get Databricks serving endpoint details |
| `serving_endpoint_config` | Update serving endpoint configuration |
| `serving_endpoint_permission` | Manage serving endpoint permissions |
| `serving_endpoint_query` | Query a Databricks serving endpoint |

### SQL Warehouses

| Module | Description |
|---|---|
| `sql_warehouse` | Manage Databricks SQL warehouses |
| `sql_warehouse_info` | Get Databricks SQL warehouse details |
| `sql_warehouse_list_info` | List Databricks SQL warehouses |
| `sql_warehouse_config` | Manage global SQL warehouse configuration |
| `sql_warehouse_start` | Start a Databricks SQL warehouse |
| `sql_warehouse_stop` | Stop a Databricks SQL warehouse |

### Delta Sharing

| Module | Description |
|---|---|
| `delta_share` | Manage Databricks Delta Sharing shares |
| `delta_share_info` | Get Delta Sharing share details |
| `delta_recipient` | Manage Delta Sharing recipients |
| `delta_recipient_info` | Get Delta Sharing recipient details |
| `delta_provider_info` | List Delta Sharing providers |

### DBFS (File System)

| Module | Description |
|---|---|
| `dbfs_file` | Manage DBFS files |
| `dbfs_file_info` | Get DBFS file status |
| `dbfs_directory` | Manage DBFS directories |
| `dbfs_directory_info` | List DBFS directory contents |

### Identity & Access Management

| Module | Description |
|---|---|
| `user` | Manage Databricks workspace users |
| `user_info` | List Databricks workspace users |
| `group` | Manage Databricks workspace groups |
| `group_info` | List Databricks workspace groups |
| `service_principal` | Manage Databricks service principals |
| `service_principal_info` | List Databricks service principals |
| `permission` | Set Databricks object permissions |
| `token` | Manage Databricks personal access tokens |
| `ip_access_list` | Manage Databricks IP access lists |
| `ip_access_list_info` | List Databricks IP access lists |

### Secrets

| Module | Description |
|---|---|
| `secret` | Manage Databricks secrets |
| `secret_info` | List Databricks secrets |
| `secret_scope` | Manage Databricks secret scopes |
| `secret_scope_info` | List Databricks secret scopes |
| `secret_acl` | Manage Databricks secret ACLs |
| `secret_acl_info` | List Databricks secret ACLs |

### Git Repos

| Module | Description |
|---|---|
| `repo` | Manage Databricks Git repos |
| `repo_info` | Get Databricks Git repo details |
| `repo_credential` | Manage Git credentials for Databricks repos |

### Governance & Monitoring

| Module | Description |
|---|---|
| `data_monitor` | Manage Databricks Lakehouse monitors |
| `data_monitor_info` | Get Lakehouse monitor details |
| `data_monitor_metric_info` | Get Lakehouse monitor metrics |
| `data_monitor_refresh` | Trigger a Lakehouse monitor refresh |
| `tag_rule` | Manage tag enforcement rules |
| `budget_policy` | Manage Databricks budget policies |
| `compliance_security_profile` | Manage compliance security profile |

### Apps & Networking

| Module | Description |
|---|---|
| `app` | Manage Databricks Apps |
| `app_info` | Get Databricks App details |
| `app_deployment` | Deploy or update a Databricks App |
| `workspace_conf` | Manage Databricks workspace configuration |
| `network_connectivity_config` | Manage network connectivity configuration |
| `network_connectivity_config_info` | Get network connectivity configuration |
| `private_access_settings` | Manage private access settings |
| `private_access_settings_info` | Get private access settings |

## Event-Driven Ansible (EDA)

The collection includes an EDA event source plugin that polls Databricks audit logs and cluster events.

### Event Source: `databricks_events`

Emits events for cluster lifecycle changes, job failures, and security alerts.

```yaml
# eda-rulebook.yml
- name: React to Databricks events
  hosts: all
  sources:
    - stevefulme1.databricks.databricks_events:
        host: "{{ databricks_host }}"
        token: "{{ databricks_token }}"
        poll_interval: 60
        event_types:
          - cluster_state_change
          - job_failure
          - security_alert
  rules:
    - name: Alert on cluster failure
      condition: event.type == "cluster_state_change" and event.state == "ERROR"
      action:
        run_playbook:
          name: remediate_cluster.yml
```

## Contributing

Contributions are welcome. Please open an issue or pull request on
[GitHub](https://github.com/stevefulme1/ansible-databricks).

## License

GNU General Public License v3.0 -- see [LICENSE](LICENSE) for details.
