# Copyright (c) 2013 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import random

import numpy
import pytest

from annoy import AnnoyIndex


def test_numpy(n_points=1000, n_trees=10):
    f = 10
    i = AnnoyIndex(f, "euclidean")
    for j in range(n_points):
        a = numpy.random.normal(size=f)
        a = a.astype(
            random.choice([numpy.float64, numpy.float32, numpy.uint8, numpy.int16])
        )
        i.add_item(j, a)

    i.build(n_trees)


def test_tuple(n_points=1000, n_trees=10):
    f = 10
    i = AnnoyIndex(f, "euclidean")
    for j in range(n_points):
        i.add_item(j, tuple(random.gauss(0, 1) for x in range(f)))

    i.build(n_trees)


def test_wrong_length(n_points=1000, n_trees=10):
    f = 10
    i = AnnoyIndex(f, "euclidean")
    i.add_item(0, [random.gauss(0, 1) for x in range(f)])
    with pytest.raises(IndexError):
        i.add_item(1, [random.gauss(0, 1) for x in range(f + 1000)])
    with pytest.raises(IndexError):
        i.add_item(2, [])

    i.build(n_trees)


def test_range_errors(n_points=1000, n_trees=10):
    f = 10
    i = AnnoyIndex(f, "euclidean")
    for j in range(n_points):
        i.add_item(j, [random.gauss(0, 1) for x in range(f)])
    with pytest.raises(IndexError):
        i.add_item(-1, [random.gauss(0, 1) for x in range(f)])
    i.build(n_trees)
    for bad_index in [-1000, -1, n_points, n_points + 1000]:
        with pytest.raises(IndexError):
            i.get_distance(0, bad_index)
        with pytest.raises(IndexError):
            i.get_nns_by_item(bad_index, 1)
        with pytest.raises(IndexError):
            i.get_item_vector(bad_index)


def test_missing_len():
    """
    We should get a helpful error message if our vector doesn't have a
    __len__ method.
    """

    class FakeCollection:
        pass

    i = AnnoyIndex(10, "euclidean")
    with pytest.raises(TypeError) as excinfo:
        i.add_item(1, FakeCollection())
    assert str(excinfo.value) == "object of type 'FakeCollection' has no len()"


def test_missing_getitem():
    """
    We should get a helpful error message if our vector doesn't have a
    __getitem__ method.
    """

    class FakeCollection:
        def __len__(self):
            return 5

    i = AnnoyIndex(5, "euclidean")
    with pytest.raises(TypeError) as excinfo:
        i.add_item(1, FakeCollection())
    assert str(excinfo.value) == "'FakeCollection' object is not subscriptable"


def test_short():
    """
    Ensure we handle our vector not being long enough.
    """

    class FakeCollection:
        def __len__(self):
            return 3

        def __getitem__(self, i):
            raise IndexError

    i = AnnoyIndex(3, "euclidean")
    with pytest.raises(IndexError):
        i.add_item(1, FakeCollection())


def test_non_float():
    """
    We should error gracefully if non-floats are provided in our vector.
    """
    array_strings = ["1", "2", "3"]

    i = AnnoyIndex(3, "euclidean")
    with pytest.raises(TypeError) as excinfo:
        i.add_item(1, array_strings)
    assert str(excinfo.value) == "must be real number, not str"
