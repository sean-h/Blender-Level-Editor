import bpy
import sys
import pdb
import math
import bmesh
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

    StairBuildType = bpy.props.EnumProperty(
        items=(
            ("IndividualStairSize", "IndividualStairSize", "IndividualStairSize"),
            ("TotalSectionSize", "TotalSectionSize", "TotalSectionSize")
        ),
        default="IndividualStairSize"
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

    StairSectionHeight = bpy.props.FloatProperty(
        name="Stair Section Height",
        default = 2,
        step=1
    )

    StairSectionDepth = bpy.props.FloatProperty(
        name="Stair Section Depth",
        default = 2,
        step=1
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
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairSectionName = obj.StairSectionName
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepCount = obj.StairStepCount
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairSectionNextDirection = obj.StairSectionNextDirection
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepWidth = obj.StairStepWidth
        obj.StairSectionList[obj.SelectedStairSectionIndex].StairBuildType = obj.StairBuildType

        if obj.StairBuildType == 'IndividualStairSize':
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepHeight = obj.StairStepHeight
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepDepth = obj.StairStepDepth
        elif obj.StairBuildType == 'TotalSectionSize':
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairSectionHeight = obj.StairSectionHeight
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairSectionDepth = obj.StairSectionDepth
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepHeight = obj.StairSectionHeight / obj.StairStepCount
            obj.StairSectionList[obj.SelectedStairSectionIndex].StairStepDepth = obj.StairSectionDepth / obj.StairStepCount

        obj.UnappliedProperties = False
        bpy.ops.object.build_stairs(name=context.scene.LevelName + '.' + context.active_object.name)
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

        #Delete previous stairs
        if context.scene.objects.find(self.name) != -1:
            previous_obj = context.scene.objects[self.name]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=self.name + '*')
            bpy.ops.object.delete()

        step_build_point = obj.location
        build_direction = '+Y'
        sections = []
        for section in obj.StairSectionList:
            steps = []
            section_origin = step_build_point
            if section.StairStepCount == 1:
                step_build_point = step_build_point - Vector((0.0, 0.0, z))

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

            #Build clip brush
            section_height = section.StairStepHeight * section.StairStepCount
            if section.StairStepCount == 1:
                section_height = 0.0

            section_length = y * section.StairStepCount

            bpy.ops.object.add(location=obj.location, type='MESH')
            clip_object = context.active_object
            
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(clip_object.data)
            # Top vertices
            bm.verts.new(Vector((-x / 2.0, 0.0, 0.0)))
            bm.verts.new(Vector((x / 2.0, 0.0, 0.0)))
            bm.verts.new(Vector((x / 2.0, section_length, section_height)))
            bm.verts.new(Vector((-x / 2.0, section_length, section_height)))

            # Bottom vertices
            bm.verts.new(Vector((-x / 2.0, section_length, section_height - section.StairStepHeight)))
            bm.verts.new(Vector((x / 2.0, section_length, section_height - section.StairStepHeight)))
            bm.verts.new(Vector((x / 2.0, 0.0, -section.StairStepHeight)))
            bm.verts.new(Vector((-x / 2.0, 0.0, -section.StairStepHeight)))

            bm.verts.ensure_lookup_table()
            bm.faces.new((bm.verts[i] for i in [0,1,2,3]))
            bm.faces.new((bm.verts[i] for i in [4,5,6,7]))
            bm.faces.new((bm.verts[i] for i in [3,4,7,0]))
            bm.faces.new((bm.verts[i] for i in [0,7,6,1]))
            bm.faces.new((bm.verts[i] for i in [1,6,5,2]))
            bm.faces.new((bm.verts[i] for i in [2,5,4,3]))

            bpy.ops.object.mode_set(mode='OBJECT')
            

            clip_object.ObjectType = 'Brush'
            clip_object.BrushType = 'Clip'
            clip_object.BrushPhysicsMaterial = 'Stairs'
            clip_object.name = self.name + '.' + section.StairSectionName + '.' + 'Clip'


            build_direction = section.StairSectionNextDirection
            
            if build_direction == '+X':
                step_build_point = step_build_point + Vector((x / 2.0, 0.0, 0.0))
            elif build_direction == '-X':
                step_build_point = step_build_point + Vector((-x / 2.0, 0.0, 0.0))
            elif build_direction == '+Y':
                step_build_point = step_build_point + Vector((0.0, y / 2.0, 0.0))
            elif build_direction == '-Y':
                step_build_point = step_build_point + Vector((0.0, -y / 2.0, 0.0))

        
        bpy.ops.object.select_all(action='DESELECT')
        for section in sections:
            section.select=True
            context.scene.objects.active = section

        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        context.active_object.name = self.name

        cursor_location = context.scene.cursor_location
        context.scene.cursor_location = obj.location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor_location = cursor_location

        context.active_object.rotation_euler = obj.rotation_euler
        # Rotate clip brushes
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=self.name + '.' + '*')
        for o in context.scene.objects:
            if o.select:
                o.rotation_euler = obj.rotation_euler

        bpy.ops.object.unwrap_object(target_name=context.active_object.name)
        bpy.ops.object.material_slot_add()
        context.active_object.material_slots[0].material = bpy.data.materials[obj.StairMaterial]
        context.active_object.ExportObject = True
        context.active_object.ColliderEnabled = False

        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj

        return {"FINISHED"}

class Stairs():

    def on_selected_stair_section_index_changed(self, context):
        self.StairSectionName = self.StairSectionList[self.SelectedStairSectionIndex].StairSectionName
        self.StairStepWidth = self.StairSectionList[self.SelectedStairSectionIndex].StairStepWidth
        self.StairStepCount = self.StairSectionList[self.SelectedStairSectionIndex].StairStepCount
        self.StairBuildType = self.StairSectionList[self.SelectedStairSectionIndex].StairBuildType
        self.StairStepHeight = self.StairSectionList[self.SelectedStairSectionIndex].StairStepHeight
        self.StairStepDepth = self.StairSectionList[self.SelectedStairSectionIndex].StairStepDepth
        self.StairSectionHeight = self.StairSectionList[self.SelectedStairSectionIndex].StairSectionHeight
        self.StairSectionDepth = self.StairSectionList[self.SelectedStairSectionIndex].StairSectionDepth
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

        bpy.types.Object.StairBuildType = bpy.props.EnumProperty(
            items=(
                ("IndividualStairSize", "IndividualStairSize", "IndividualStairSize"),
                ("TotalSectionSize", "TotalSectionSize", "TotalSectionSize")
            ),
            default="IndividualStairSize"
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

        bpy.types.Object.StairSectionHeight = bpy.props.FloatProperty(
            name="Stair Section Height",
            default = 2,
            step=1
        )

        bpy.types.Object.StairSectionDepth = bpy.props.FloatProperty(
            name="Stair Section Depth",
            default = 2,
            step=1
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

        bpy.types.Object.StairMaterial = bpy.props.StringProperty(
            name="Stair Material",
            description="Stair Material",
            default="Material"
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