from __future__ import annotations

import struct
from math import cos, sin, floor
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector, Euler
from ..helpers import getBoneTag

class AnmFile:
    bones: int
    frameTime: int
    movements: list[Vector]
    boneRotations: dict[int, list[Vector]]
    name: str

    def __init__(self, bones, frame_time, movements, bone_rotations, name) -> None:
        self.bones = bones
        self.frameTime = frame_time
        self.movements = movements
        self.boneRotations = bone_rotations
        self.name = name
        pass

    def bone_quat(self, frame: int, index: int) -> Quaternion:
        angle = self.boneRotations[frame][index]
        # return Euler(angle).to_quaternion()
        roll = Quaternion((cos(angle.x * 0.5), sin(angle.x * 0.5), 0, 0))
        pitch = Quaternion((cos(angle.y * 0.5), 0, sin(angle.y * 0.5), 0))
        yaw = Quaternion((cos(angle.z * 0.5), 0, 0, sin(angle.z * 0.5)))
        return yaw @ pitch @ roll  # todo maybe Euler(angle).to_quaternion()

    def create(self, obj: bpy.types.Object) -> bpy.types.AnimData:
        armature: bpy.types.Armature = obj

        if armature.animation_data == None:
            armature.animation_data_create()
        
        action = bpy.data.actions.new(name = self.name)
        armature.animation_data.action = action

        # bpy.context.scene.render.fps = 60
        # msPerFrame = 1000 / bpy.context.scene.render.fps
        # frameDistance = self.frameTime / msPerFrame
        bpy.context.scene.render.fps = 1000
        bpy.context.scene.render.fps_base = self.frameTime
        frameDistance = 1
        bpy.context.scene.frame_current = 0
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = floor(list(self.boneRotations)[-1] * frameDistance)
        base = {}

        for frame, rotations in self.boneRotations.items():
            for bone, coord in enumerate(rotations):
                if not bone in base:
                    base[bone] = coord

        for frame, rotations in self.boneRotations.items():
            for bone, coord in enumerate(rotations):
                boneObj = next(filter(lambda e: getBoneTag(e.bone) == bone, armature.pose.bones), None)
                boneObj.rotation_mode = "QUATERNION"
                # boneObj.rotation_euler = coord
                roll = Quaternion((cos(coord.x * 0.5), sin(coord.x * 0.5), 0, 0))
                pitch = Quaternion((cos(coord.y * 0.5), 0, sin(coord.y * 0.5), 0))
                yaw = Quaternion((cos(coord.z * 0.5), 0, 0, sin(coord.z * 0.5)))
                boneObj.rotation_quaternion = yaw @ pitch @ roll
                # boneObj.rotation_euler = (Euler(coord).to_matrix() @ mp.inverted_safe().to_3x3()).to_euler('XYZ', Euler(coord))
                boneObj.keyframe_insert(data_path="rotation_quaternion", frame=frame * frameDistance)
                # todo

        for frame, coord in enumerate(self.movements):
            armature.location = coord
            armature.keyframe_insert(data_path="location", frame=frame)

        # disable interpolation, as blender can't interpolate by slerp
        for fcurve in armature.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "CONSTANT"

        armature.animation_data.action.name = self.name

    @staticmethod
    def read(filename) -> AnmFile:
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
        with open(filename, 'wb') as file:
            file.write(struct.pack('I', self.bones))
            file.write(struct.pack('I', self.frameTime))

            numFrames = int(list(self.boneRotations)[-1]) + 1
            file.write(struct.pack('I', numFrames))
            
            for frame in range(numFrames):
                file.write(struct.pack('fff', *self.movements[frame].to_tuple()))

            for bone in range(self.bones):
                for frame in range(numFrames):
                    file.write(struct.pack('fff', *self.boneRotations[frame][bone].to_tuple()))           
    
    @staticmethod
    def fromObject(obj) -> AnmFile:
        armature = obj

        boneRotations: dict[int, list[Vector]] = {}
        movements: list[Vector] = []
        action = obj.animation_data.action

        start_frame = bpy.context.scene.frame_start
        end_frame = bpy.context.scene.frame_end
        
        for f in range(start_frame, end_frame + 1):
            # Ensure the frame exists in boneRotations
            boneRotations[f - start_frame] = [Vector((0, 0, 0))] * len(obj.pose.bones)
            movements.append(Vector((0, 0, 0)))
        
        quaternions_by_frame = {}

        for fcurve in action.fcurves:
            if 'pose.bones["' in fcurve.data_path:
                # Extract the bone name
                bone_name = fcurve.data_path.split('"')[1]
                bone = obj.pose.bones.get(bone_name)
                
                if not bone:
                    continue
                
                # Get the bone tag
                tag = getBoneTag(bone.bone)
                
                for f in range(start_frame, end_frame + 1):
                    if "rotation_quaternion" in fcurve.data_path:
                        component = fcurve.array_index
                        
                        # Evaluate the value for the given frame
                        value = fcurve.evaluate(f)

                        if f not in quaternions_by_frame:
                            quaternions_by_frame[f] = [1.0, 0.0, 0.0, 0.0]
                        quaternions_by_frame[f][component] = value
                        
                        quat = Quaternion(quaternions_by_frame[f])
                        
                        # Convert quaternion to Euler
                        euler_rotation = quat.to_euler()
                        boneRotations[f - start_frame][tag] = Vector(euler_rotation)

                    elif "rotation_euler" in fcurve.data_path:
                        component = fcurve.array_index
                        
                        # Evaluate the value for the given frame
                        value = fcurve.evaluate(f)
                        
                        if component == 0:
                            boneRotations[f - start_frame][tag].x = value
                        elif component == 1:
                            boneRotations[f - start_frame][tag].y = value
                        elif component == 2:
                            boneRotations[f - start_frame][tag].z = value

            if fcurve.data_path == 'location':
                for f in range(start_frame, end_frame + 1):
                    value = fcurve.evaluate(f)
                    component = fcurve.array_index
                        
                    if component == 0:
                        movements[f - start_frame].x = value
                    elif component == 1:
                        movements[f - start_frame].y = value
                    elif component == 2:
                        movements[f - start_frame].z = value


        scene = bpy.context.scene
        frame_time = round(1000 * scene.render.fps_base / scene.render.fps)

        return AnmFile(len(obj.pose.bones), frame_time, movements, boneRotations, action.name)