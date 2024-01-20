import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..logger import operator_logger


class ExportMeshOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    """Export Nevosoft Mesh file from selected mesh"""

    bl_idname = "nevosoft.export_mesh"
    bl_label = "Nevosoft Mesh (.msh)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".msh"

    filter_glob: bpy.props.StringProperty(
        default='*.msh',
        options={'HIDDEN'}
    )

    @staticmethod
    def find_mesh():
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                return obj
            
        return None
    
    @classmethod
    def poll(cls, context):
        return ExportMeshOperator.find_mesh() is not None
    
    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportMeshOperator.find_mesh()
                if obj is None:
                    raise Exception("Failed to find a mesh to export. Select a mesh in your 3D viewport")

                MshFile.write(obj, self.filepath)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

        return {'FINISHED'}
    