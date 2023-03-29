import pandas as pd
from format_glob import format_glob, format_glob_pd, path_not_found_message
from pathlib import Path


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
        ['tmp/run-1/run_nodes3_name-Alice.txt',
         {'n': '3', 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'}],
        ['tmp/run-1/run_nodes4_name-Bob.txt',
         {'n': '4', 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'}],
    ]
    assert sorted(collected_data) == sorted(target_data)


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
    assert sorted(collected_data) == sorted(target_data)


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
    assert sorted(collected_data) == sorted(target_data)


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

        import io
        import contextlib
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            df2 = format_glob_pd("tmp2/run-{run:d}/run_nodes{n:f}_name-{name}.txt")
        assert f.getvalue() == F'WARNING: in folder "{Path(__file__).parent}" no file/folder "tmp2" found. Did you mean "tmp"?\n'

    # compare with target
    target_data = pd.DataFrame([
        {'run': 1, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt'},
        {'run': 1, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt'},
        {'run': 2, 'n': 4.0, 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes4_name-Bar.txt'},
        {'run': 2, 'n': 3.0, 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes3_name-Foo.txt'},
    ])
    pd.testing.assert_frame_equal(df.sort_values(by=['filename']).reset_index(drop=True),
                                  target_data.sort_values(by=['filename']).reset_index(drop=True))


def test_format_template():
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
        for (filename, data) in format_glob("tmp/run-{run:d}/run_nodes{n:f}_name-{name}.txt", return_template=True):
            collected_data.append([filename, data])

    # compare with target
    target_data = [
        ['tmp/run-2/run_nodes3_name-Foo.txt', {'run': 2, 'n': 3.0, 'name': 'Foo', 'filename': 'tmp/run-2/run_nodes3_name-Foo.txt', 'template': 'tmp/run-{__int__run>[0-}/run_nodes{__float__n>[0-9}_name-{name}.txt'}],
        ['tmp/run-2/run_nodes4_name-Bar.txt', {'run': 2, 'n': 4.0, 'name': 'Bar', 'filename': 'tmp/run-2/run_nodes4_name-Bar.txt', 'template': 'tmp/run-{__int__run>[0-}/run_nodes{__float__n>[0-9}_name-{name}.txt'}],
        ['tmp/run-1/run_nodes4_name-Bob.txt', {'run': 1, 'n': 4.0, 'name': 'Bob', 'filename': 'tmp/run-1/run_nodes4_name-Bob.txt', 'template': 'tmp/run-{__int__run>[0-}/run_nodes{__float__n>[0-9}_name-{name}.txt'}],
        ['tmp/run-1/run_nodes3_name-Alice.txt', {'run': 1, 'n': 3.0, 'name': 'Alice', 'filename': 'tmp/run-1/run_nodes3_name-Alice.txt', 'template': 'tmp/run-{__int__run>[0-}/run_nodes{__float__n>[0-9}_name-{name}.txt'}],
    ]
    assert sorted(collected_data) == sorted(target_data)


def test_not_found_message():
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
        assert path_not_found_message("tmp/run-3/run_nodes3_name-Foo.txt") == F'WARNING: in folder "{Path(__file__).parent}/tmp" no file/folder "run-3" found. Did you mean "run-2"?'
        assert path_not_found_message("tmp/run-*/run_nodes5_name-Foo.txt") == F'WARNING: in any of the 2 folders matching the pattern "{Path(__file__).parent}/tmp/run-*" no file/folder "run_nodes5_name-Foo.txt" found'
        assert path_not_found_message("tmp/run-*/run_nodes5_name-*.txt") == F'WARNING: in any of the 2 folders matching the pattern "{Path(__file__).parent}/tmp/run-*" pattern "run_nodes5_name-*.txt" not found'
        assert path_not_found_message("tmp/*-1/run_nodes5_name-*.txt") == F'WARNING: in the only folder matching the pattern "{Path(__file__).parent}/tmp/*-1" pattern "run_nodes5_name-*.txt" not found'
