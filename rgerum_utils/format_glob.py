import pandas as pd
from pathlib import Path
import glob
import sys


def format_glob(pattern, return_template=False):
    import re
    pattern = str(Path(pattern))
    regexp_string = re.escape(pattern).replace("\\*\\*/", ".*").replace("\\*", ".*")
    regexp_string = re.sub(r"\\{([^}]*):f\\}", r"(?P<__float__\1>[0-9.]*)", regexp_string)
    regexp_string = re.sub(r"\\{([^}]*):d\\}", r"(?P<__int__\1>[0-9]*)", regexp_string)
    regexp_string = re.sub(r"\\{([^}]*)\\}", r"(?P<\1>.*)", regexp_string)

    if return_template is True:
        regexp_string3 = ""
        replacement = ""
        count = 1
        for part in re.split(r"(\([^)]*\))", regexp_string):
            if part.startswith("("):
                regexp_string3 += part
                replacement += f"{{{part[4:-4]}}}"
                count += 1
            else:
                regexp_string3 += f"({part})"
                replacement += f"\\{count}"
                count += 1

    regexp_string2 = re.compile(regexp_string)
    glob_string = re.sub(r"({[^}]*})", "*", pattern)

    output_base = glob_string
    while "*" in str(output_base):
        output_base = Path(output_base).parent

    for file in output_base.rglob(str(Path(glob_string).relative_to(output_base))):#glob.glob(glob_string, recursive=True):
        file = str(Path(file))
        match = regexp_string2.match(file)
        if match is None:  # pragma: no cover
            continue
        group = match.groupdict()
        group["filename"] = file
        group2 = {}
        for col in group.keys():
            if col.startswith("__float__"):
                group2[col[len("__float__"):]] = float(group[col])
            elif col.startswith("__int__"):
                group2[col[len("__int__"):]] = int(group[col])
            else:
                group2[col] = group[col]
        group = group2
        if return_template:
            template_name = re.sub(regexp_string3, replacement, file)
            group["template"] = template_name
        yield file, group


def format_glob_pd(pattern, return_template=False):
    data = []
    for _, d in format_glob(pattern, return_template):
        data.append(d)
    if len(data) == 0:
        print(path_not_found_message(pattern), file=sys.stderr)
    return pd.DataFrame(data)


def path_not_found_message(name):
    def levenshteinDistance(str1, str2):
        m = len(str1)
        n = len(str2)
        d = [[i] for i in range(1, m + 1)]  # d matrix rows
        d.insert(0, list(range(0, n + 1)))  # d matrix columns
        for j in range(1, n + 1):
            for i in range(1, m + 1):
                if str1[i - 1] == str2[j - 1]:  # Python (string) is 0-based
                    substitutionCost = 0
                else:
                    substitutionCost = 1
                d[i].insert(j, min(d[i - 1][j] + 1,
                                   d[i][j - 1] + 1,
                                   d[i - 1][j - 1] + substitutionCost))
        return d[-1][-1]

    # get a list of all parent folders
    name = Path(name).absolute()
    hierarchy = []
    while name.parent != name:
        hierarchy.append(name)
        name = name.parent

    parent_folder_count = 1
    # iterate over the parent folders, starting from the lowest
    for path in hierarchy[::-1]:
        # check if the path exists (or is a glob pattern with matches)
        if "*" in str(path):
            exists = len(glob.glob(str(path)))
        else:
            exists = path.exists()

        # if it does not exist, we have found our problem
        if not exists:
            similar_paths = list([p.name for p in path.parent.glob("*")])
            distances = [levenshteinDistance(p, str(path.name)) for p in similar_paths]
            import numpy as np
            if len(distances) == 0:
                distances = [np.inf]
                similar_paths = ["none"]
            i = np.argmin(distances)

            target = f"no file/folder \"{path.name}\" found"
            if "*" in str(path.name):
                target = f"pattern \"{path.name}\" not found"
            source = f"in folder \"{path.parent}\""
            if "*" in str(path.parent):
                if parent_folder_count == 1:
                    source = f"in the only folder matching the pattern \"{path.parent}\""
                else:
                    source = f"in any of the {parent_folder_count} folders matching the pattern \"{path.parent}\""
            if distances[i] < 10:
                return f"WARNING: {source} {target}. Did you mean \"{similar_paths[i]}\"?"
            else:
                return f"WARNING: {source} {target}"
        parent_folder_count = exists
