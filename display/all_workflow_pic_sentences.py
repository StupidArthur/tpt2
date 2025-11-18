# encoding: utf-8

import os



def all_sentences():

    with open(os.path.join(os.path.dirname(__file__), "get_all_workflow_pic.yaml"), "r", encoding="utf-8") as f:
        out = [x.strip() for x in f.readlines() if x]

    return out


if __name__ == "__main__":
    out = all_sentences()
    print(out)