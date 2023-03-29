from cache_decorator import cache
from mock_dir import MockDir
import numpy as np

# to test we create an artificial folder structure
file_structure = {
    "tmp": {
        "run-1": [],
        "run-2": [],
    }
}


def test_simple_output_array():
    multiplier = 1
    @cache("out.npz", version=1)
    def func(folder, i):
        nonlocal multiplier
        return np.ones(i)*multiplier

    with MockDir(file_structure):
        results = []
        for i in range(1, 3):
            results.append(func(f"tmp/run-{i}", i))
        multiplier = 2
        results2 = []
        for i in range(1, 3):
            results2.append(func(f"tmp/run-{i}", i))

        for r, r2 in zip(results, results2):
            assert (r == r2).all()


def test_two_output_array():
    multiplier = 1
    @cache("out.npz", version=1)
    def func(folder, i):
        nonlocal multiplier
        return np.ones(i)*multiplier, np.ones(i)*multiplier*10

    with MockDir(file_structure):
        results = []
        for i in range(1, 3):
            results.append(func(f"tmp/run-{i}", i))
        multiplier = 2
        results2 = []
        for i in range(1, 3):
            results2.append(func(f"tmp/run-{i}", i))

        for r, r2 in zip(results, results2):
            assert (r[0] == r2[0]).all()
            assert (r[1] == r2[1]).all()


def test_dict_output():
    multiplier = 1
    @cache("out.npz", version=1)
    def func(folder, i):
        nonlocal multiplier
        return dict(i=i*multiplier, foo="foo")

    with MockDir(file_structure):
        results = []
        for i in range(1, 3):
            results.append(func(f"tmp/run-{i}", i))
        multiplier = 2
        results2 = []
        for i in range(1, 3):
            results2.append(func(f"tmp/run-{i}", i))

        for r, r2 in zip(results, results2):
            assert r == r2


def test_format_filename_output():
    multiplier = 1
    @cache("out_{i}.npz", version=1)
    def func(folder, i):
        nonlocal multiplier
        return dict(i=i*multiplier, foo="foo")

    with MockDir(file_structure):
        results = []
        for i in range(1, 3):
            for j in range(1, 3):
                results.append(func(f"tmp/run-{i}", j))
        multiplier = 2
        results2 = []
        for i in range(1, 3):
            for j in range(1, 3):
                results2.append(func(f"tmp/run-{i}", j))

        for r, r2 in zip(results, results2):
            assert r == r2


def test_different_version():
    multiplier = 1
    @cache("out.npz", version=1)
    def func(folder, i):
        nonlocal multiplier
        return np.ones(i)*multiplier

    with MockDir(file_structure):
        results = []
        for i in range(1, 3):
            results.append(func(f"tmp/run-{i}", i))

        multiplier = 2
        @cache("out.npz", version=1)
        def func(folder, i):  # pragma: no cover
            nonlocal multiplier
            return np.ones(i) * multiplier

        results2 = []
        for i in range(1, 3):
            results2.append(func(f"tmp/run-{i}", i))

        for r, r2 in zip(results, results2):
            assert (r == r2).all()

        multiplier = 2

        @cache("out.npz", version=2)
        def func(folder, i):
            nonlocal multiplier
            return np.ones(i) * multiplier

        results2 = []
        for i in range(1, 3):
            results2.append(func(f"tmp/run-{i}", i))

        for r, r2 in zip(results, results2):
            assert (r != r2).all()