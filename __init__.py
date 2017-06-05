bl_info = {
    "name":        "Level Editor",
    "description": "Tools for creating video game levels.",
    "author":      "Sean Humeniuk",
    "version":     (0, 0, 1),
    "blender":     (2, 7, 8),
    "location":    "View 3D > Tool Shelf",
    "warning":     "",  # used for warning icon and text in addons panel
    "category":    "3D View"
}

import bpy
import sys
from .objecttype import LevelPropertiesMenu
from .level import Level
from .brush import Brush
from .materialpainter import MaterialPainter

def register():
    bpy.utils.register_class(Level)
    Brush.register()
    bpy.utils.register_class(LevelPropertiesMenu)
    bpy.utils.register_class(MaterialPainter)

def unregister():
    bpy.utils.unregister_class(LevelPropertiesMenu)
    Brush.unregister()
    bpy.utils.unregister_class(Level)
    bpy.utils.unregister_class(MaterialPainter)
    del sys.modules['LevelEditor']