# encoding: utf-8

import os
import json
from DEFINE import TEMPLATE_PATH, DISPLAY_PATH
from data_process.formatter import format_workflow_diagram, conversation_analyze


with open(os.path.join(TEMPLATE_PATH, "all.json"), "r", encoding="utf-8") as f:
    data = json.load(f)


PAPER = []

tree = {}

for k, v in data.items():
    catalog = v.get('catalog')
    items = v.get('items')
    _ = json.loads(k)
    _workflow = _.get('workflow')
    _branch_rules = _.get('branch_rules')
    display = format_workflow_diagram(_workflow, _branch_rules)

    if not tree.get(catalog):
        tree[catalog] = [
            [display, items]
        ]
    else:
        tree[catalog].append([display, items])


BLANK_LINE_LENGTH = 100

for catalog, contents in tree.items():
    with open(os.path.join(DISPLAY_PATH, f"{catalog}.txt"), "w", encoding="utf-8") as f:
        f.write('=' * BLANK_LINE_LENGTH + "\n")
        for display, items in contents:
            f.write(f"{display}\n")
            f.write("-" * BLANK_LINE_LENGTH + "\n")
            for item in items:
                f.write(f"{item}\n")
            f.write("=" * BLANK_LINE_LENGTH + "\n\n")

