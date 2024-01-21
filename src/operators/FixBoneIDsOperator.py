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
from ..logger import operator_logger, logger


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
                
                used_ids = set()

                for bone in obj.data.edit_bones:
                    properties = get_bone_properties(bone)

                    if properties.tag >= 0:
                        used_ids.add(properties.tag)

                found_ids = list()

                for bone in obj.data.edit_bones:
                    properties = get_bone_properties(bone)

                    # Enforce ID 0 for root bone
                    if bone.parent == None:
                        properties.tag = 0
                        used_ids.add(0)
                    # Fill missing IDs
                    elif properties.tag < 0 or properties.tag in found_ids:
                        properties.tag = 0
                        while properties.tag in used_ids:
                            properties.tag += 1
                        used_ids.add(properties.tag)

                    found_ids.append(properties.tag) 

                # Fill ID gaps
                for i in range(len(obj.data.edit_bones)):
                    if i not in found_ids:
                        source = found_ids.pop(found_ids.index(max(found_ids)))
                        logger.debug('Moving bone ID %s to %s', source, i)
                        get_bone_properties(find_bone_by_tag(obj.data.edit_bones, source)).tag = i
                        found_ids.append(i)

            
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            
            return {'FINISHED'}
        