# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import os, json
from learnbot_dsl.blocksConfig.blocks import pathBlocks as pathImgBlocks

pathConfig = os.path.dirname(os.path.realpath(__file__))

def reload_functions(file=None):
    blocks = None
    pathsConfig = [pathConfig,
                   os.path.join(os.getenv('HOME'), ".learnblock", "block")
                   ]
    if file is None:
        for path in pathsConfig:
            if not os.path.exists(path):
                continue
            for f in os.listdir(path):
                if os.path.splitext(f)[-1] == ".conf":
                    f = os.path.join(path, f)
                    print(f)
                    with open(f, "rb") as f:
                        text = f.read()
                    if blocks is None:
                        blocks = json.loads(text)
                    else:
                        blocks += json.loads(text)
    else:
        with open(file, "r") as f:
            text = f.read()
        blocks = json.loads(text)
    for b in blocks:
        for i in range(len(b["img"])):
            b["img"][i] = os.path.join(pathImgBlocks, b["img"][i])

    return blocks


if __name__ == '__main__':
    blocks = reload_functions()
    from learnbot_dsl.functions import getFuntions
    functions = getFuntions()
    nameconfigBlocks = [x["name"] for x in blocks]
    for x in nameconfigBlocks:
        if x not in functions:
            print(x)