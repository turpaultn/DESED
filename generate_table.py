import os
import re


def concat_files(readme):
    result_doc = ""
    matched = False
    with open(readme, "r+", encoding="utf-8") as f:
        for line in f.readlines():
            if not matched:
                result_doc += line

            match = re.search(r"<!--(|\s+)include (.+)(^$|\s+)-->", line)
            if match and not matched:
                matched = True
                fname = match.group(2)
                with open(fname, "r") as inc:
                    for ll in inc:
                        result_doc += ll
            elif re.search(r"<!--(|\s+)end(|\s+)-->", line):
                matched = False
                result_doc += "\n" + line
                print("skip")
                continue

    print(result_doc)

    with open(readme, "w") as f:
        print("writing")
        f.write(result_doc)


if __name__ == '__main__':
    concat_files("README.md")
