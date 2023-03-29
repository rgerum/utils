import numpy as np
from pathlib import Path
import inspect


def cache(filename, version=1, force_write=False):
    """ a decorator to cache the output of a function that takes a folder as its first argument
    :parameter
    filename: the filename of the cache
    version: the version number of the function, if increased overwrite earlier cache versions
    force_write: weather to always write to the cache, disable reading the cache (for testing the function)
    """
    def wrap(func):
        def wrapped_func(folder, *args, **kwargs):
            # get args
            all_args = inspect.getcallargs(func, folder, *args, **kwargs)
            # join the path and add arguments into filename
            output_path = Path(folder) / filename.format(**all_args)
            # if the output path exists
            if output_path.exists() and not force_write:
                # load from cache
                loaded = np.load(output_path, allow_pickle=True)
                # only return it if the version is the current one
                if loaded.get("version", None) == version:
                    try:
                        return tuple(loaded["output"])
                    except TypeError:
                        return loaded["output"][()]
            # call the function
            output = func(folder, *args, **kwargs)
            # save the result
            np.savez(output_path, output=output, version=version)
            # return
            return output
        return wrapped_func
    return wrap
