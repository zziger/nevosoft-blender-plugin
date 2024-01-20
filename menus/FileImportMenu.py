import bpy

from ..operators.ImportObjectOperator import ImportObjectOperator
from ..operators.ImportMeshOperator import ImportMeshOperator
from ..operators.ImportCharacterOperator import ImportCharacterOperator
from ..operators.ImportSkeletonOperator import ImportSkeletonOperator
from ..operators.ImportAnimationOperator import ImportAnimationOperator

class FileImportMenu:
    @staticmethod
    def draw(self: bpy.types.Menu, context):
        self.layout.operator(ImportObjectOperator.bl_idname, text=ImportObjectOperator.bl_label, icon="MESH_CUBE")
        self.layout.operator(ImportMeshOperator.bl_idname, text=ImportMeshOperator.bl_label, icon="MESH_DATA")
        self.layout.operator(ImportCharacterOperator.bl_idname, text=ImportCharacterOperator.bl_label, icon="OUTLINER_OB_ARMATURE")
        self.layout.operator(ImportSkeletonOperator.bl_idname, text=ImportSkeletonOperator.bl_label, icon="ARMATURE_DATA")
        self.layout.operator(ImportAnimationOperator.bl_idname, text=ImportAnimationOperator.bl_label, icon="ANIM")

def register():
    bpy.types.TOPBAR_MT_file_import.append(FileImportMenu.draw)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(FileImportMenu.draw)
