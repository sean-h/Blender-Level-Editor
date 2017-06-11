import bpy
import sys
import pdb
import math
from mathutils import Vector

class StairSectionList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "StairSectionName", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

class StairSectionPropertyGroup(bpy.types.PropertyGroup):
    StairSectionName = bpy.props.StringProperty(
        name="Stair Section Name",
        description="Section Name",
        default="Section"
    )

    StairStepHeight = bpy.props.FloatProperty(
        name="Stair Step Height",
        default = 0.25,
        step=0.25
    )

    StairStepWidth = bpy.props.FloatProperty(
        name="Stair Step Height",
        default = 0.25,
        step=0.25
    )

    StairStepDepth = bpy.props.FloatProperty(
        name="Stair Step Depth",
        default = 0.3,
        step=1
    )

    StairStepCount = bpy.props.IntProperty(
        name="Stair Step Count",
        default = 5,
        step=5
    )

    StairSectionNextDirection = bpy.props.EnumProperty(
        items=(
            ('+X', "+X", ""),
            ('-X', "-X", ""),
            ('+Y', "+Y", ""),
            ('-Y', "-Y", ""),
        ),
        default="+Y"
    )

class StairSectionList_actions(bpy.types.Operator):
    bl_idname = "object.stair_section_list_action"
    bl_label = "Stair Section List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):
        current_index = context.active_object.SelectedStairSectionIndex

        try:
            item = context.active_object.StairSectionList[current_index]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and current_index < len(context.active_object.StairSectionList) - 1:
                item_next = context.active_object.StairSectionList[current_index+1].name
                context.active_object.SelectedStairSectionIndex += 1

            elif self.action == 'UP' and current_index >= 1:
                item_next = context.active_object.StairSectionList[current_index-1].name
                context.active_object.SelectedStairSectionIndex -= 1

            elif self.action == 'REMOVE':
                if context.active_object.SelectedStairSectionIndex > 0:
                    context.active_object.SelectedStairSectionIndex -= 1
                context.active_object.StairSectionList.remove(current_index)

            elif self.action == 'ADD':
                context.active_object.StairSectionList.add()
        
        return {"FINISHED"}

class ApplyStairSectionProperties(bpy.types.Operator):
    bl_idname = "object.apply_stair_section_properties"
    bl_label = "Apply Stair Section Properties"

    def invoke(self, context, event):
        obj = context.active_object
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepHeight = obj.StairStepHeight
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepWidth = obj.StairStepWidth
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepDepth = obj.StairStepDepth
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepCount = obj.StairStepCount
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairSectionNextDirection = obj.StairSectionNextDirection
        obj.UnappliedProperties = False
        return {"FINISHED"}

class BuildStairs(bpy.types.Operator):
    bl_idname = "object.build_stairs"
    bl_label = "Build Stairs"

    name = bpy.props.StringProperty(
        name="Name",
        description="Built stair object name",
        default="Stairs",
    )

    def execute(self, context):
        obj = context.active_object
        step_build_point = obj.location
        build_direction = '+Y'
        sections = []
        for section in obj.StairSectionList:
            steps = []
            section_origin = step_build_point

            x = section.StairStepWidth 
            y = section.StairStepDepth
            z = section.StairStepHeight

            if build_direction == '+X' or build_direction == '-X':
                x = section.StairStepDepth
                y = section.StairStepWidth 

            for i in range(0,section.StairStepCount):
                if build_direction == '+X':
                    bpy.ops.mesh.primitive_cube_add(location=step_build_point + Vector((x / 2.0, 0.0, z / 2.0)))
                elif build_direction == '-X':
                    bpy.ops.mesh.primitive_cube_add(location=step_build_point + Vector((-x / 2.0, 0.0, z / 2.0)))
                elif build_direction == '+Y':
                    bpy.ops.mesh.primitive_cube_add(location=step_build_point + Vector((0.0, y / 2.0, z / 2.0)))
                elif build_direction == '-Y':
                    bpy.ops.mesh.primitive_cube_add(location=step_build_point + Vector((0.0, -y / 2.0, z / 2.0)))
                context.active_object.scale=Vector((x / 2.0, y / 2.0, z / 2.0))
                steps.append(context.active_object)
                if build_direction == '+X':
                    step_build_point = step_build_point + Vector((x, 0.0, z))
                elif build_direction == '-X':
                    step_build_point = step_build_point + Vector((-x, 0.0, z))
                elif build_direction == '+Y':
                    step_build_point = step_build_point + Vector((0.0, y, z))
                elif build_direction == '-Y':
                    step_build_point = step_build_point + Vector((0.0, -y, z))

            for step in steps:
                step.select=True

            # Center back on step
            if build_direction == '+X':
                step_build_point = step_build_point - Vector((x / 2.0, 0.0, 0.0))
            elif build_direction == '-X':
                step_build_point = step_build_point - Vector((-x / 2.0, 0.0, 0.0))
            elif build_direction == '+Y':
                step_build_point = step_build_point - Vector((0.0, y / 2.0, 0.0))            
            elif build_direction == '-Y':
                step_build_point = step_build_point - Vector((0.0, -y / 2.0, 0.0))    

            # Join steps
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            cursor_location = context.scene.cursor_location
            context.scene.cursor_location = section_origin
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            sections.append(context.active_object)

            build_direction = section.StairSectionNextDirection
            
            if build_direction == '+X':
                step_build_point = step_build_point + Vector((x / 2.0, 0.0, 0.0))
            elif build_direction == '-X':
                step_build_point = step_build_point + Vector((-x / 2.0, 0.0, 0.0))
            elif build_direction == '+Y':
                step_build_point = step_build_point + Vector((0.0, y / 2.0, 0.0))
            elif build_direction == '-Y':
                step_build_point = step_build_point + Vector((0.0, -y / 2.0, 0.0))


        
        for section in sections:
            section.select=True

        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        context.active_object.name = self.name

        cursor_location = context.scene.cursor_location
        context.scene.cursor_location = obj.location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor_location = cursor_location

        context.active_object.rotation_euler = obj.rotation_euler   

        return {"FINISHED"}

