import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile

# TODO: allow to export selected meshes instead of the whole scene

class ExportObjectOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    """Export Nevosoft Object file from current scene"""

    bl_idname = "nevosoft.export_object"
    bl_label = "Nevosoft Object (.cgo)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".cgo"

    bake_materials: BoolProperty(
        name="Bake materials",
        description="Bake materials instead of searching for texture",
        default=False,
    )
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None and len(bpy.context.scene.objects) > 0

    def execute(self, context):
        try:
            if bpy.context.scene is None:
                raise Exception("Failed to find a scene to export. Are you running headless?")
            
            if len(bpy.context.scene.objects) == 0:
                raise Exception("No objects found in the scene")

            CgoFile.write(self.filepath, bpy.context.scene, self.bake_materials)
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)

        return {'FINISHED'}

    def draw(self, context):
        pass

    @staticmethod
    def load():
        bpy.utils.register_class(ExportObjectOperator)
        bpy.utils.register_class(CUSTOM_PT_object_export_settings)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportObjectOperator)
        bpy.utils.unregister_class(CUSTOM_PT_object_export_settings)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


class CUSTOM_PT_object_export_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Export settings"

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return operator.bl_idname == "NEVOSOFT_OT_export_object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        layout.prop(operator, 'bake_materials')


def menu_func_export(self, context):
    self.layout.operator(ExportObjectOperator.bl_idname, text=ExportObjectOperator.bl_label, icon="MESH_CUBE")