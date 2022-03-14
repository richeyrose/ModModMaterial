import pytest
import bmesh
import bpy


@pytest.fixture
def bpy_module(cache):
    return cache.get("bpy_module", None)
