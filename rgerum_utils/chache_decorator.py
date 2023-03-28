import numpy as np
from pathlib import Path


def cache(filename, version=1, force_write=False):
    """ a decorator to cache the output of a function that takes a folder as its first argument
    :parameter
    filename: the filename of the cache
    version: the version number of the function, if increased overwrite earlier cache versions
    force_write: weather to always write to the cache, disable reading the cache (for testing the function)
    """
    def wrap(func):
        def wrapped_func(folder, *args, **kwargs):
            output_path = Path(folder) / filename
            if output_path.exists() and not force_write:
                loaded = np.load(output_path, allow_pickle=True)
                if loaded["version"] == version:
                    return tuple(loaded["output"])
            output = func(folder, *args, **kwargs)
            np.savez(output_path, output=output, version=version)
            return output
        return wrapped_func
    return wrap


if __name__ == "__main__":
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": [],
            "run-2": [],
        }
    }

    @cache("out.npz", version=1)
    def func(folder, i):
        print("run func", folder, i)
        return np.ones(i), np.zeros(i)

    with MockDir(file_structure):
        for i in range(1, 3):
            print(func(f"tmp/run-{i}", i))
        for i in range(1, 3):
            print(func(f"tmp/run-{i}", i))

    @cache("out.npz", version=2)
    def func(folder, i):
        print("run func", folder, i)
        return np.ones(i*2), np.zeros(i*2)

    with MockDir(file_structure):
        for i in range(1, 3):
            print(func(f"tmp/run-{i}", i))
        for i in range(1, 3):
            print(func(f"tmp/run-{i}", i))

