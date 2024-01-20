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


class RetargetModelOperator(bpy.types.Operator, OperatorBase):
    """Change model rest pose to the current pose and retarget current animation"""

    bl_idname = "nevosoft.retarget_model"
    bl_label = "Retarget model"

    confirmed: bpy.props.BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def draw(self, context):
        if not self.confirmed:
            layout = self.layout
            layout.label(text="This will change model's rest pose to the current pose and retarget current animation")
            layout.label(text="All animations that were not retargeted will not match this model anymore")
            layout.label(text="Proceed?")
    
    def invoke(self, context, event):
        if not self.confirmed:
            return context.window_manager.invoke_props_dialog(self, width=600)
        
        return self.execute(context)
        
    def execute(self, context):
        if not self.confirmed:
            bpy.ops.nevosoft.retarget_model('INVOKE_DEFAULT', confirmed=True)
            return {'FINISHED'}
        
        with operator_logger(self):
            obj = ExportSkeletonOperator.find_armature()

            if obj is None:
                raise Exception("Failed to find an armature to retarget animations. Select armature in your 3D viewport and make sure it has a mesh child")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            select(obj)
            
            anm = None
            mesh = obj.children[0]

            if mesh is None:
                raise Exception("Failed to find armature mesh")

            if obj.animation_data != None:
                anm = AnmFile.fromObject(obj, align_bones=False)
                anm.pre_transpose(obj.pose)

            set_active(mesh)
            bpy.ops.object.modifier_copy(modifier=find_last(mesh.modifiers, lambda e: e.type == 'ARMATURE').name)
            bpy.ops.object.modifier_apply(modifier=find_last(mesh.modifiers, lambda e: e.type == 'ARMATURE').name)

            set_active(obj)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.armature_apply()
            bpy.ops.object.mode_set(mode='OBJECT')

            if anm != None:
                anm.create(obj)
                anm = AnmFile.fromObject(obj)

                bpy.ops.object.mode_set(mode='EDIT')
                for bone in obj.data.edit_bones:
                    bone.tail = bone.head + (BONE_DIRECTION_DEBUG if get_preferences().debug else BONE_DIRECTION)
                    bone.roll = 0
                bpy.ops.object.mode_set(mode='OBJECT')

                anm.create(obj)
            
            return {'FINISHED'}
