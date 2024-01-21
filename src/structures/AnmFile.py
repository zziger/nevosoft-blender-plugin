from __future__ import annotations

import struct
from math import cos, sin, floor, pi
from pathlib import Path

import bpy
from ..settings.AnimationSettings import AnimationSettings
from ..preferences import get_preferences
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG, REFERENCE_BONE, TEMP_BONE
from ..logger import logger
from mathutils import Quaternion, Vector, Euler, Matrix
from ..helpers import compare_quat, find_bone_by_tag, get_bone_tag, set_active

class AnmFile:
    bones: int
    frame_time: int
    movements: list[Vector]
    bone_rotations: dict[int, list[Vector]]
    name: str

    def __init__(self, bones, frame_time, movements, bone_rotations, name) -> None:
        self.bones = bones
        self.frame_time = frame_time
        self.movements = movements
        self.bone_rotations = bone_rotations
        self.name = name
        pass

    @staticmethod
    def to_quat(coord) -> Quaternion:
        """Converts rotation from animation into quaternion in the game's original rotation order"""

        roll = Quaternion((cos(coord.x * 0.5), sin(coord.x * 0.5), 0, 0))
        pitch = Quaternion((cos(coord.y * 0.5), 0, sin(coord.y * 0.5), 0))
        yaw = Quaternion((cos(coord.z * 0.5), 0, 0, sin(coord.z * 0.5)))
        return yaw @ pitch @ roll

    def bone_quat(self, frame: int, index: int) -> Quaternion:
        """Returns a quaternion for a specified bone at a specified frame"""

        angle = self.bone_rotations[frame][index]
        return AnmFile.to_quat(angle)

    def create(self, obj: bpy.types.Object, use_quat = True, anm_settings: AnimationSettings = AnimationSettings(), use_old_action = False, start_frame = 0) -> bpy.types.AnimData:
        """Applies animation data to a specified object"""

        armature: bpy.types.Armature = obj

        if armature.animation_data == None:
            armature.animation_data_create()
        
        action = armature.animation_data.action

        if not use_old_action:
            action = bpy.data.actions.new(name = self.name)
            armature.animation_data.action = action

        bpy.context.scene.render.fps = 1000
        bpy.context.scene.render.fps_base = self.frame_time
        frame_distance = 1
        bpy.context.scene.frame_current = start_frame
        bpy.context.scene.frame_start = start_frame
        bpy.context.scene.frame_end = start_frame + floor(list(self.bone_rotations)[-1] * frame_distance)

        logger.info('Applying animation %s from frame %d to %d', self.name, start_frame, bpy.context.scene.frame_end)

        if anm_settings.bone_rotations:
            logger.debug("Applying bone rotations")
            for frame, rotations in self.bone_rotations.items():
                for bone, coord in enumerate(rotations):
                    boneObj: bpy.types.PoseBone = next(filter(lambda e: get_bone_tag(e) == bone, armature.pose.bones), None)

                    if boneObj == None:
                        logger.warn("Failed to find bone %d", bone)
                        continue

                    if use_quat:
                        boneObj.rotation_mode = "QUATERNION"
                        boneObj.rotation_quaternion = AnmFile.to_quat(coord)
                        boneObj.keyframe_insert(data_path="rotation_quaternion", frame=(frame + start_frame) * frame_distance)
                    else:
                        boneObj.rotation_mode = "XYZ"
                        boneObj.rotation_euler = coord
                        boneObj.keyframe_insert(data_path="rotation_euler", frame=(frame + start_frame) * frame_distance)

        if anm_settings.location_x or anm_settings.location_y or anm_settings.location_z:
            logger.debug("Applying object location")
            for frame, coord in enumerate(self.movements):
                if anm_settings.location_x:
                    armature.location.x = coord.x
                    armature.keyframe_insert(data_path="location", frame=(frame + start_frame) * frame_distance, index=0)

                if anm_settings.location_y:
                    armature.location.y = coord.y
                    armature.keyframe_insert(data_path="location", frame=(frame + start_frame) * frame_distance, index=1)

                if anm_settings.location_z:
                    armature.location.z = coord.z
                    armature.keyframe_insert(data_path="location", frame=(frame + start_frame) * frame_distance, index=2)

        # disable interpolation, as blender can't interpolate by slerp
        for fcurve in armature.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "CONSTANT"

        armature.animation_data.action.name = self.name

    def pre_transpose(self, pose: bpy.types.Pose):
        """Retargets all animation bone rotations to a new rest pose.
        
        Resulting animation is not suitable for export, as the rotations have different origin (not (0, 1, 0)).
        Apply animation to a retargeted model first, inject aligned bones, and read animations from them.
        """

        logger.debug("Pre-transposing animation to pose")

        for bone in pose.bones:
            tag = get_bone_tag(bone)
            
            quat_transformation = bone.rotation_euler.to_quaternion()

            if bone.rotation_mode == "QUATERNION":
                quat_transformation = bone.rotation_quaternion

            quat_transformation = quat_transformation.inverted()

            for frame, rotations in self.bone_rotations.items():
                # Get the animation keyframe quaternion
                quat_keyframe = AnmFile.to_quat(rotations[tag])
                
                # Adjust the keyframe with the transformation
                quat_adjusted = quat_transformation @ quat_keyframe
                rotations[tag] = Vector(quat_adjusted.to_euler())

    @staticmethod
    def read(filename) -> AnmFile:
        """Reads animation from an .anm file"""

        logger.info('Reading animation from %s', filename)

        with open(filename, 'rb') as file:
            bone_count = struct.unpack('I', file.read(4))[0]
            frame_time = struct.unpack('I', file.read(4))[0]
            frame_count = struct.unpack('I', file.read(4))[0]

            movements: list[Vector] = [None] * frame_count
            bone_rotations_raw: list[Vector] = [None] * (frame_count * bone_count)
            bone_rotations = {}

            for frame in range(frame_count):
                movements[frame] = Vector(struct.unpack('fff', file.read(4 * 3)))

            for i in range(frame_count * bone_count):
                bone_rotations_raw[i] = Vector(struct.unpack('fff', file.read(4 * 3)))

            for frame in range(frame_count):
                bone_rotations[frame] = []
                for bone in range(bone_count):
                    bone_rotations[frame].append(bone_rotations_raw[frame + bone * frame_count])

        return AnmFile(bone_count, frame_time, movements, bone_rotations, Path(filename).stem)
    
    def write(self, filename: str):
        """Writes animation to an .anm file"""

        logger.info('Writing animation to %s', filename)

        with open(filename, 'wb') as file:
            file.write(struct.pack('I', self.bones))
            file.write(struct.pack('I', self.frame_time))

            num_frames = int(list(self.bone_rotations)[-1]) + 1
            file.write(struct.pack('I', num_frames))
            
            for frame in range(num_frames):
                file.write(struct.pack('fff', *self.movements[frame].to_tuple()))

            for bone in range(self.bones):
                for frame in range(num_frames):
                    file.write(struct.pack('fff', *self.bone_rotations[frame][bone].to_tuple()))   

    @staticmethod
    def __inject_aligned_bones(obj: bpy.types.Object):
        """Injects temporary bones pointing to the (0, 1, 0), allowing to read pose rotation values in correct space"""

        logger.debug('Injecting aligned bones to %s', obj.name)
        armature: bpy.types.Armature = obj.data
        
        set_active(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        for edit_bone in list(armature.edit_bones):
            if compare_quat(edit_bone.matrix.to_quaternion(), Quaternion()) and edit_bone.roll == 0:
                logger.debug('Skipping aligned bone injection to %s (already aligned)', edit_bone.name)
                continue

            new_bone = armature.edit_bones.new(edit_bone.name + "_retarget")
            new_bone.head = edit_bone.head
            new_bone.tail = edit_bone.head + (BONE_DIRECTION_DEBUG if get_preferences().debug else BONE_DIRECTION)
            new_bone.parent = edit_bone
            new_bone[TEMP_BONE] = True
            edit_bone[REFERENCE_BONE] = new_bone.name
            edit_bone.hide = True
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def __cleanup_aligned_bones(obj: bpy.types.Object):
        """Removes temporary bones from the object"""

        logger.debug('Cleaning up aligned bones from %s', obj.name)
        armature: bpy.types.Armature = obj.data
        
        set_active(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        for edit_bone in list(armature.edit_bones):
            if REFERENCE_BONE in edit_bone:
                del edit_bone[REFERENCE_BONE]
            if TEMP_BONE in edit_bone:
                armature.edit_bones.remove(edit_bone)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    @staticmethod
    def fromObject(obj: bpy.types.Object, align_bones = True, anm_settings: AnimationSettings = AnimationSettings(), start_frame = -1, end_frame = -1, frame_time = -1) -> AnmFile:
        """Creates an animation from an object
        
        Parameters
        ----------
        obj : bpy.types.Object
            Object to read animation from
        align_bones : bool, optional
            Whether to inject temporary bones to align the animation to the correct space, by default True
        """

        logger.info('Creating animation from object %s', obj.name)
        armature: bpy.types.Armature = obj.data
        scene = bpy.context.scene

        if align_bones:
            AnmFile.__inject_aligned_bones(obj)

        try:
            bone_rotations: dict[int, list[Vector]] = {}
            movements: list[Vector] = []
            action = obj.animation_data.action

            curr_frame = bpy.context.scene.frame_current
            if start_frame == -1:
                start_frame = bpy.context.scene.frame_start
            if end_frame == -1:
                end_frame = bpy.context.scene.frame_end
            bone_count = sum(1 for pose_bone in obj.pose.bones if not TEMP_BONE in pose_bone.bone)
            
            for f in range(start_frame, end_frame + 1):
                bpy.context.scene.frame_set(f)
                frame_id = f - start_frame
                logger.debug('Creating animation frame %d (%s)', frame_id, f)
                
                movement = Vector(obj.matrix_world @ obj.pose.bones[find_bone_by_tag(armature.bones, 0).name].head)

                if not anm_settings.location_x:
                    movement.x = 0
                if not anm_settings.location_y:
                    movement.y = 0
                if not anm_settings.location_z:
                    movement.z = 0
                    
                movements.append(movement)

                bone_rotations[frame_id] = [Vector((0, 0, 0)) for _ in range(bone_count)]

                if anm_settings.bone_rotations:
                    for bone_index in range(len(obj.pose.bones)):
                        pose_bone = obj.pose.bones[bone_index]
                        bone = pose_bone.bone
                        reference_pose_bone = obj.pose.bones[bone[REFERENCE_BONE]] if REFERENCE_BONE in bone else pose_bone

                        if TEMP_BONE in bone:
                            logger.debug('Skipping bone %s', bone.name)
                            continue

                        bone_tag = get_bone_tag(pose_bone)
                        matrix: Matrix = reference_pose_bone.matrix 

                        parent_pose_bone = pose_bone.parent
                        if parent_pose_bone:
                            parent_bone = parent_pose_bone.bone
                            parent_reference_pose_bone = obj.pose.bones[parent_bone[REFERENCE_BONE]] if REFERENCE_BONE in parent_bone else parent_pose_bone
                            matrix = parent_reference_pose_bone.matrix.inverted_safe() @ matrix

                        bone_rotations[frame_id][bone_tag] = Vector(matrix.to_quaternion().to_euler('XYZ'))

            scene.frame_current = curr_frame
            if frame_time == -1:
                frame_time = round(1000 * scene.render.fps_base / scene.render.fps)

            return AnmFile(bone_count, frame_time, movements, bone_rotations, action.name)
        finally:
            if align_bones:
                AnmFile.__cleanup_aligned_bones(obj)

    batch_data = []

    @classmethod
    def hasBatch(cls):
        return len(cls.batch_data) > 0

    @classmethod
    def createBatch(cls, animations: list[AnmFile], obj: bpy.types.Object):
        armature: bpy.types.Armature = obj

        if armature.animation_data == None:
            armature.animation_data_create()
        
        action = bpy.data.actions.new(name = 'animation_batch')
        armature.animation_data.action = action
        
        cls.batch_data = animations

        start_frame = 0
        for animation in animations:
            animation.create(obj, use_old_action=True, start_frame=start_frame)
            start_frame += len(animation.movements)

    @classmethod
    def reapply_batch(cls, obj: bpy.types.Object, anm_settings: AnimationSettings = AnimationSettings()):
        if not cls.hasBatch():
            raise Exception("Batch animation data is missing")

        start_frame = 0
        for animation in cls.batch_data:
            animation.create(obj, use_old_action=True, start_frame=start_frame, anm_settings=anm_settings)
            start_frame += len(animation.movements)

    @classmethod
    def saveBatch(cls, obj: bpy.types.Object, directory: str):
        armature: bpy.types.Armature = obj
        
        start_frame = 0
        for old_animation in cls.batch_data:
            frame_count = len(old_animation.movements)
            logger.info('Saving batched animation %s from frame %d to %d', old_animation.name, start_frame, start_frame + frame_count - 1)
            animation = cls.fromObject(obj, start_frame=start_frame, end_frame=start_frame + frame_count - 1, frame_time=old_animation.frame_time)
            animation.write(directory + "/" + old_animation.name + ".anm")
            start_frame += frame_count