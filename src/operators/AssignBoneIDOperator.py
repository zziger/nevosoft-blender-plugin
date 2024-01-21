from pathlib import Path
import traceback

import bpy
import bpy_extras
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG
from mathutils import Vector, Matrix, Quaternion, Euler
from ..preferences import get_preferences
from .ExportSkeletonOperator import ExportSkeletonOperator

from ..utils import find_last
from ..helpers import OperatorBase, find_bone_by_tag, get_bone_properties, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class FixBoneIDsOperator(bpy.types.Operator, OperatorBase):
    """Assigns selected bone a new bone ID"""

    bl_idname = "nevosoft.assign_bone_id"
    bl_label = "Assign new bone ID"

    confirmed: bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def invoke(self, context, event):
        return self.execute(context)
        
    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()

                if obj is None:
                    raise Exception("Failed to find an armature to assign bone ID. Select armature in your 3D viewport and make sure it has a mesh child")
                
                bone = context.active_bone
                if bone is None:
                    raise Exception("Failed to find an active bone. Select a bone in your 3D viewport")
                
                properties = get_bone_properties(bone)
                if properties.tag >= 0:
                    raise Exception("Bone already has an ID assigned")
                
                for i in range(len(obj.data.bones)):
                    if find_bone_by_tag(obj.data.bones, i) is None:
                        properties.tag = i
                        break

            except Exception as e:
                self.error(str(e), logToConsole=False)
                traceback.print_exception(e)
            
            return {'FINISHED'}
        