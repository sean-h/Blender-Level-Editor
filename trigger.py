import bpy

class TargetList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

    def invoke(self, context, event):
        pass

class TriggerTargetPropertyGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(
            name="name",
            description="Target Name",
            default=""
        )

class TargetList_actions(bpy.types.Operator):
    bl_idname = "object.target_list_action"
    bl_label = "Target List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    def invoke(self, context, event):
        current_index = context.active_object.SelectedTargetIndex

        try:
            item = context.active_object.TargetsList[current_index]
        except IndexError:
            pass

        else:
            if self.action == 'DOWN' and current_index < len(context.active_object.TargetsList) - 1:
                item_next = context.active_object.TargetsList[current_index+1].name
                context.active_object.SelectedTargetIndex += 1

            elif self.action == 'UP' and current_index >= 1:
                item_next = context.active_object.TargetsList[current_index-1].name
                context.active_object.SelectedTargetIndex -= 1

            elif self.action == 'REMOVE':
                if context.active_object.SelectedTargetIndex > 0:
                    context.active_object.SelectedTargetIndex -= 1
                context.active_object.TargetsList.remove(current_index)
                Trigger.UpdateTriggerTargets(context.active_object)

            elif self.action == 'ADD':
                pass
        
        return {"FINISHED"}

class Trigger():
    def CreateTriggerMaterial():
        mat = bpy.data.materials.get("Trigger")
        if mat == None:
            bpy.data.materials.new("Trigger")
            mat = bpy.data.materials.get("Trigger")
            mat.diffuse_color = [0.0, 0.8, 0.0]
            mat.use_shadeless = True
            mat.use_transparency = True
            mat.alpha = 0.5

    def AddToTargets(self, context):
        if self.TriggerTarget != "":
            list_already_contains_target = False

            for target in self.TargetsList:
                if target.name == self.TriggerTarget:
                    list_already_contains_target = True
                    break

            if list_already_contains_target == False:
                target = self.TargetsList.add()
                target.name = self.TriggerTarget
                Trigger.UpdateTriggerTargets(self)
            self.TriggerTarget = ""

    def UpdateTriggerTargets(object):
        object.TriggerTargets = ""
        for target in object.TargetsList:
            if len(object.TriggerTargets) > 0:
                object.TriggerTargets = object.TriggerTargets + ";" + target.name
            else:
                object.TriggerTargets = target.name


    def set_object_as_trigger(object):
        Trigger.CreateTriggerMaterial()
        mat = bpy.data.materials.get("Trigger")
        object.show_transparent = True
        object.show_wire = True
        if object.data.materials:
            object.data.materials[0] = mat
        else:
            object.data.materials.append(mat)

    def register():
        bpy.types.Object.TriggerTarget = bpy.props.StringProperty(
            name="Target",
            description="Target Object",
            default="",
            update = Trigger.AddToTargets
        )

        bpy.types.Object.TriggerTargets = bpy.props.StringProperty(
            name="Targets",
            description="Target Object",
            default=""
        )

        bpy.utils.register_class(TargetList)
        bpy.utils.register_class(TriggerTargetPropertyGroup)
        bpy.utils.register_class(TargetList_actions)

        bpy.types.Object.TargetsList = bpy.props.CollectionProperty(type=TriggerTargetPropertyGroup)
        bpy.types.Object.SelectedTargetIndex = bpy.props.IntProperty(
            name="Selected Target Index",
            default = 0,
            step=1
        )

    def unregister():
        bpy.utils.unregister_class(TargetList)
        bpy.utils.unregister_class(TriggerTargetPropertyGroup)
        bpy.utils.unregister_class(TargetList_actions)