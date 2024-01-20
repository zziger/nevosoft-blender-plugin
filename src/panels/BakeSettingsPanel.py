import bpy

class BakeSettingsPanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_idname = 'FILE_PT_nevosoft_bake_settings'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Material settings"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return operator.bl_idname == "NEVOSOFT_OT_export_character" or operator.bl_idname == "NEVOSOFT_OT_export_object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        layout.prop(operator, 'bake_materials')
