import math
from typing import Union
from mathutils import Quaternion
from .extensions import BoneProperties
from .logger import logger
import bpy

class OperatorBase:
    def message(self, msg):
        logger.info(msg)
        self.report({"INFO"}, msg)

    def warning(self, msg):
        logger.warn(msg)
        self.report({"WARNING"}, msg)

    def error(self, msg, logToConsole=True):
        if logToConsole:
            logger.error(msg)
        self.report({"ERROR"}, msg)


class ErrorException(Exception):
    pass

def get_bone_properties(bone: Union[bpy.types.Bone, bpy.types.EditBone, bpy.types.PoseBone]) -> BoneProperties:
    if isinstance(bone, bpy.types.Bone) or isinstance(bone, bpy.types.EditBone):
        return bone.nevosoft
    elif isinstance(bone, bpy.types.PoseBone):
        return bone.bone.nevosoft
    
def get_bone_tag(bone: Union[bpy.types.Bone, bpy.types.EditBone, bpy.types.PoseBone]) -> int:
    return get_bone_properties(bone).tag

def find_bone_by_tag(bones, tag: int) -> bpy.types.Bone:
    return next(filter(lambda e: get_bone_tag(e) == tag, bones), None)

def deselect():
    for inner in bpy.context.selected_objects:
        inner.select_set(False)

def select(element: bpy.types.Object, recursive = True):
    deselect()
    bpy.context.view_layer.objects.active = element
    element.select_set(True)
    if recursive:
        bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')

def set_active(element: bpy.types.Object, select_recursive = True):
    bpy.context.view_layer.objects.active = element
    select(element, recursive=select_recursive)

def duplicate(element: bpy.types.Object):
    bpy.ops.object.duplicate(linked=False)
    target = bpy.context.active_object

def save_mat_texture(mat: bpy.types.Material, path):
    found = False
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeBsdfPrincipled):
                if len(node.inputs['Base Color'].links) > 0:
                    link = node.inputs['Base Color'].links[0]
                    if isinstance(link.from_node,
                                    bpy.types.ShaderNodeTexImage) and link.from_node.image is not None:
                        found = True
                        link.from_node.image.save(filepath=path)

    return found


def compare_quat(q1: Quaternion, q2: Quaternion) -> bool:
    return math.isclose(abs(q1.dot(q2)), 1, rel_tol = 1e-12)