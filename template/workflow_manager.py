# encoding: utf-8

import os
import json


class Manager(object):
    
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "all_with_name.json"), "r", encoding='utf-8') as f:
            self.data = json.load(f)
        self.name_map = {}
        for w, item in self.data.items():
            _ = json.loads(w)
            item['workflow'] = _.get('workflow')
            item['branch_rules'] = _.get('branch_rules')
            self.name_map[item.get('show_name')] = w

    def by_workflow_and_branch_rules(self, workflow: str, branch_rules: str):
        return self.data.get(
            json.dumps({
                "workflow": workflow,
                "branch_rules": branch_rules
            }, ensure_ascii=False)
        )

    def by_name(self, name: str):
        return self.data.get(
            self.name_map.get(name)
        )


workflow_manager = Manager()