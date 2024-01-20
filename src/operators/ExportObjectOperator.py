import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile
from ..logger import operator_logger

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

    only_selected: BoolProperty(
        name="Only selected",
        description="Include selected objects only (instead of all objects in the scene)",
        default=False,
    )
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None and len(bpy.context.scene.objects) > 0 or len(bpy.context.selected_objects) > 0

    def execute(self, context):
        with operator_logger(self):
            try:
                if bpy.context.scene is None:
                    raise Exception("Failed to find a scene to export. Are you running headless?")
                
                if len(bpy.context.scene.objects) == 0:
                    raise Exception("No objects found in the scene")

                CgoFile.write(self.filepath, bpy.context.selected_objects if self.only_selected else bpy.context.scene.objects, bake=self.bake_materials)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

        return {'FINISHED'}

    def draw(self, context):
        pass


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
        layout.prop(operator, 'only_selected')