import bpy

class AnimationSettingsPanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_idname = 'FILE_PT_nevosoft_animation_settings'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Animation settings"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return operator.bl_idname == "NEVOSOFT_OT_import_animation" or operator.bl_idname == "NEVOSOFT_OT_export_animation"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        layout.prop(operator, 'bone_rotations')

        col = layout.column()
        split = col.split()
        sub = split.column()
        row = sub.row()
        row.label(text="Axis")

        subrow = row.row(align=True)
        subrow.prop(operator, 'location_x', text="X", toggle=True)
        subrow.prop(operator, 'location_y', text="Y", toggle=True)
        subrow.prop(operator, 'location_z', text="Z", toggle=True)
