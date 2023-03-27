import pandas as pd
from pathlib import Path


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
        for part in re.split("(\([^)]*\))", regexp_string):
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
        if match is None:
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
    return pd.DataFrame(data)


if __name__ == "__main__":
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt", "run_nodes7_name-Foo.txt", "run_nodes7.8_name-Bar.txt"],
            "run-2": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt", "run_nodes7_name-Foo.txt", "run_nodes7.8_name-Bar.txt"],
        }
    }
    with MockDir(file_structure):
        # get files from one folder
        for filename, data in format_glob("tmp/run-1/run_nodes{n}_name-{name}.txt"):
            print(filename, data)
        """
        tmp/run-1/run_nodes4_name-Bob.txt {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}
        tmp/run-1/run_nodes7_name-Foo.txt {'n': '7', 'name': 'Foo', 'filename': 'tmp/run-1/run_nodes7_name-Foo.txt'}
        tmp/run-1/run_nodes7.8_name-Bar.txt {'n': '7.8', 'name': 'Bar', 'filename': 'tmp/run-1/run_nodes7.8_name-Bar.txt'}
        tmp/run-1/run_nodes3_name-Alice.txt {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}
        """

        # get all sub folders
        for filename, data in format_glob("tmp/**/run_nodes{n}_name-{name}.txt"):
            print(filename, data)
        """                
        tmp/run-2/run_nodes4_name-Bob.txt {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-2/run_nodes4_name-Bob.txt'}
        tmp/run-2/run_nodes7_name-Foo.txt {'n': '7', 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes7_name-Foo.txt'}
        tmp/run-2/run_nodes7.8_name-Bar.txt {'n': '7.8', 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes7.8_name-Bar.txt'}
        tmp/run-2/run_nodes3_name-Alice.txt {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-2/run_nodes3_name-Alice.txt'}
        tmp/run-1/run_nodes4_name-Bob.txt {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}
        tmp/run-1/run_nodes7_name-Foo.txt {'n': '7', 'name': 'Foo', 'filename': 'tmp/run-1/run_nodes7_name-Foo.txt'}
        tmp/run-1/run_nodes7.8_name-Bar.txt {'n': '7.8', 'name': 'Bar', 'filename': 'tmp/run-1/run_nodes7.8_name-Bar.txt'}
        tmp/run-1/run_nodes3_name-Alice.txt {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}
        """

        # convert to int or float
        for filename, data in format_glob("tmp/run-{run:d}/run_nodes{n:f}_name-{name}.txt"):
            print(filename, data)
        """
        tmp/run-2/run_nodes4_name-Bob.txt {'run': 2, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-2/run_nodes4_name-Bob.txt'}
        tmp/run-2/run_nodes7_name-Foo.txt {'run': 2, 'n': 7.0, 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes7_name-Foo.txt'}
        tmp/run-2/run_nodes7.8_name-Bar.txt {'run': 2, 'n': 7.8, 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes7.8_name-Bar.txt'}
        tmp/run-2/run_nodes3_name-Alice.txt {'run': 2, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-2/run_nodes3_name-Alice.txt'}
        tmp/run-1/run_nodes4_name-Bob.txt {'run': 1, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}
        tmp/run-1/run_nodes7_name-Foo.txt {'run': 1, 'n': 7.0, 'name': 'Foo', 'filename': 'tmp/run-1/run_nodes7_name-Foo.txt'}
        tmp/run-1/run_nodes7.8_name-Bar.txt {'run': 1, 'n': 7.8, 'name': 'Bar', 'filename': 'tmp/run-1/run_nodes7.8_name-Bar.txt'}
        tmp/run-1/run_nodes3_name-Alice.txt {'run': 1, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}
        """

        # or get the result as a pandas dataframe
        df = format_glob_pd("tmp/run-{run:d}/run_nodes{n:f}_name-{name}.txt")
        print(df)
        """
           run    n   name                             filename
        0    2  4.0    Bob    tmp/run-2/run_nodes4_name-Bob.txt
        1    2  7.0    Foo    tmp/run-2/run_nodes7_name-Foo.txt
        2    2  7.8    Bar  tmp/run-2/run_nodes7.8_name-Bar.txt
        3    2  3.0  Alice  tmp/run-2/run_nodes3_name-Alice.txt
        4    1  4.0    Bob    tmp/run-1/run_nodes4_name-Bob.txt
        5    1  7.0    Foo    tmp/run-1/run_nodes7_name-Foo.txt
        6    1  7.8    Bar  tmp/run-1/run_nodes7.8_name-Bar.txt
        7    1  3.0  Alice  tmp/run-1/run_nodes3_name-Alice.txt
        """
