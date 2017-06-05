import bpy
import sys
from mathutils import Vector, Matrix
import pdb
import math

def assign_brush_vertex_colors():
    sectors = []
    for obj in bpy.context.scene.objects:
        if obj.BrushType != "None":
            sectors.append(obj.name)

    for i, sector_name in enumerate(sectors):
        sector = bpy.data.objects[sector_name]
        sector_num = i
        col = (sector_num // 400 * 0.05, sector_num // 20 * 0.05, sector_num % 20 * 0.05)
        
        if 'Col' not in sector.data.vertex_colors.keys():
            sector.data.vertex_colors.new('Col')

        if 'White' not in sector.data.vertex_colors.keys():
            sector.data.vertex_colors.new('White')
        
        for i in range(len(sector.data.vertex_colors['Col'].data)):
            sector.data.vertex_colors['Col'].data[i].color = col
            sector.data.vertex_colors['White'].data[i].color = (1.0, 1.0, 1.0)

        sector.data.vertex_colors['White'].active = True

def color_compare(c1, c2):
    c1_255 = (math.floor(c1[0] * 255), math.floor(c1[1] * 255), math.floor(c1[2] * 255))
    c2_255 = (math.floor(c2[0] * 255), math.floor(c2[1] * 255), math.floor(c2[2] * 255))
    return abs(c1_255[0] - c2_255[0]) <= 1 and abs(c1_255[1] - c2_255[1]) <= 1 and abs(c1_255[2] - c2_255[2]) <= 1

def separate_sectors():
    
    sectors = {k: v for k, v in bpy.data.objects.items() if v.ObjectType == 'Brush' and v.BrushType == 'Sector'}
    map = bpy.data.objects[bpy.context.scene.LevelName]

    bpy.ops.object.select_all(action='DESELECT')
    map.select = True

    if 'UV_Grid' not in bpy.data.images.keys():
        bpy.ops.image.new(name='UV_Grid', width=512, height=512, generated_type='UV_GRID')

    for sector in sectors:
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        map.select = True
        bpy.context.scene.objects.active = map

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        mesh = map.data
        color_layer = mesh.vertex_colors['Col']
        tk = {}
        i = 0
        for poly in mesh.polygons:
            for idx in poly.loop_indices:
                loop = mesh.loops[idx]
                v = loop.vertex_index
                linked = tk.get(v, [])
                linked.append(color_layer.data[idx].color)
                tk[v] = linked
                i += 1
        
        color = bpy.data.objects[sector].data.vertex_colors['Col'].data[0].color
        select_count = 0
        for i, v in tk.items():
            for c in v:
                if color_compare(c, color):
                    map.data.vertices[i].select = True
                    select_count += 1
                    break

        if select_count > 0:
            bpy.ops.object.mode_set(mode = 'EDIT')
            objects_before_separate = set(bpy.data.objects.keys())
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')
            objects_after_separate = set(bpy.data.objects.keys())
            new_object = objects_after_separate.difference(objects_before_separate).pop()
            bpy.data.objects[new_object].ExportObject = True
            bpy.data.objects[new_object].name = map.name + '.' + sector

    map.select = True
    bpy.context.scene.objects.active = map
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    map.select = True
    bpy.context.scene.objects.active = map
    bpy.ops.object.delete()

    split_sectors = {k: v for k, v in bpy.data.objects.items() if v.name.startswith(bpy.context.scene.LevelName)}

    # UV Unwrap split sectors
    for sector in split_sectors:
        if len(bpy.data.objects[sector].data.vertices) == 0:
            continue

        bpy.data.objects[sector].select = True
        bpy.context.scene.objects.active = bpy.data.objects[sector]
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[sector].select = True
        bpy.context.scene.objects.active = bpy.data.objects[sector]
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.uv.cube_project(cube_size=0.5)
        
        for uv_face in  bpy.data.objects[sector].data.uv_textures.active.data:
            uv_face.image = bpy.data.images['UV_Grid']

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')


class BuildLevel(bpy.types.Operator):
    bl_idname = "scene.build_level"
    bl_label = "Build Level"

    def execute(self, context):
        scene = bpy.context.scene

        bpy.ops.object.select_all(action='DESELECT')

        # Delete old level
        bpy.ops.object.select_pattern(pattern=scene.LevelName + '*')
        bpy.ops.object.delete()

        bpy.ops.object.select_all(action='DESELECT')

        assign_brush_vertex_colors()

        sector_brushes = []
        for object in scene.objects:
            if object.BrushType == 'Sector':
                sector_brushes.append(object)

        if len(sector_brushes) == 0:
            return {"FINISHED"}

        if bpy.data.meshes.find(scene.LevelName) != -1:
            bpy.data.meshes.remove(bpy.data.meshes[scene.LevelName])
        map = bpy.data.objects.new(scene.LevelName, sector_brushes[0].data)
        scene.objects.link(map)
        map.location = sector_brushes[0].location
        map.scale = sector_brushes[0].scale
        map.rotation_euler = sector_brushes[0].rotation_euler
        map = scene.objects[scene.LevelName]
        map.select = True
        scene.objects.active = map
        bpy.ops.object.make_single_user(object=True, obdata=True)
        sector_brushes.remove(sector_brushes[0])
        
        for brush in sector_brushes:
            # Add sector's materials to map
            for material_slot in brush.material_slots:
                if map.material_slots.find(material_slot.material.name) == -1:
                    bpy.ops.object.material_slot_add()
                    map.material_slots[''].material = bpy.data.materials[material_slot.material.name]

            bool_mod = map.modifiers.new(name=brush.name, type="BOOLEAN")
            bool_mod.object = brush
            bool_mod.operation = "UNION"
            bool_mod.solver = "CARVE"
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=brush.name)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode="OBJECT")

        map.ExportObject = True

        separate_sectors()

        return {"FINISHED"}

