import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile
from ..utils import clear_scene
from ..logger import operator_logger


class ImportObjectOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Import Nevosoft Object file into current scene"""

    bl_idname = "nevosoft.import_object"
    bl_label = "Nevosoft Object (.cgo)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.cgo',
        options={'HIDDEN'}
    )

    clear_scene: BoolProperty(
        name="Clear scene",
        description="Clear whole scene before importing",
        default=True,
    )

    def execute(self, context):
        with operator_logger(self):
            try:
                if self.clear_scene:
                    clear_scene()
                cgo = CgoFile.read(self.filepath)
                cgo.create()
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        operator = context.space_data.active_operator
        layout.prop(operator, 'clear_scene')