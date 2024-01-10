import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile


class ExportMeshOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_mesh"
    bl_label = "Nevosoft Mesh (.msh)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".msh"

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
        try:
            obj = ExportMeshOperator.find_mesh()
            if obj is None:
                raise Exception("Failed to find a mesh to export. Select a mesh in your 3D viewport")

            MshFile.write(obj, self.filepath)
            self.message(f"Exported mesh successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)

        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ExportMeshOperator)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportMeshOperator)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportMeshOperator.bl_idname, text=ExportMeshOperator.bl_label, icon="MESH_DATA")
