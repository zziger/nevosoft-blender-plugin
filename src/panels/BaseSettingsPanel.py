import bpy

class BaseSettingsPanel:
    bl_space_type = 'FILE_BROWSER'
    bl_idname = 'FILE_PT_nevosoft_base_settings'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Settings"
    bl_parent_id = "FILE_PT_operator"

    operator_id = None

    @classmethod
    def match_operator(cls, operator):
        if cls.operator_id is None:
            return False
        return operator.bl_idname == cls.operator_id

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return cls.match_operator(operator)
    
    def draw_settings(self, context, layout, operator):
        ...

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        self.draw_settings(context, layout, operator)
