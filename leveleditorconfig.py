import bpy
import os
import addon_utils
import json
import sys

def config_file_path():
    addon_directory = None
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == 'Level Editor':
            addon_directory = mod.__file__.replace('__init__.py', '')
            break

    return addon_directory + '\\config.json'

def create_config_file():
    if config_file_exists():
        return

     # Create config file
    file_data = {
        'material_list_path': '',
        'prefab_list_path': ''
    }

    with open(config_file_path(), 'w') as f:
        f.write(json.dumps(file_data))

def config_file_exists():
    return os.path.isfile(config_file_path())

def material_list_path():
    if not config_file_exists():
        create_config_file()

    config_file = open(config_file_path())

    return json.load(config_file)['material_list_path']

def prefab_list_path():
    if not config_file_exists():
        create_config_file()

    config_file = open(config_file_path())

    return json.load(config_file)['prefab_list_path']

def set_config_property(key, value):
    with open(config_file_path(), 'r+') as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()

class LevelEditorConfig(bpy.types.Panel):
    bl_label = 'Level Editor Config'
    bl_idname = 'ui.level_editor_config'
    bl_category = 'Level Editor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Material List Path", icon="FILE_FOLDER")
        col.prop(bpy.context.scene, 'MaterialListPath', text="")

        col = layout.column(align=True)
        col.label(text="Prefab List Path", icon="FILE_FOLDER")
        col.prop(bpy.context.scene, 'PrefabListPath', text="")

    def material_list_path_updated(self, context):
        set_config_property('material_list_path', self.MaterialListPath)

    def prefab_list_path_updated(self, context):
        set_config_property('prefab_list_path', self.PrefabListPath)

def register():
    bpy.utils.register_class(LevelEditorConfig)

    create_config_file()

    bpy.types.Scene.MaterialListPath = bpy.props.StringProperty(
        name="Material List Path",
        default=material_list_path(),
        update=LevelEditorConfig.material_list_path_updated,
        subtype="FILE_PATH"
    )

    bpy.types.Scene.PrefabListPath = bpy.props.StringProperty(
        name="Material List Path",
        default=prefab_list_path(),
        update=LevelEditorConfig.prefab_list_path_updated,
        subtype="FILE_PATH"
    )

def unregister():
    bpy.utils.unregister_class(LevelEditorConfig)
    del sys.modules['LevelEditor.leveleditorconfig']