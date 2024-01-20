import bpy

from ..operators.ExportObjectOperator import ExportObjectOperator
from ..operators.ExportMeshOperator import ExportMeshOperator
from ..operators.ExportCharacterOperator import ExportCharacterOperator
from ..operators.ExportSkeletonOperator import ExportSkeletonOperator
from ..operators.ExportAnimationOperator import ExportAnimationOperator

class FileExportMenu:
    @staticmethod
    def draw(self: bpy.types.Menu, context):
        self.layout.operator(ExportObjectOperator.bl_idname, text=ExportObjectOperator.bl_label, icon="MESH_CUBE")
        self.layout.operator(ExportMeshOperator.bl_idname, text=ExportMeshOperator.bl_label, icon="MESH_DATA")
        self.layout.operator(ExportCharacterOperator.bl_idname, text=ExportCharacterOperator.bl_label, icon="OUTLINER_OB_ARMATURE")
        self.layout.operator(ExportSkeletonOperator.bl_idname, text=ExportSkeletonOperator.bl_label, icon="ARMATURE_DATA")
        self.layout.operator(ExportAnimationOperator.bl_idname, text=ExportAnimationOperator.bl_label, icon="ANIM")

def register():
    bpy.types.TOPBAR_MT_file_export.append(FileExportMenu.draw)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(FileExportMenu.draw)
