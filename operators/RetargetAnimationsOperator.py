from pathlib import Path
import traceback

import bpy
import bpy_extras
from mathutils import Vector
from .ExportSkeletonOperator import ExportSkeletonOperator
from ..utils import find_last

from ..helpers import OperatorBase, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class RetargetAnimationsOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Retarget selected Nevosoft Animation files onto a new rest pose. Current armature pose will be used as a new rest pose for the animations"""

    bl_idname = "nevosoft.retarget_animations"
    bl_label = "Retarget animations"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def execute(self, context):
        with operator_logger(self):
            obj = ExportSkeletonOperator.find_armature()

            if obj is None:
                raise Exception("Failed to find an armature to retarget animations. Select armature in your 3D viewport and make sure it has a mesh child")

            bpy.ops.object.mode_set(mode='OBJECT')
            select(obj)

            bpy.ops.object.duplicate(linked=False)
            target = bpy.context.active_object
            mesh = target.children[0]
            anm = None
            select(target)

            set_active(target)
            bpy.ops.object.modifier_copy(modifier=find_last(mesh.modifiers, lambda e: e.type == 'ARMATURE').name)
            bpy.ops.object.modifier_apply(modifier=find_last(mesh.modifiers, lambda e: e.type == 'ARMATURE').name)

            set_active(target)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.armature_apply()
            bpy.ops.object.mode_set(mode='OBJECT')

            target.animation_data_clear()
            
            for filepath in self.files:
                try:
                    filename = filepath.name
                    filepath = self.directory + filepath.name
                    anm = AnmFile.read(filepath)

                    anm.pre_transpose(obj.pose)
                    anm.create(target)
                    directory = self.directory + "transposed/"
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    AnmFile.fromObject(target).write(str(Path(directory) / filename))
                except Exception as e:
                    self.error(str(e))
                    traceback.print_exception(e)

            select(target)
            bpy.ops.object.delete()

            self.message("Finished retargetting animations") 
            return {'FINISHED'}
