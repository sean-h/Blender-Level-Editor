import bpy
import json
import os

class ImportMaterials(bpy.types.Operator):
    bl_idname = "scene.import_materials"
    bl_label = "Import Materials"

    def execute(self, context):
        material_file = open('F:/Unity Projects/Materials/MaterialList.json', 'r')
        data = json.load(material_file)

        for material in data['MaterialNames']:
            if material['MaterialName'] not in bpy.data.materials.keys():
                bpy.data.materials.new(material['MaterialName'])
                
            if len(bpy.data.materials[material['MaterialName']].texture_slots.keys()) == 0:
                bpy.data.materials[material['MaterialName']].texture_slots.add()
            
            try:
                image = bpy.data.images.load(material['TexturePath'], check_existing=True)
                image.reload()
            except:
                print('Could not load image: ' + material['TexturePath'])
            
            if material['MaterialName'] not in bpy.data.textures.keys():
                texture = bpy.data.textures.new(material['MaterialName'], 'IMAGE')
                
            image_dir, image_name = os.path.split(material['TexturePath'])
            texture = bpy.data.textures[material['MaterialName']]
            try:
                texture.image = bpy.data.images[image_name]
                texture_slot = bpy.data.materials[material['MaterialName']].texture_slots.keys()[0]
                slot = bpy.data.materials[material['MaterialName']].texture_slots[texture_slot]
                slot.texture = bpy.data.textures[material['MaterialName']]
            except:
                print('Could not load image: ' + material['TexturePath'])

        return {'FINISHED'}

class SetMaterial(bpy.types.Operator):
    bl_idname = "scene.set_material"
    bl_label = "Set Material"

    def execute(self, context):
        selected_material = bpy.context.scene.material_selector
        obj = bpy.context.active_object

        material_exists = False
        for material in obj.material_slots:
            if material == selected_material:
                material_exists = True
                break

        if material_exists == False:
            bpy.ops.object.material_slot_add()
            obj.material_slots[''].material = bpy.data.materials[selected_material]

        for i, material in enumerate(obj.material_slots):
            if material == selected_material:
                obj.active_material_index = i
                break

        bpy.ops.object.material_slot_assign()

        return {'FINISHED'}

class StartEditSectorMaterial(bpy.types.Operator):
    bl_idname = "scene.start_edit_sector_material"
    bl_label = "Start Edit Sector Material"

    def execute(self, context):
        sector = bpy.context.active_object

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        sector.draw_type = 'TEXTURED'

        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.uv.cube_project(cube_size=0.5)
        bpy.ops.mesh.select_all(action = 'DESELECT')

        return {'FINISHED'}

class EndEditSectorMaterial(bpy.types.Operator):
    bl_idname = "scene.end_edit_sector_material"
    bl_label = "End Edit Sector Material"

    def execute(self, context):
        sector = bpy.context.active_object

        bpy.ops.object.mode_set(mode = 'OBJECT')
        sector.draw_type = 'WIRE'

        return {'FINISHED'}


class MaterialPainter(bpy.types.Panel):
    bl_label = 'Material Painter'
    bl_idname = 'ui.material_painter'
    bl_category = 'Level Editor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        
        build_col = layout.column(align=True)
        build_col.operator("scene.import_materials", icon="ASSET_MANAGER", text="Load Materials")

        set_col = layout.column(align=True)
        set_col.operator("scene.start_edit_sector_material", icon="TRIA_RIGHT", text="Start Edit Sector Material")
        set_col.operator("scene.end_edit_sector_material", icon="X", text="End Edit Sector Material")
        set_col.template_icon_view(context.scene, "material_selector")
        set_col.operator("scene.set_material", icon="MATERIAL", text="Set Material")

    def register():
        bpy.utils.register_class(ImportMaterials)
        bpy.utils.register_class(SetMaterial)
        bpy.utils.register_class(StartEditSectorMaterial)
        bpy.utils.register_class(EndEditSectorMaterial)

        material_previews = bpy.utils.previews.new()
        material_previews.images_location = 'F:/Unity Projects/Materials/'

        material_items = []


        material_file = open('F:/Unity Projects/Materials/MaterialList.json', 'r')
        data = json.load(material_file)

        for i, material in enumerate(data['MaterialNames']):
            thumb = material_previews.load(material['TexturePath'], material['TexturePath'], 'IMAGE')
            material_items.append((material['MaterialName'], material['MaterialName'], "", thumb.icon_id, i))

        bpy.types.Scene.material_selector = bpy.props.EnumProperty(
            items=material_items
        )

    def unregister():
        bpy.utils.unregister_class(ImportMaterials)
        bpy.utils.unregister_class(SetMaterial)
        bpy.utils.unregister_class(StartEditSectorMaterial)
        bpy.utils.unregister_class(EndEditSectorMaterial)
        del sys.modules['LevelEditor.materialpainter']
