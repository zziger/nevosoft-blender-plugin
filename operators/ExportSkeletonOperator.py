import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.SklFile import SklFile


class ExportSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_skeleton"
    bl_label = "Nevosoft Skeleton (.skl)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".skl"

    @staticmethod
    def find_armature():
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE' and len(obj.children) == 1 and obj.children[0].type == 'MESH':
                return obj
            
            if obj.type == 'MESH' and obj.parent is not None and len(obj.parent.children) == 1 and obj.parent.type == 'ARMATURE':
                return obj.parent
            
        return None
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None

    def execute(self, context):
        try:
            obj = ExportSkeletonOperator.find_armature()
            if obj is None:
                raise Exception("Failed to find an armature to export. Select armature in your 3D viewport and make sure it has a mesh child")

            SklFile.write(obj, self.filepath)
            self.message(f"Exported skeleton succesfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)

        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ExportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportSkeletonOperator.bl_idname, text=ExportSkeletonOperator.bl_label, icon="ARMATURE_DATA")
