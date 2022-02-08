import os
import bpy

# File and directory handling


def get_path():
    """returns addon path"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_addon_name():
    """returns file path name of calling file"""
    return os.path.basename(get_path())


def get_prefs():
    """returns MakeTile preferences"""
    return bpy.context.preferences.addons[get_addon_name()].preferences
