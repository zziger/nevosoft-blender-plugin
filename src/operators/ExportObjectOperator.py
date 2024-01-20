import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..settings.BakeSettings import BakeSettings
from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile
from ..logger import operator_logger

class ExportObjectOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper, BakeSettings):
    """Export Nevosoft Object file from current scene"""

    bl_idname = "nevosoft.export_object"
    bl_label = "Nevosoft Object (.cgo)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".cgo"

    filter_glob: bpy.props.StringProperty(
        default='*.cgo',
        options={'HIDDEN'}
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

                objects = bpy.context.selected_objects if self.only_selected else bpy.context.scene.objects
                CgoFile.write(self.filepath, objects, self)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        operator = context.space_data.active_operator
        layout.prop(operator, 'only_selected')