class DeleteLevel(bpy.types.Operator):
    bl_idname = "scene.delete_level"
    bl_label = "Delete Level"

    def execute(self, context):
        scene = bpy.context.scene

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=scene.LevelName + '*')
        bpy.ops.object.delete()

        return {"FINISHED"}

class ExportLevel(bpy.types.Operator):
    bl_idname = "scene.export_level"
    bl_label = "Build Level"

    def execute(self, context):
        scene = context.scene

        map_pieces = {k: v for k, v in bpy.data.objects.items() if k.startswith(scene.LevelName)}

        for obj in bpy.context.scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            if obj.ObjectType != None and obj.ObjectType == 'Prefab':
                obj.select = True

                if obj.vertex_groups.find('Origin') != -1:
                    mesh = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
                    origin_group_index = obj.vertex_groups['Origin'].index
                    for v in mesh.vertices:
                        for g in v.groups:
                            if g.group == origin_group_index:
                                origin_vertex = mesh.vertices[v.index].co

                                adjacent_vertices = [e[0] for e in mesh.edge_keys if e[1] == v.index] + [e[1] for e in mesh.edge_keys if e[0] == v.index]
                                forward_vertex = None
                                left_vertex = None
                                up_vertex = None

                                forward_group_index = obj.vertex_groups['X'].index
                                left_group_index = obj.vertex_groups['Y'].index
                                up_group_index = obj.vertex_groups['Z'].index

                                for a in adjacent_vertices:
                                    for a_group in mesh.vertices[a].groups:
                                        if a_group.group == forward_group_index:
                                            forward_vertex = mesh.vertices[a].co - origin_vertex
                                        elif a_group.group == left_group_index:
                                            left_vertex = mesh.vertices[a].co - origin_vertex
                                        elif a_group.group == up_group_index:
                                            up_vertex = mesh.vertices[a].co - origin_vertex

                                x_vec = Vector((1.0, 0.0, 0.0))
                                y_vec = Vector((0.0, -1.0, 0.0))
                                z_vec = Vector((0.0, 0.0, 1.0))

                                rot_matrix = Matrix.Identity(3)
                                rot_matrix[0][0] = forward_vertex.dot(x_vec)
                                rot_matrix[0][1] = forward_vertex.dot(y_vec)
                                rot_matrix[0][2] = forward_vertex.dot(z_vec)
                                rot_matrix[1][0] = left_vertex.dot(x_vec)
                                rot_matrix[1][1] = left_vertex.dot(y_vec)
                                rot_matrix[1][2] = left_vertex.dot(z_vec)
                                rot_matrix[2][0] = up_vertex.dot(x_vec)
                                rot_matrix[2][1] = up_vertex.dot(y_vec)
                                rot_matrix[2][2] = up_vertex.dot(z_vec)

                                bpy.ops.object.select_all(action='DESELECT')
                                obj.select = True
                                bpy.context.scene.objects.active = obj
                                bpy.ops.object.duplicate_move()
                                bpy.context.active_object.modifiers.clear()
                                bpy.context.active_object.location = v.co + obj.location
                                bpy.context.active_object.rotation_euler = rot_matrix.to_euler('XYZ')
                                
                                bpy.context.active_object.data = bpy.data.meshes['Cube']
                                bpy.context.active_object.ExportObject = True
                                

                else:
                    bpy.ops.object.duplicate_move()
                    for duplicated_object in bpy.context.selected_objects:
                        duplicated_object.data = bpy.data.meshes['Cube']


        bpy.ops.object.select_pattern(pattern="*")
        for obj in bpy.context.selected_objects:
            if obj.ExportObject == False or (obj.BrushType != 'None' and obj.BrushType != 'Mesh'):
                bpy.data.objects[obj.name].select = False
        
        bpy.ops.export_scene.fbx(
            filepath=bpy.path.abspath(scene.LevelExportPath) + scene.LevelName + ".fbx",
            axis_forward="Z",
            axis_up="Y",
            bake_space_transform=True,
            use_selection=1,
            use_custom_props=True
        )

        bpy.ops.object.select_all(action='DESELECT')

        #Delete duplicated prefabs
        for obj in bpy.context.scene.objects:
            if obj.ObjectType == 'Prefab' and obj.ExportObject == True:
                obj.select = True
                bpy.ops.object.delete()
        
        return {"FINISHED"}

