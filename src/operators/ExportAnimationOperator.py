import traceback

import bpy
import bpy_extras
from ..logger import operator_logger
from .ExportSkeletonOperator import ExportSkeletonOperator

from ..helpers import OperatorBase
from ..structures.AnmFile import AnmFile


class ExportAnimationOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    """Export Nevosoft Animation file from selected armature.
Armature must have one mesh child, animation data includes bone rotations and armature object location"""

    bl_idname = "nevosoft.export_animation"
    bl_label = "Nevosoft Animation (.anm)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".anm"
    
    @classmethod
    def poll(cls, context):
        obj = ExportSkeletonOperator.find_armature()
        return obj is not None and obj.animation_data is not None and obj.animation_data.action is not None

    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()
                if obj is None:
                    raise Exception("Failed to find an armature to export animation from. Select armature in your 3D viewport and make sure it has a mesh child")
                
                if obj.animation_data is None or obj.animation_data.action is None:
                    raise Exception("Failed to find an animation to export. Make sure selected armature contains an animation")

                anm = AnmFile.fromObject(obj)
                anm.write(self.filepath)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}
        