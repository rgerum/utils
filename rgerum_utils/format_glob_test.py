import pandas as pd
from format_glob import format_glob, format_glob_pd

""" Tests """
def test_simple_folder():
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt"],
            "run-2": ["run_nodes3_name-Foo.txt", "run_nodes4_name-Bar.txt"],
        }
    }
    collected_data = []
    with MockDir(file_structure):
        # get files from one folder
        for (filename, data) in format_glob("tmp/run-1/run_nodes{n}_name-{name}.txt"):
            collected_data.append([filename, data])

    # compare with target
    target_data = [
        ['tmp/run-1/run_nodes4_name-Bob.txt',
         {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}],
        ['tmp/run-1/run_nodes3_name-Alice.txt',
         {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}],
    ]
    assert collected_data == target_data


def test_glob_folder():
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt"],
            "run-2": ["run_nodes3_name-Foo.txt", "run_nodes4_name-Bar.txt"],
        }
    }
    collected_data = []
    with MockDir(file_structure):
        # get files from one folder
        for (filename, data) in format_glob("tmp/*/run_nodes{n}_name-{name}.txt"):
            collected_data.append([filename, data])

    # compare with target
    target_data = [
        ['tmp/run-2/run_nodes3_name-Foo.txt', {'n': '3', 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes3_name-Foo.txt'}],
        ['tmp/run-2/run_nodes4_name-Bar.txt', {'n': '4', 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes4_name-Bar.txt'}],
        ['tmp/run-1/run_nodes4_name-Bob.txt', {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}],
        ['tmp/run-1/run_nodes3_name-Alice.txt', {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}],
    ]
    assert collected_data == target_data


def test_format_numbers():
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt"],
            "run-2": ["run_nodes3_name-Foo.txt", "run_nodes4_name-Bar.txt"],
        }
    }
    collected_data = []
    with MockDir(file_structure):
        # get files from one folder
        for (filename, data) in format_glob("tmp/run-{run:d}/run_nodes{n:f}_name-{name}.txt"):
            collected_data.append([filename, data])

    # compare with target
    target_data = [
        ['tmp/run-2/run_nodes3_name-Foo.txt', {'run': 2, 'n': 3.0, 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes3_name-Foo.txt'}],
        ['tmp/run-2/run_nodes4_name-Bar.txt', {'run': 2, 'n': 4.0, 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes4_name-Bar.txt'}],
        ['tmp/run-1/run_nodes4_name-Bob.txt', {'run': 1, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}],
        ['tmp/run-1/run_nodes3_name-Alice.txt', {'run': 1, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}],
    ]
    assert collected_data == target_data


def test_pandas():
    from mock_dir import MockDir
    # to test we create an artificial folder structure
    file_structure = {
        "tmp": {
            "run-1": ["run_nodes3_name-Alice.txt", "run_nodes4_name-Bob.txt"],
            "run-2": ["run_nodes3_name-Foo.txt", "run_nodes4_name-Bar.txt"],
        }
    }
    with MockDir(file_structure):
        df = format_glob_pd("tmp/run-{run:d}/run_nodes{n:f}_name-{name}.txt")

    # compare with target
    target_data = pd.DataFrame([
        {'run': 2, 'n': 3.0, 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes3_name-Foo.txt'},
        {'run': 2, 'n': 4.0, 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes4_name-Bar.txt'},
        {'run': 1, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'},
        {'run': 1, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'},
    ])
    pd.testing.assert_frame_equal(df, target_data)
