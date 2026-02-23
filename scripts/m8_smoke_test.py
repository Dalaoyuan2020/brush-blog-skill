#!/usr/bin/env python3
"""
M8 smoke test for brush-blog-skill.

Usage:
  python3 scripts/m8_smoke_test.py
"""

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"
BEHAVIOR_EVENTS_FILE = DATA_DIR / "behavior_events.jsonl"
SAVED_NOTES_FILE = DATA_DIR / "saved_notes.jsonl"
TEST_USER_ID = "m8-smoke-user"


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def _run():
    import sys

    sys.path.insert(0, str(SRC_DIR))
    from main import handle_command  # pylint: disable=import-error

    profile_path = PROFILES_DIR / "{0}.json".format(TEST_USER_ID)
    if profile_path.exists():
        profile_path.unlink()

    outputs = []
    for command in [
        "/brush",
        "/brush choose ai",
        "/brush choose design",
        "/brush start",
        "/brush",
        "/brush read",
        "/brush save",
        "/brush refresh",
    ]:
        result = handle_command(command, [], TEST_USER_ID, {})
        message = result.get("message", "")
        outputs.append({"command": command, "message": message, "buttons": result.get("buttons", [])})

    first = outputs[0]["message"]
    _assert("欢迎来到刷博客" in first, "cold start welcome message missing")
    _assert("冷启动进度" in first, "cold start progress missing")

    choose_output = outputs[1]["message"]
    _assert("已选择领域" in choose_output, "interest selection message missing")

    completion = outputs[3]["message"]
    _assert("冷启动完成" in completion, "cold start completion message missing")

    second_feed_output = outputs[4]["message"]
    _assert("还在了解你的口味" in second_feed_output or "稳定推荐模式" in second_feed_output, "quick learning hint missing")

    read_output = outputs[5]["message"]
    _assert("深度阅读" in read_output, "read command failed")

    save_output = outputs[6]["message"]
    _assert("已收藏" in save_output, "save command failed")
    _assert("已沉淀" in save_output or "沉淀失败" in save_output, "sink feedback missing")

    refresh_output = outputs[7]["message"]
    _assert("已换一批" in refresh_output, "refresh command failed")

    behavior_rows = [row for row in _read_jsonl(BEHAVIOR_EVENTS_FILE) if row.get("user_id") == TEST_USER_ID]
    actions = [row.get("action") for row in behavior_rows]
    for expected_action in ["cold_start_view", "cold_start_choose", "cold_start_complete", "view", "read", "save", "refresh"]:
        _assert(expected_action in actions, "behavior action missing: {0}".format(expected_action))

    note_rows = [row for row in _read_jsonl(SAVED_NOTES_FILE) if row.get("user_id") == TEST_USER_ID]
    _assert(len(note_rows) >= 1, "saved note missing")
    _assert(bool(note_rows[-1].get("title")), "saved note title missing")

    print("M8 smoke test PASS")
    print("checked commands: {0}".format(", ".join(row["command"] for row in outputs)))
    print("behavior events: {0}".format(len(behavior_rows)))
    print("saved notes: {0}".format(len(note_rows)))


if __name__ == "__main__":
    _run()
