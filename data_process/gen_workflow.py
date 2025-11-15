# encoding: utf-8
import json
import os
import yaml
from test_template.manager import template_manager
from data_process.file_name_process import sanitize_filename
from data_process.formatter import conversation_analyze, ConversationInfo
from DEFINE import TEST_RESULT_PATH, TEMPLATE_PATH

output = {
    "simulation": {},
    "prediction": {},
    "control": {},
    "optimization": {},
    "evaluation": {},
    "statistics": {},
}

out_all = {}


with open(template_manager.standard, "r", encoding="utf-8") as f:
    out = [sanitize_filename(x.strip()) for x in f.readlines() if x]
with open(template_manager.external, "r", encoding="utf-8") as f:
    out.extend([sanitize_filename(x.strip()) for x in f.readlines() if x])

# print(out)

result_files = os.listdir(TEST_RESULT_PATH)
for item in out:
    file = os.path.join(TEST_RESULT_PATH, f"{item}.json")
    try:
        with open(file, "r", encoding="utf-8") as f:
            raw = json.load(f)
            info = conversation_analyze(raw)
            s_key = json.dumps({
                "workflow": info.workflow,
                "branch_rules": info.branch_rules
            }, ensure_ascii=False)
            output[info.catalog][s_key] = ""

            if not out_all.get(s_key):
                out_all[s_key] = {
                    "catalog": info.catalog,
                    "items": [item, ]
                }
            else:
                out_all[s_key]['items'].append(item)

    except Exception as e:
        print(file, e, "!" * 30)


# for k, v in output.items():
#     print(k, len(v))


with open(os.path.join(TEMPLATE_PATH, "all.json"), "w", encoding="utf-8") as f:
    json.dump(out_all, f, ensure_ascii=False, indent=4)

