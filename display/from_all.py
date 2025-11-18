# encoding: utf-8

import os
import json
from DEFINE import TEMPLATE_PATH, DISPLAY_PATH
from data_process.formatter import format_workflow_diagram, conversation_analyze


with open(os.path.join(TEMPLATE_PATH, "all_ds.json"), "r", encoding="utf-8") as f:
    data = json.load(f)


PAPER = []

tree = {}

for k, v in data.items():
    catalog = v.get('catalog')
    items = v.get('items')
    _ = json.loads(k)
    _workflow = _.get('workflow')
    _branch_rules = _.get('branch_rules')
    show_name = v.get('show_name')
    display = format_workflow_diagram(_workflow, _branch_rules)

    if not tree.get(catalog):
        tree[catalog] = [
            [display, show_name, items]
        ]
    else:
        tree[catalog].append([display, show_name, items])


BLANK_LINE_LENGTH = 100

for catalog, contents in tree.items():
    with open(os.path.join(DISPLAY_PATH, f"{catalog}.txt"), "w", encoding="utf-8") as f:
        f.write('=' * BLANK_LINE_LENGTH + "\n")
        for display, show_name, items in contents:
            f.write(f"[{show_name}]\n")
            f.write(f"{display}\n")
            f.write("-" * BLANK_LINE_LENGTH + "\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("=" * BLANK_LINE_LENGTH + "\n")


with open(os.path.join(DISPLAY_PATH, f"all_ds.txt"), "w", encoding="utf-8") as f:
    for catalog, contents in tree.items():
        f.write('=' * BLANK_LINE_LENGTH + "\n")
        for display, show_name, items in contents:
            f.write(f"[{catalog}] - [{show_name}]\n")
            f.write(f"{display}\n")
            f.write("-" * BLANK_LINE_LENGTH + "\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("=" * BLANK_LINE_LENGTH + "\n")