class Level(bpy.types.Panel):
    bl_label = 'Level'
    bl_idname = 'ui.level'
    bl_category = 'Level Editor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        
        build_col = layout.column(align=True)
        build_col.prop(scene, "LevelName", text="Level Name")
        build_col.operator("scene.build_level", icon="MOD_BUILD", text="Build Level")
        build_col.operator("scene.delete_level", icon="CANCEL", text="Delete Level")

        layout.label(text="Export Path", icon="FILE_FOLDER")
        export_col = layout.column(align=True)
        export_col.prop(scene, "LevelExportPath", text="")
        export_col.operator("scene.export_level", icon="LIBRARY_DATA_DIRECT", text="Export Level")


    def register():
        bpy.utils.register_class(BuildLevel)
        bpy.utils.register_class(DeleteLevel)
        bpy.utils.register_class(ExportLevel)

        bpy.types.Scene.LevelName = bpy.props.StringProperty(
            name="Level Name",
            description="The name of the scene's level",
            default="Level"
        )

        bpy.types.Scene.LevelExportPath = bpy.props.StringProperty(
            name="Level Export Path",
            description="",
            default="",
            subtype="DIR_PATH"
        )

    def unregister():
        bpy.utils.unregister_class(BuildLevel)
        bpy.utils.unregister_class(DeleteLevel)
        bpy.utils.unregister_class(ExportLevel)
        del sys.modules['LevelEditor.level']
