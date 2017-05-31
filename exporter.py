import bpy

class Exporter(bpy.types.Panel):
    bl_label = 'Exporter'
    bl_idname = 'ui.exporter'
    bl_category = 'Level Editor'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Test", icon="OBJECT_DATA")
        
        scene = bpy.context.scene


    def register():
    	bpy.types.Scene.LevelName = bpy.props.StringProperty(
    		name="Level Name",
    		description="The name of the scene's level",
    		default="Level"
		)

    def unregister():