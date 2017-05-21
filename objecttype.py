import bpy, bmesh, mathutils
import json
import os
import copy
import math
from .prefab import Prefab

def CreateTriggerMaterial():
    mat = bpy.data.materials.get("Trigger")
    if mat == None:
        bpy.data.materials.new("Trigger")
        mat = bpy.data.materials.get("Trigger")
        mat.diffuse_color = [0.0, 0.8, 0.0]
        mat.use_shadeless = True
        mat.use_transparency = True
        mat.alpha = 0.5

def LevelPropertyTypeChanged(self, context):
    # Reset material
    CreateTriggerMaterial()
    mat = bpy.data.materials.get("Material")
    self.show_transparent = False
    self.show_wire = False
    self.show_axis = False
    if self.data.materials:
        self.data.materials[0] = mat
    else:
        self.data.materials.append(mat)
    
    if self.ObjectType == "Trigger":
        mat = bpy.data.materials.get("Trigger")
        self.show_transparent = True
        self.show_wire = True
        if self.data.materials:
            self.data.materials[0] = mat
        else:
            self.data.materials.append(mat)
    
    return None

bpy.types.Object.ObjectType = bpy.props.EnumProperty(
    items=[
        ("Door", "Door", "a door object"),
        ("Button", "Button", "a button object"),
        ("Trigger", "Trigger", "trigger volume"),
        ("Push", "Push", "push object"),
        ("Prefab", "Prefab", "Prefab object"),
        ("None", "None", "no object")
    ],
    name="Object Type",
    description="Type of the selected object",
    default="None",
    update=LevelPropertyTypeChanged
)

bpy.types.Object.door_open_speed = bpy.props.FloatProperty(
    name="Door Open Speed",
    default = 1,
    step=100,
    precision=2
)

bpy.types.Object.door_open_direction = bpy.props.FloatVectorProperty(
    name="Door Open Direction",
    default=(0.0,1.0,0.0),
    step=10,
    precision=2
)

def AddToTargets(self, context):
    if self.TriggerTarget != "":
        if len(self.TriggerTargets) > 0:
            self.TriggerTargets = self.TriggerTargets + ";" + self.TriggerTarget
        else:
            self.TriggerTargets = self.TriggerTarget
        self.TriggerTarget = ""

bpy.types.Object.TriggerTarget = bpy.props.StringProperty(
    name="Target",
    description="Target Object",
    default="",
    update = AddToTargets
)

bpy.types.Object.TriggerTargets = bpy.props.StringProperty(
    name="Targets",
    description="Target Object",
    default=""
)

bpy.types.Object.PushDirection = bpy.props.FloatVectorProperty(
    name="Push Direction",
    default=(0.0,1.0,0.0),
    step=10,
    precision=2
)

bpy.types.Object.PushDistance = bpy.props.FloatProperty(
    name="Push Distance",
    default = 1,
    step=100,
    precision=2
)

bpy.types.Object.PushObjectType = bpy.props.StringProperty(
    name="Push Object Type",
    description="Push Object Type",
    default="Default"
)

class LevelPropertiesMenu(bpy.types.Panel):
    bl_label = 'Level Properties'
    bl_idname = 'ui.level_properties'
    bl_category = 'Level Editor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Test", icon="OBJECT_DATA")
        
        scene = bpy.context.scene
        
        active_object = context.active_object
        if active_object != None:
            layout.prop(active_object, "ObjectType", text="Type")
            
            if active_object.ObjectType == "Door":
                layout.prop(active_object, "door_open_speed", text="Open Speed")
                layout.prop(active_object, "door_open_direction", text="Open Direction")
            elif active_object.ObjectType == "Trigger":
                layout.prop_search(active_object, "TriggerTarget", scene, "objects")
                layout.prop(active_object, "TriggerTargets", text="Targets")
            elif active_object.ObjectType == "Push":
                layout.prop(active_object, "PushObjectType", text="Push Object Type")
                layout.prop(active_object, "PushDirection", text="Push Direction")
                layout.prop(active_object, "PushDistance", text="Push Distance")
            elif active_object.ObjectType == "Prefab":
                layout.operator("object.create_prefabs")
                layout.prop_search(active_object, "PrefabName", scene, "Prefabs")
        
    def register():
        Prefab.register()
    
    def unregister():
        Prefab.unregister()
