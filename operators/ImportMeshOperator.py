import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..logger import operator_logger


class ImportMeshOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Import Nevosoft Mesh file into current scene"""

    bl_idname = "nevosoft.import_mesh"
    bl_label = "Nevosoft Mesh (.msh)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.msh',
        options={'HIDDEN'}
    )

    def execute(self, context):
        with operator_logger(self):
            try:
                skl = MshFile.read(self.filepath)
                skl.create()
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportMeshOperator)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportMeshOperator)
