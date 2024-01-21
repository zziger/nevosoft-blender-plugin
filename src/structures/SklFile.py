from __future__ import annotations
from os import path

import struct
from dataclasses import dataclass, field
from math import floor

from ..settings.ImportSkeletonSettings import ImportSkeletonSettings
from ..logger import logger
import bmesh
import bpy
import bpy.types
from ..constants import BONE_DIRECTION, BONE_DIRECTION_DEBUG
from mathutils import Vector, Matrix, Quaternion
from ..preferences import get_preferences
from ..helpers import get_bone_properties, get_bone_tag, find_bone_by_tag, set_active

from .AnmFile import AnmFile

magic = b'ZEGR'

def notNullFilter(iter):
    return list(filter(lambda e: e != None, iter))


@dataclass
class AnimBone:
    pos: Vector
    mat: Matrix


@dataclass
class SklNsBone:
    name: str = ""
    children: list[int] = field(default_factory=lambda: [])


@dataclass
class SklNsVertexLink:
    data: list[SklLink] = field(default_factory=lambda: [])


@dataclass
class SklNsFaceUv:
    uv0: Vector
    uv1: Vector
    uv2: Vector


@dataclass
class SklBone:
    pos: Vector
    name: str = ""
    children: list[int] = field(default_factory=lambda: [])


@dataclass
class SklLink:
    weight: float
    indx: int
    pos: Vector


@dataclass
class SklVertexLink:
    links: list[SklLink] = field(default_factory=lambda: [])


@dataclass
class SklFace:
    indx0: int
    indx1: int
    indx2: int


@dataclass(unsafe_hash=True)
class SklBufVertex:
    index: int
    uvX: int
    uvY: int
    
@dataclass()
class SklNsMeta:
    vertices: list[Vector] | None = None


class SklVertex:
    xyz: Vector
    normal: Vector
    uv: Vector


class SklLinkedVertex:
    xyz: Vector
    normal: Vector


class SklNs:
    bones: list[SklNsBone]
    boneVecs: list[Vector]
    vertLinks: list[SklNsVertexLink]
    indxFaces: list[SklFace]
    uvFaces: list[SklNsFaceUv]
    meta: SklNsMeta

    def __init__(self):
        self.bones = []
        self.boneVecs = []
        self.vertLinks = []
        self.indxFaces = []
        self.uvFaces = []
        self.meta = SklNsMeta()

    def write(self, filename):
        with open(filename, 'wb') as file:
            numVerts = len(self.vertLinks)
            numBones = len(self.boneVecs)

            file.write(struct.pack('I', numVerts))
            file.write(struct.pack('I', numBones))

            for bone in self.boneVecs:
                file.write(struct.pack('fff', *bone.to_tuple()))

            for ns_link in self.vertLinks:
                for link in ns_link.data[:3]:
                    file.write(struct.pack('f', link.weight))
                    file.write(struct.pack('I', link.indx))
                    file.write(struct.pack('fff', *link.pos.to_tuple()))
                for _ in range(max(3 - len(ns_link.data), 0)):
                    file.write(struct.pack('f', 0.0))
                    file.write(struct.pack('I', 0))
                    file.write(struct.pack('fff', 0.0, 0.0, 0.0))

            for ns_bone in self.bones:
                file.write(struct.pack('I', len(ns_bone.children)))
                for child in ns_bone.children:
                    file.write(struct.pack('I', child))
                for _ in range(5 - len(ns_bone.children)):  # arr is const 5 length, filling rest space with zeros
                    file.write(struct.pack('I', 0))
                file.write(ns_bone.name.encode("utf-8")[:32].ljust(32, b'\x00'))

            numFaces = len(self.indxFaces)
            file.write(struct.pack('I', numFaces))

            for face in self.indxFaces:
                file.write(struct.pack('III', face.indx0, face.indx1, face.indx2))

            for face in self.uvFaces:
                file.write(struct.pack('ff', *face.uv0.to_tuple()))
                file.write(struct.pack('ff', *face.uv1.to_tuple()))
                file.write(struct.pack('ff', *face.uv2.to_tuple()))

            file.write(magic)
            
            if self.meta.vertices != None:
                for vertex in self.meta.vertices:
                    file.write(struct.pack('fff', *vertex.to_tuple()))
    
    def read(self, filename: str) -> None:
        with open(filename, 'rb') as file:
            numVerts = struct.unpack('I', file.read(4))[0]
            numBones = struct.unpack('I', file.read(4))[0]

            for _ in range(numBones):
                self.boneVecs.append(Vector(struct.unpack('fff', file.read(3 * 4))))

            for _ in range(numVerts):
                vertexLink = SklNsVertexLink()
                for _ in range(3):
                    link = SklLink(
                        struct.unpack('f', file.read(4))[0],
                        struct.unpack('I', file.read(4))[0],
                        Vector(struct.unpack('fff', file.read(3 * 4)))
                    )
                    vertexLink.data.append(link)
                self.vertLinks.append(vertexLink)

            for _ in range(numBones):
                bone = SklNsBone()
                boneChildCount = struct.unpack('I', file.read(4))[0]
                for childIndex in range(5):
                    if childIndex >= boneChildCount:
                        file.seek(4, 1)
                        continue
                    bone.children.append(struct.unpack('I', file.read(4))[0])
                bone.name = file.read(32).decode("utf-8")
                self.bones.append(bone)

            numFaces = struct.unpack('I', file.read(4))[0]

            for _ in range(numFaces):
                data = struct.unpack('III', file.read(3 * 4))
                self.indxFaces.append(SklFace(data[0], data[1], data[2]))

            for _ in range(numFaces):
                self.uvFaces.append(SklNsFaceUv(
                    Vector(struct.unpack('ff', file.read(2 * 4))),
                    Vector(struct.unpack('ff', file.read(2 * 4))),
                    Vector(struct.unpack('ff', file.read(2 * 4)))
                ))

            if file.tell() + len(magic) < path.getsize(filename):
                logger.debug("Trying to read meta block")
                if file.read(len(magic)) != magic:
                    logger.warn("Invalid SKL meta block")
                    return
                
                self.meta.vertices = []
                for _ in range(numVerts):
                    self.meta.vertices.append(Vector(struct.unpack('fff', file.read(3 * 4))))

