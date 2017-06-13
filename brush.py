import bpy
import sys

def change_brush_type(self, context):
    if self.BrushType == "None" or self.BrushType == "Mesh":
        self.draw_type = 'TEXTURED'
        self.ExportObject = True
        self.ColliderEnabled = True
    elif self.BrushType == 'Clip':
        self.draw_type = 'TEXTURED'
        self.show_transparent = True
        self.ExportObject = True
        self.ColliderEnabled = True
        mat = bpy.data.materials.get("Clip")
        if mat == None:
            bpy.data.materials.new("Clip")
            mat = bpy.data.materials.get("Clip")
            mat.diffuse_color = [0.8, 0.364, 0.0]
            mat.use_shadeless = True
            mat.use_transparency = True
            mat.alpha = 0.5
            mat = bpy.data.materials.get("Clip")
        if self.data.materials:
            self.data.materials[0] = mat
        else:
            self.data.materials.append(mat)
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
                ("Clip", "Clip", ""),
                ("None", "None", "")
            ],
            name="Brush Type",
            description="Brush type of the selected object",
            default="None",
            update=change_brush_type
        )

        bpy.types.Object.BrushBuildOrder = bpy.props.IntProperty(
            name="Brush Build Order",
            description="Order to add brush to map when building level",
            default=10
        )

        bpy.types.Object.BrushPhysicsMaterial = bpy.props.StringProperty(
            name="Brush Physics Material",
            description="The physics material to set on the brush's collider",
            default=""
        )

    def unregister():
        del sys.modules['LevelEditor.brush']
