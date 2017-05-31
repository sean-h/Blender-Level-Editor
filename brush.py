import bpy
import sys

def change_brush_type(self, context):
    if self.BrushType == "None" or self.BrushType == "Mesh":
        self.draw_type = 'TEXTURED'
        self.ExportObject = True
    else:
        self.draw_type = 'WIRE'
        self.ExportObject = False

class Brush:
    def register():
        bpy.types.Object.BrushType = bpy.props.EnumProperty(
            items=[
                ("Additive", "Additive", ""),
                ("Subtractive", "Subtractive", ""),
                ("Sector", "Sector", ""),
                ("Mesh", "Mesh", ""),
                ("None", "None", "")
            ],
            name="Brush Type",
            description="Brush type of the selected object",
            default="None",
            update=change_brush_type
        )

    def unregister():
        del sys.modules['LevelEditor.brush']