class Stairs():

    def on_selected_stair_section_index_changed(self, context):
        self.StairSectionName = self.StairSectionList[self.SelectedStairSectionIndex].StairSectionName
        self.StairStepHeight = self.StairSectionList[self.SelectedStairSectionIndex].StairStepHeight
        self.StairStepWidth = self.StairSectionList[self.SelectedStairSectionIndex].StairStepWidth
        self.StairStepDepth = self.StairSectionList[self.SelectedStairSectionIndex].StairStepDepth
        self.StairStepCount = self.StairSectionList[self.SelectedStairSectionIndex].StairStepCount
        self.StairSectionNextDirection = self.StairSectionList[self.SelectedStairSectionIndex].StairSectionNextDirection

    def on_property_changed(self, context):
        self.UnappliedProperties = True

    def register():
        bpy.utils.register_class(StairSectionList)
        bpy.utils.register_class(StairSectionPropertyGroup)
        bpy.utils.register_class(StairSectionList_actions)
        bpy.utils.register_class(ApplyStairSectionProperties)
        bpy.utils.register_class(BuildStairs)

        bpy.types.Object.StairSectionList = bpy.props.CollectionProperty(type=StairSectionPropertyGroup)
        bpy.types.Object.SelectedStairSectionIndex = bpy.props.IntProperty(
            name="Selected Stair Section Index",
            default = 0,
            step=1,
            update=Stairs.on_selected_stair_section_index_changed
        )

        bpy.types.Object.StairSectionName = bpy.props.StringProperty(
            name="Stair Section Name",
            description="Section Name",
            default="Section",
            update=Stairs.on_property_changed
        )

        bpy.types.Object.StairStepHeight = bpy.props.FloatProperty(
            name="Stair Step Height",
            default = 0.25,
            step=1,
            update=Stairs.on_property_changed
        )

        bpy.types.Object.StairStepWidth = bpy.props.FloatProperty(
            name="Stair Step Width",
            default = 2.0,
            step=1,
            update=Stairs.on_property_changed
        )

        bpy.types.Object.StairStepDepth = bpy.props.FloatProperty(
            name="Stair Step Depth",
            default = 0.3,
            step=1,
            update=Stairs.on_property_changed
        )

        bpy.types.Object.StairStepCount = bpy.props.IntProperty(
            name="Stair Step Count",
            default = 5,
            step=5,
            update=Stairs.on_property_changed
        )

        bpy.types.Object.StairSectionNextDirection = bpy.props.EnumProperty(
            items=(
                ('+X', "+X", ""),
                ('-X', "-X", ""),
                ('+Y', "+Y", ""),
                ('-Y', "-Y", ""),
            ),
            default="+Y"
        )

        bpy.types.Object.UnappliedProperties = bpy.props.BoolProperty(
            name="UnappliedProperties",
            description="Properties have not been applied to selected section",
            default=False,
        )


    def unregister():
        bpy.utils.unregister_class(StairSectionList)
        bpy.utils.unregister_class(StairSectionPropertyGroup)
        bpy.utils.unregister_class(StairSectionList_actions)
        bpy.utils.unregister_class(ApplyStairSectionProperties)
        bpy.utils.unregister_class(BuildStairs)
        del sys.modules['LevelEditor.stairs']