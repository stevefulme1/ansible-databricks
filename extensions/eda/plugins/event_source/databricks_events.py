# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Databricks event source plugin for Event-Driven Ansible.

Polls Databricks audit logs and cluster events, emitting structured events
for cluster lifecycle changes, job failures, and security alerts.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import asyncio
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import json


DOCUMENTATION = r"""
---
module: databricks_events
short_description: Databricks event source for EDA
description:
  - Polls Databricks audit logs or cluster events and emits events
    for cluster lifecycle changes, job failures, and security alerts.
version_added: "1.1.0"
author: Steve Fulmer (@stevefulme1)
options:
  host:
    description: Databricks workspace URL.
    type: str
    required: true
  token:
    description: Databricks personal access token.
    type: str
    required: true
  poll_interval:
    description: Seconds between polling cycles.
    type: int
    default: 30
  event_types:
    description: Event types to monitor.
    type: list
    elements: str
    default:
      - cluster_started
      - cluster_terminated
      - job_failed
      - security_alert
  cluster_ids:
    description: Optional list of cluster IDs to monitor.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Listen for Databricks events
  stevefulme1.databricks.databricks_events:
    host: https://adb-123.4.azuredatabricks.net
    token: "{{ databricks_token }}"
    poll_interval: 60
    event_types:
      - cluster_started
      - cluster_terminated
      - job_failed
"""


def _api_get(host, token, path, params=None):
    """Make a GET request to the Databricks REST API."""
    url = "{0}/api/2.0/{1}".format(host.rstrip("/"), path)
    if params:
        query = "&".join("{0}={1}".format(k, v) for k, v in params.items())
        url = "{0}?{1}".format(url, query)

    req = Request(url)
    req.add_header("Authorization", "Bearer {0}".format(token))
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        return {"error": str(exc)}


def _classify_event(event_data):
    """Classify a raw Databricks event into a normalized type."""
    action = event_data.get("action_name", "")
    service = event_data.get("service_name", "")

    if service == "clusters":
        if "start" in action.lower() or "create" in action.lower():
            return "cluster_started"
        if "delete" in action.lower() or "terminate" in action.lower():
            return "cluster_terminated"
    if service == "jobs" and "fail" in action.lower():
        return "job_failed"
    if service in ("accounts", "iamRole", "tokens"):
        return "security_alert"
    return "unknown"


def _poll_cluster_events(host, token, cluster_ids, since_ts):
    """Poll cluster events for specific clusters."""
    events = []
    for cid in cluster_ids:
        payload = {
            "cluster_id": cid,
            "start_time": int(since_ts * 1000),
            "order": "ASC",
            "limit": 50,
        }
        url = "{0}/api/2.0/clusters/events".format(host.rstrip("/"))
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, method="POST")
        req.add_header("Authorization", "Bearer {0}".format(token))
        req.add_header("Content-Type", "application/json")

        try:
            with urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                for ev in result.get("events", []):
                    ev_type = ev.get("type", "").upper()
                    if "RUNNING" in ev_type or "STARTING" in ev_type:
                        event_kind = "cluster_started"
                    elif "TERMINATING" in ev_type or "TERMINATED" in ev_type:
                        event_kind = "cluster_terminated"
                    else:
                        event_kind = "cluster_event"
                    events.append(
                        {
                            "event_type": event_kind,
                            "cluster_id": cid,
                            "details": ev,
                            "timestamp": ev.get("timestamp", 0),
                        }
                    )
        except (HTTPError, URLError):
            pass
    return events


def _poll_audit_logs(host, token, since_ts, event_types):
    """Poll workspace audit logs for relevant events."""
    events = []
    resp = _api_get(
        host,
        token,
        "unity-catalog/system/access/audit",
        params={
            "start_time": str(int(since_ts * 1000)),
            "limit": "100",
        },
    )

    if "error" in resp:
        return events

    for entry in resp.get("events", resp.get("log_items", [])):
        classified = _classify_event(entry)
        if classified in event_types:
            events.append(
                {
                    "event_type": classified,
                    "source": "audit_log",
                    "details": entry,
                    "timestamp": entry.get("timestamp", 0),
                }
            )
    return events


async def main(queue, args):
    """Entry point for the EDA event source plugin.

    Polls Databricks for cluster events and audit log entries,
    then places matching events onto the provided queue.
    """
    host = args.get("host", "")
    token = args.get("token", "")
    poll_interval = int(args.get("poll_interval", 30))
    event_types = args.get(
        "event_types",
        [
            "cluster_started",
            "cluster_terminated",
            "job_failed",
            "security_alert",
        ],
    )
    cluster_ids = args.get("cluster_ids", [])

    last_poll = time.time()

    while True:
        now = time.time()
        events = []

        if cluster_ids:
            events.extend(_poll_cluster_events(host, token, cluster_ids, last_poll))

        events.extend(_poll_audit_logs(host, token, last_poll, event_types))

        for event in events:
            if event.get("event_type") in event_types:
                await queue.put({"databricks": event})

        last_poll = now
        await asyncio.sleep(poll_interval)


if __name__ == "__main__":

    class _MockQueue:
        """Simple mock queue for local testing."""

        async def put(self, item):
            print(json.dumps(item, indent=2))

    asyncio.run(
        main(
            _MockQueue(),
            {
                "host": "https://example.databricks.com",
                "token": "test",
                "poll_interval": 5,
            },
        )
    )
