import math
from mathutils import Quaternion
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

def getBoneTag(bone):
    if not 'tag' in bone or bone['tag'] == None:
        return -1
    return bone['tag']

def findBoneByTag(bones, tag: int) -> bpy.types.Bone:
    return next(filter(lambda e: getBoneTag(e) == tag, bones), None)

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


def compare_quat(q1: Quaternion, q2: Quaternion) -> bool:
    return math.isclose(abs(q1.dot(q2)), 1, rel_tol = 1e-12)