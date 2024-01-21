from pathlib import Path
import traceback

import bpy
import bpy_extras
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG
from mathutils import Vector, Matrix, Quaternion, Euler
from ..preferences import get_preferences
from .ExportSkeletonOperator import ExportSkeletonOperator

from ..logger import logger
from ..utils import find_last
from ..helpers import OperatorBase, find_bone_by_tag, get_bone_properties, get_bone_tag, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class FixBoneIDsOperator(bpy.types.Operator, OperatorBase):
    """Places skeleton on ground properly for each animation frame"""

    bl_idname = "nevosoft.place_skeleton_on_ground"
    bl_label = "Place skeleton on ground"

    confirmed: bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def draw(self, context):
        if not self.confirmed:
            layout = self.layout
            layout.label(text="This action will change every animation frame")
            layout.label(text="Proceed?")
    
    def invoke(self, context, event):
        armature = ExportSkeletonOperator.find_armature()
        if not self.confirmed and armature.animation_data is not None and armature.animation_data.action is not None:
            return context.window_manager.invoke_props_dialog(self, width=600)
        
        return self.execute(context)
    
    def __place_on_ground(self, obj: bpy.types.Object):
        lowest_bone = get_bone_tag(min(obj.data.bones, key=lambda e: e.head_local.z))
        offset = Vector(obj.matrix_world @ obj.pose.bones[find_bone_by_tag(obj.data.bones, lowest_bone).name].head)
        obj.location.z -= offset.z
        
    def execute(self, context):
        if not self.confirmed:
            bpy.ops.nevosoft.place_skeleton_on_ground('INVOKE_DEFAULT', confirmed=True)
            return {'FINISHED'}
        
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()

                if obj is None:
                    raise Exception("Failed to find an armature to place on ground. Select armature in your 3D viewport and make sure it has a mesh child")
                
                if obj.animation_data is not None and obj.animation_data.action is not None:
                    curr_frame = bpy.context.scene.frame_current
                    start_frame = bpy.context.scene.frame_start
                    end_frame = bpy.context.scene.frame_end
                    
                    for f in range(start_frame, end_frame + 1):
                        bpy.context.scene.frame_set(f)
                        frame_id = f - start_frame
                        self.__place_on_ground(obj)
                        obj.keyframe_insert(data_path="location", frame=f, index=2) # Z only


                    bpy.context.scene.frame_set(curr_frame)
                    pass
                
                self.__place_on_ground(obj)

            except Exception as e:
                self.error(str(e), logToConsole=False)
                traceback.print_exception(e)
            
            return {'FINISHED'}
        