import bpy, bmesh, mathutils
import json
import os, sys
import copy
import math
import pdb
from .leveleditorconfig import prefab_list_path

class MeshPropertyGroup(bpy.types.PropertyGroup):
    mesh_path = bpy.props.StringProperty(name="MeshPath", description="")
    xPos = bpy.props.FloatProperty(name="xPos")
    yPos = bpy.props.FloatProperty(name="yPos")
    zPos = bpy.props.FloatProperty(name="zPos")
    
    xRot = bpy.props.FloatProperty(name="xRot")
    yRot = bpy.props.FloatProperty(name="yRot")
    zRot = bpy.props.FloatProperty(name="zRot")
    
    assetXRot = bpy.props.FloatProperty(name="assetXRot")
    assetYRot = bpy.props.FloatProperty(name="assetYRot")
    assetZRot = bpy.props.FloatProperty(name="assetZRot")
    
    xScale = bpy.props.FloatProperty(name="xScale")
    yScale = bpy.props.FloatProperty(name="yScale")
    zScale = bpy.props.FloatProperty(name="zScale")

class PrefabPropertyGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Name", description="")
    model = bpy.props.StringProperty(name="Model", description="")
    models = bpy.props.StringProperty(name="Models", description="")
    meshes = bpy.props.CollectionProperty(type=MeshPropertyGroup, name="Meshes")

def ChangePrefab(self, context):
    model_file_path = bpy.context.scene.Prefabs[self.PrefabName].models

    if model_file_path != "":
        self.show_axis = False
        
        objects_before_import = set()
        for object in bpy.context.scene.objects:
            objects_before_import.add(object.name)

        merged_mesh = bmesh.new()
        for mesh in bpy.context.scene.Prefabs[self.PrefabName].meshes:
            
            previous_objects = set()
            for object in bpy.context.scene.objects:
                previous_objects.add(object.name)
            
            print(mesh.mesh_path)
            bpy.ops.import_scene.fbx(filepath=mesh.mesh_path, axis_forward="Z", axis_up="Y")
        
            objects = set()
            for object in bpy.context.scene.objects:
                objects.add(object.name)
            
            for object in objects - previous_objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[object].select = True
                
                bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
                bpy.data.objects[object].rotation_euler = mathutils.Euler((math.radians(-mesh.assetXRot), math.radians(mesh.assetZRot), math.radians(mesh.assetYRot)), 'XYZ')
                bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
                
                bpy.data.objects[object].scale = mathutils.Vector((mesh.xScale, mesh.zScale, mesh.yScale))
                bpy.data.objects[object].rotation_euler = mathutils.Euler((math.radians(mesh.xRot), math.radians(mesh.zRot), math.radians(mesh.yRot)), 'XYZ')                
                bpy.data.objects[object].location = mathutils.Vector((-mesh.xPos, -mesh.zPos, mesh.yPos))
                bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
                bpy.data.objects[object].rotation_euler = mathutils.Euler((math.radians(0.0), math.radians(0.0), math.radians(180)), 'XYZ')
                bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)                                
                merged_mesh.from_mesh(bpy.data.objects[object].data)
        
        m = bpy.data.meshes.new(self.PrefabName)
        merged_mesh.to_mesh(m)
        self.data = m

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(self.data)

        origin_vertex = bm.verts.new((0.0, 0.0, 0.0))
        x_vertex = bm.verts.new((1.0, 0.0, 0.0))
        y_vertex = bm.verts.new((0.0, -1.0, 0.0))
        z_vertex = bm.verts.new((0.0, 0.0, 1.0))

        bm.verts.ensure_lookup_table()

        # Add edges
        bm.edges.new((origin_vertex, x_vertex))
        bm.edges.new((origin_vertex, y_vertex))
        bm.edges.new((origin_vertex, z_vertex))

        bpy.ops.object.mode_set(mode='OBJECT')


        if self.vertex_groups.find('Origin') == -1:
            self.vertex_groups.new('Origin')
        self.vertex_groups['Origin'].add([len(self.data.vertices)-4], 1.0, 'ADD')

        if self.vertex_groups.find('X') == -1:
            self.vertex_groups.new('X')
        self.vertex_groups['X'].add([len(self.data.vertices)-3], 1.0, 'ADD')

        if self.vertex_groups.find('Y') == -1:
            self.vertex_groups.new('Y')
        self.vertex_groups['Y'].add([len(self.data.vertices)-2], 1.0, 'ADD')

        if self.vertex_groups.find('Z') == -1:
            self.vertex_groups.new('Z')
        self.vertex_groups['Z'].add([len(self.data.vertices)-1], 1.0, 'ADD')
        
        
            
        objects_after_import = set()
        for object in bpy.context.scene.objects:
            objects_after_import.add(object.name)

        #Delete imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for object in objects_after_import - objects_before_import:
            bpy.data.objects[object].select = True
            print(object)
        bpy.ops.object.delete()
    else:
        self.show_axis = True
        self.data = bpy.data.meshes['Cube']

class CreatePrefabs(bpy.types.Operator):
    bl_idname = "object.create_prefabs"
    bl_label = "Minimal Operator"

    def execute(self, context):
        prefab_file_path = prefab_list_path()
        if os.path.isfile(prefab_file_path):
            bpy.context.scene.Prefabs.clear()
            prefab_file = open(prefab_file_path, 'r')
            data = json.load(prefab_file)
            
            for p in data["Prefabs"]:
                prefab = bpy.context.scene.Prefabs.add()
                prefab.name = p["PrefabName"]
                prefab.model = p["MeshPath"]
                prefab.models = ""      
                
                prefab.meshes.clear()
                for mesh in p["Meshes"]:
                    m = prefab.meshes.add()
                    m.mesh_path = mesh["MeshPath"]
                    m.xPos = mesh["xPos"]
                    m.yPos = mesh["yPos"]
                    m.zPos = mesh["zPos"]
                    
                    m.xRot = mesh["xRot"]
                    m.yRot = mesh["yRot"]
                    m.zRot = mesh["zRot"]
                    
                    m.assetXRot = mesh["assetXRot"]
                    m.assetYRot = mesh["assetYRot"]
                    m.assetZRot = mesh["assetZRot"]
                    
                    m.xScale = mesh["xScale"]
                    m.yScale = mesh["yScale"]
                    m.zScale = mesh["zScale"]

                for model in p["MeshPaths"]:
                    if prefab.models == "":
                        prefab.models = model
                    else:
                        prefab.models = prefab.models + ";" + model

        return {'FINISHED'}

class Prefab:
    def register():
        bpy.utils.register_class(MeshPropertyGroup)
        bpy.utils.register_class(PrefabPropertyGroup)
        bpy.utils.register_class(CreatePrefabs)
        bpy.types.Object.PrefabName = bpy.props.StringProperty(
            name="Prefab Name",
            description="Prefab Object",
            default="",
            update=ChangePrefab
        )

        bpy.types.Scene.Prefabs = bpy.props.CollectionProperty(type=PrefabPropertyGroup)

    def unregister():
        bpy.utils.unregister_class(MeshPropertyGroup)
        bpy.utils.unregister_class(PrefabPropertyGroup)
        bpy.utils.unregister_class(CreatePrefabs)
        del sys.modules['LevelEditor.prefab']