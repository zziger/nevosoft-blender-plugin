from pathlib import Path
import traceback

import bpy
import bpy_extras
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG
from mathutils import Vector, Matrix, Quaternion, Euler
from ..settings import get_preferences
from .ExportSkeletonOperator import ExportSkeletonOperator

from ..utils import find_last
from ..helpers import OperatorBase, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class FixBoneIDsOperator(bpy.types.Operator, OperatorBase):
    """Adds missing bone IDs to the armature. Enforces root bone ID to be 0"""

    bl_idname = "nevosoft.fix_bone_ids"
    bl_label = "Fix bone IDs"

    confirmed: bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def draw(self, context):
        if not self.confirmed:
            layout = self.layout
            layout.label(text="This will change bone IDs of the armature")
            layout.label(text="Animations that were exported with old IDs might behave incorrectly")
            layout.label(text="Proceed?")
    
    def invoke(self, context, event):
        if not self.confirmed:
            return context.window_manager.invoke_props_dialog(self, width=600)
        
        return self.execute(context)
        
    def execute(self, context):
        if not self.confirmed:
            bpy.ops.nevosoft.fix_bone_ids('INVOKE_DEFAULT', confirmed=True)
            return {'FINISHED'}
        
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()

                if obj is None:
                    raise Exception("Failed to find an armature to fix bone IDs. Select armature in your 3D viewport and make sure it has a mesh child")
                
                bpy.ops.object.mode_set(mode='EDIT')
                
                root_bones = list(filter(lambda e: e.parent == None, obj.data.bones))
                if len(root_bones) > 1:
                    raise Exception("Multiple root bones found! Please ensure that your armature has only one root bone with ID 0")
                
                used = list()

                for bone in obj.data.edit_bones:
                    if bone.tag != None:
                        used.append(bone.tag)

                found = list()

                for bone in obj.data.edit_bones:
                    if bone.parent == None:
                        bone.tag = 0
                        used.append(0)
                    elif bone.tag == None or bone.tag < 0 or bone.tag in found:
                        bone.tag = 0
                        while bone.tag in used:
                            bone.tag += 1
                        used.append(bone.tag)
                    found.append(bone.tag) 

                # TODO: fill ID gaps
            
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            
            return {'FINISHED'}
        