class SklFile:
    bones: list[SklBone]
    vertLinks: list[SklVertexLink]
    faces: list[SklFace]
    indicesMapper: list[int]
    bufVerts: list[SklBufVertex]
    uvFaces: list[SklNsFaceUv]
    meta: SklNsMeta

    animBones: list[AnimBone]
    anim: AnmFile

    def __init__(self):
        self.bones = []
        self.vertLinks = []
        self.faces = []
        self.indicesMapper = []
        self.bufVerts = []
        self.uvFaces = []
        self.animBones = []

    def prepareBoneAnim(self, frame: int, ibone: int, pbone_index: int):
        if ibone == 0:
            self.animBones[0] = AnimBone(Vector((0, 0, 0)), self.anim.bone_quat(frame, 0).to_matrix())
        else:
            m = self.anim.bone_quat(frame, ibone).to_matrix()
            pbone = self.animBones[pbone_index]
            self.animBones[ibone] = AnimBone((pbone.mat @ self.bones[ibone].pos) + pbone.pos, pbone.mat @ m)

        for child in self.bones[ibone].children:
            self.prepareBoneAnim(frame, child, ibone)

    def prepareBone(self, frame: int, ibone: int, pbone_index: int):
        if ibone != 0:
            self.bones[ibone].pos += self.bones[pbone_index].pos

        for child in self.bones[ibone].children:
            self.prepareBone(frame, child, ibone)

    def isComplex(self):
        if self.meta.vertices != None:
            return False
        
        for i, vertLink in enumerate(self.vertLinks):
            if len(vertLink.links) > 1:
                return True
        return False
    
    def simplify(self, anim):
        if not self.isComplex():
            logger.warn("Attempted to simplify non-complex model")
            return
        
        self.animBones = [None] * len(self.bones)
        self.anim = anim

        self.prepareBoneAnim(0, 0, 0)

        linkedVerts: list[SklLinkedVertex] = []
        for i, vertLink in enumerate(self.vertLinks):
            linkedVert = SklLinkedVertex()
            linkedVert.xyz = Vector((0, 0, 0))

            sum = 0

            for link in vertLink.links:
                sum  = sum + link.weight
                bone = self.animBones[link.indx]
                linkedVert.xyz += (bone.mat @ link.pos + bone.pos) * link.weight

            linkedVerts.append(linkedVert)

        for i, vertLink in enumerate(self.vertLinks):
            linkedVert = linkedVerts[i]

            if len(vertLink.links) <= 1:
                continue

            indx = vertLink.links[0].indx
            bone: AnimBone = self.animBones[indx]
            vertLink.links = [
                SklLink(1, indx, (linkedVert.xyz - bone.pos) @ bone.mat.to_4x4())
            ]

    def create(self, name: str, image=None, skl_settings: ImportSkeletonSettings = ImportSkeletonSettings()) -> bpy.types.Object:
        scn = bpy.context.scene
        if scn == None:
            raise Exception("No scene to import to!")
        
        z_offset = 0

        if skl_settings.load_at_0z:
            z_offset = -self.bones[0].pos.z
            self.bones[0].pos = Vector((0, 0, 0))

        # creating material
        mat = bpy.data.materials.new(name="material")  # todo name
        mat.use_nodes = True
        mat.blend_method = 'HASHED'
        matBsdf = next(filter(lambda e: e.type == 'BSDF_PRINCIPLED', mat.node_tree.nodes), None)
        matTex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        mat.node_tree.links.new(matBsdf.inputs['Base Color'], matTex.outputs['Color'])
        mat.node_tree.links.new(matBsdf.inputs['Alpha'], matTex.outputs['Alpha'])

        if image != None:
            matTex.image = image

        # creating mesh and objects
        msh = bpy.data.meshes.new(name + "_mesh")
        sklObj = bpy.data.objects.new(name + "_mesh", msh)
        sklObj.data.materials.append(mat)
        scn.collection.objects.link(sklObj)

        self.prepareBone(0, 0, 0)

        linkedVerts: list[SklLinkedVertex] = []
        for i, vertLink in enumerate(self.vertLinks):
            linkedVert = SklLinkedVertex()
            linkedVert.xyz = Vector((0, 0, 0))

            if self.meta.vertices != None:
                linkedVert.xyz = self.meta.vertices[i] + Vector((0, 0, z_offset))
            else:
                for link in vertLink.links:
                    bone = self.bones[link.indx]
                    linkedVert.xyz += (link.pos + bone.pos) * link.weight
                    break

            linkedVerts.append(linkedVert)

        vertices = [None] * len(linkedVerts)
        uvs = []
        normals = []
        faces = []

        for i, link in enumerate(linkedVerts):
            vertices[i] = link.xyz

        for i, face in enumerate(self.faces):
            uvs.append(self.uvFaces[i].uv0)
            uvs.append(self.uvFaces[i].uv1)
            uvs.append(self.uvFaces[i].uv2)
            faces.append((face.indx0, face.indx1, face.indx2))

        msh.from_pydata(vertices, [], faces)

        uvmap = msh.uv_layers.new(name='uvmap')

        for face in msh.polygons:
            i = 0
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uvmap.data[loop_idx].uv = uvs[face.index * 3 + i]
                i += 1

        armature = bpy.data.armatures.new(name + "_armature")
        # armature.show_names=True
        armature.display_type = "STICK"
        rig = bpy.data.objects.new(name + "_armature", armature)
        rig.show_in_front = True
        sklObj.parent = rig

        modifier = sklObj.modifiers.new(type='ARMATURE', name="Armature")
        modifier.object = rig
        bpy.context.scene.collection.objects.link(rig)

        bonemap: map[int, bpy.types.Bone] = {}

        set_active(rig)
        bpy.ops.object.mode_set(mode='EDIT')
        for index, bone in enumerate(self.bones):
            name = bone.name
            current_bone = armature.edit_bones.new(name)
            get_bone_properties(current_bone).tag = index
            bonemap[index] = current_bone
            group = sklObj.vertex_groups.new(name=name)
            for indexInner, boneInner in enumerate(self.bones):
                if index in boneInner.children:
                    current_bone.parent = find_bone_by_tag(armature.edit_bones, indexInner)
            current_bone.use_local_location = False
            current_bone.head = bone.pos
            current_bone.tail = bone.pos + (BONE_DIRECTION_DEBUG if get_preferences().debug else BONE_DIRECTION)

            current_bone.use_local_location = True

        for i, vertLink in enumerate(self.vertLinks):
            for link in vertLink.links:
                bone = self.bones[link.indx]
                if link.weight != 0:
                    sklObj.vertex_groups[find_bone_by_tag(armature.edit_bones, link.indx).name].add([i], link.weight, "ADD")

        bpy.ops.object.mode_set(mode='OBJECT')

        return sklObj

    @staticmethod
    def read(filename) -> SklFile:
        data = SklNs()
        data.read(filename)
        # data.write(filename + ".sus")
        skl = SklFile()

        for i, nsBone in enumerate(data.bones):
            bone = SklBone(data.boneVecs[i], nsBone.name)
            for j, child in enumerate(nsBone.children):
                bone.children.append(child)
            skl.bones.append(bone)

        skl.faces = data.indxFaces

        for i, nsVertLink in enumerate(data.vertLinks):
            vertLink = SklVertexLink()
            for link in nsVertLink.data:
                if link.weight != 0:
                    vertLink.links.append(link)
            skl.vertLinks.append(vertLink)

        indxCount = len(data.indxFaces) * 3
        vertMap: map[SklBufVertex, list[int]] = {}


        skl.uvFaces = data.uvFaces
        indxs = [item for faces in data.indxFaces for item in (faces.indx0, faces.indx1, faces.indx2)]
        tcs = [item for uvs in data.uvFaces for item in (uvs.uv0, uvs.uv1, uvs.uv2)]

        for i in range(indxCount):
            key = SklBufVertex(indxs[i], tcs[i].x, tcs[i].y)
            if not key in vertMap:
                vertMap[key] = []

            vertMap[key].append(i)

        skl.indicesMapper = [None] * indxCount
        for key, value in vertMap.items():
            nindx = len(skl.bufVerts)
            for indx in value:
                skl.indicesMapper[indx] = nindx
            skl.bufVerts.append(key)

        skl.meta = data.meta
        return skl

    @staticmethod
    def prepareBoneWrite(armature: bpy.types.Armature, data: SklNs, ibone: int, pbone_index: int):
        bone = find_bone_by_tag(armature.edit_bones, ibone)

        if ibone == 0:
            data.boneVecs[ibone] = bone.head
        else:
            pbone = find_bone_by_tag(armature.edit_bones, pbone_index)
            data.boneVecs[ibone] = bone.head - pbone.head

        child_ids: list[int] = []
        for children in bone.children:
            child_ids.append(get_bone_tag(children))

        data.bones[ibone] = SklNsBone(bone.name, child_ids)

        for children in bone.children:
            SklFile.prepareBoneWrite(armature, data, get_bone_tag(children), ibone)

    @staticmethod
    def ensureBoneIds(rig: bpy.types.Object):
        armature: bpy.types.Armature = rig.data
        
        root_bones = list(filter(lambda e: e.parent == None, armature.bones))
        if len(root_bones) > 1:
            raise Exception("Multiple root bones found! Please ensure that your armature has only one root bone with ID 0")
            
        if get_bone_tag(root_bones[0]) != 0:
            raise Exception("Root bone must have ID 0")

        for bone in armature.bones:
            if get_bone_tag(bone) < 0:
                raise Exception("Bone " + bone.name + " has no ID")
            
        used = list()
        for bone in armature.bones:
            if get_bone_tag(bone) in used:
                raise Exception("Bone " + bone.name + " has duplicate ID " + str(get_bone_tag(bone)))
            used.append(get_bone_tag(bone))
            
        for i in range(len(armature.bones)):
            if find_bone_by_tag(armature.bones, i) == None:
                raise Exception("Bone with ID " + str(i) + " not found")
    
    @staticmethod
    def write(rig: bpy.types.Object, filename):
        SklFile.ensureBoneIds(rig)
        
        data = SklNs()

        armature: bpy.types.Armature = rig.data
        data.boneVecs = [None] * len(armature.bones)
        data.bones = [None] * len(armature.bones)

        bpy.ops.object.mode_set(mode='OBJECT')
        set_active(rig)
        bpy.ops.object.mode_set(mode='EDIT')
        SklFile.prepareBoneWrite(armature, data, 0, 0)

        obj: bpy.types.Object = rig.children[0]
        bm: bmesh.types.BMesh = bmesh.new()
        deps_graph = bpy.context.evaluated_depsgraph_get()
        bm.from_object(obj, deps_graph)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')

        msh: bpy.types.Mesh = rig.children[0].data
        uvmap = msh.uv_layers[0]
        data.uvFaces = [None] * len(bm.faces)
        data.indxFaces = [None] * len(bm.faces)
        
        
        uv_layer = bm.loops.layers.uv.verify()
        for index, face in enumerate(bm.faces):
            data.uvFaces[index] = SklNsFaceUv(face.loops[0][uv_layer].uv, face.loops[1][uv_layer].uv, face.loops[2][uv_layer].uv)
        
        for index, face in enumerate(bm.faces):
            data.indxFaces[index] = SklFace(face.verts[0].index, face.verts[1].index, face.verts[2].index)
        
        deform = bm.verts.layers.deform.active
        
        
        data.vertLinks = [None] * len(bm.verts)
        data.meta.vertices = [None] * len(bm.verts)
        for index, vertex in enumerate(bm.verts):

            vertex: bmesh.types.BMVert
            vertexDeform: bmesh.types.BMDeformVert = vertex[deform]
            
            ns_link = SklNsVertexLink()
            for group, weight in vertexDeform.items():
                if weight == 0:
                    continue

                vertex_group = obj.vertex_groups[group]
                bone: bpy.types.Bone = rig.data.edit_bones[vertex_group.name]
                if bone is None:
                    logger.warn("Bone not found: " + vertex_group.name)
                    continue

                tag = get_bone_tag(rig.data.bones[vertex_group.name])
                pos = vertex.co - bone.head
                ns_link.data.append(SklLink(weight, tag, pos)),

            data.vertLinks[index] = ns_link
            data.meta.vertices[index] = vertex.co

        data.write(filename)
        bpy.ops.object.mode_set(mode='OBJECT')

