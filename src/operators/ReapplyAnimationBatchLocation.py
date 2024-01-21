from pathlib import Path
import traceback

import bpy
import bpy_extras
from ..settings.AnimationSettings import AnimationSettings
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG
from mathutils import Vector, Matrix, Quaternion, Euler
from ..preferences import get_preferences
from .ExportSkeletonOperator import ExportSkeletonOperator

from ..utils import find_last
from ..helpers import OperatorBase, get_bone_properties, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class ReapplyAnimationBatchLocationOperator(bpy.types.Operator, OperatorBase):
    """Reapplies previously imported animation batch location animation"""

    bl_idname = "nevosoft.reapply_animation_batch_location"
    bl_label = "Reapply animation batch location"

    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None and AnmFile.hasBatch()
    
    def invoke(self, context, event):
        return self.execute(context)
        
    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()

                if obj is None:
                    raise Exception("Failed to find an armature to reapply animation location. Select armature in your 3D viewport and make sure it has a mesh child")
                
                if not AnmFile.hasBatch():
                    raise Exception("Batch animation data is missing. Import animation batch first")
                
                settings = AnimationSettings()
                settings.bone_rotations = False

                AnmFile.reapply_batch(obj, settings)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            
            return {'FINISHED'}