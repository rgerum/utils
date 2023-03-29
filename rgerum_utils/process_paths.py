import glob
import sys

from pathlib import Path

from format_glob import format_glob


def processPaths(name, filter=None, file_name=None):
    results = []
    meta_data = []
    # if the function is called with a list or tuple, iterate over those and join the results
    if isinstance(name, (tuple, list)):
        for n in name:
            r, m = processPaths(n, filter=filter, file_name=file_name)
            results.extend(r)
            meta_data.extend(m)
    else:
        # add the file_name pattern if there is one and if it is not already there
        if file_name is not None and Path(name).suffix != Path(file_name).suffix:
            name = Path(name) / "**" / file_name
        # if it is a glob pattern, add all matching elements
        if "{" in str(name):
            for file, data in format_glob(name):
                results.append(file)
                meta_data.append(data)
        elif "*" in str(name):
            results = glob.glob(str(name), recursive=True)
            meta_data = [{}]*len(results)
        # or add the name directly
        elif Path(name).exists():
            results = [name]
            meta_data = [{}]

        # filter results if a filter is provided
        if filter is not None:
            meta_data2 = []
            results2 = []
            for n, m in zip(results, meta_data):
                print("filter", n, filter(n))
                if filter(n):
                    meta_data2.append(m)
                    results2.append(n)
            results = results2
            meta_data = meta_data2

        # if nothing was found, try to give a meaningful error message
        if len(results) == 0:
            # get a list of all parent folders
            name = Path(name).absolute()
            hierarchy = []
            while name.parent != name:
                hierarchy.append(name)
                name = name.parent
            # iterate over the parent folders, starting from the lowest
            for path in hierarchy[::-1]:
                # check if the path exists (or is a glob pattern with matches)
                if "*" in str(path):
                    exists = len(glob.glob(str(path)))
                else:
                    exists = path.exists()
                # if it does not exist, we have found our problem
                if not exists:
                    target = f"No file/folder \"{path.name}\""
                    if "*" in str(path.name):
                        target = f"Pattern \"{path.name}\" not found"
                    source = f"in folder \"{path.parent}\""
                    if "*" in str(path.parent):
                        source = f"in any folder matching the pattern \"{path.parent}\""
                    print(f"WARNING: {target} {source}", file=sys.stderr)
                    break

    return zip(results, meta_data)


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

        # or get the result as a pandas dataframe
        for results, meta_data in processPaths("tmp/**/run_nodes{n:f}_name-{name}x", file_name=".txt"):
            print(results)
            print(meta_data)

