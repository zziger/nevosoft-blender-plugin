from __future__ import annotations

import struct

import bmesh
import bpy
import bpy.types
from bmesh.types import BMFace
from mathutils import Vector

from ..bake import bake_texture


class MshNs:
    vertices: list[Vector]
    faces: list[tuple[int, int, int]]
    uvs: list[tuple[float, float]]

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.uvs = []

    def write(self, filename):
        with open(filename, 'wb') as file:
            file.seek(0)
            file.write(b'MSH'.ljust(29, b'\x00'))  # filling header with zeroes, TODO investigate meaning
            file.write(struct.pack('I', len(self.vertices)))
            file.write(struct.pack('I', len(self.faces)))

            print(f'exported {len(self.vertices)} vertices {len(self.faces)} faces')

            for vert in self.vertices:
                file.write(struct.pack('fff', *vert.to_tuple()))

            for face in self.faces:
                file.write(struct.pack('iii', *face))

            if len(self.uvs) == 0:
                for uv in range(len(self.faces) * 3):
                    file.write(struct.pack('ff', 0.0, 0.0))
            else:
                assert len(self.uvs) == len(self.faces) * 3
                for uv in self.uvs:
                    file.write(struct.pack('ff', *uv))

            file.truncate()

    def read(self, filename: str) -> None:
        with open(filename, 'rb') as file:
            if file.read(3) != b'MSH':
                raise Exception("Invalid MSH header")
            file.seek(29, 0)

            num_vertices = struct.unpack('I', file.read(4))[0]
            num_faces = struct.unpack('I', file.read(4))[0]

            for i in range(num_vertices):
                self.vertices.append(Vector(struct.unpack('fff', file.read(3 * 4))))

            for i in range(num_faces):
                (idx1, idx2, idx3) = struct.unpack('iii', file.read(3 * 4))
                self.faces.append((idx1, idx2, idx3))

            for i in range(num_faces * 3):
                (uv1, uv2) = struct.unpack('ff', file.read(2 * 4))
                self.uvs.append((uv1, uv2))


def polygon_to_tris(vertices):
    for i in range(1, len(vertices) - 1):
        yield vertices[0], vertices[i], vertices[i + 1]


class MshFile:
    ns: MshNs

    def create(self, image: bpy.types.Image = None, name: str = "object") -> bpy.types.Object:
        scene = bpy.context.scene
        if scene is None:
            raise Exception("No scene to import to!")

        # creating material
        mat = bpy.data.materials.new(name="material")  # todo name
        mat.use_nodes = True
        mat.blend_method = 'HASHED'
        mat_bsdf = next(filter(lambda e: e.type == 'BSDF_PRINCIPLED', mat.node_tree.nodes), None)
        mat_texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
        mat.node_tree.links.new(mat_bsdf.inputs['Base Color'], mat_texture.outputs['Color'])
        mat.node_tree.links.new(mat_bsdf.inputs['Alpha'], mat_texture.outputs['Alpha'])

        if image is not None:
            mat_texture.image = image

        # creating mesh and objects
        msh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new(name, msh)
        msh.materials.append(mat)
        scene.collection.objects.link(obj)

        msh.from_pydata(self.ns.vertices, [], self.ns.faces)

        uv_map = msh.uv_layers.new(name='uvmap')

        for index, loop in enumerate(msh.loops):
            uv_map.data[loop.index].uv = self.ns.uvs[index]

        return obj

    @staticmethod
    def read(filename) -> MshFile:
        data = MshNs()
        data.read(filename)
        skl = MshFile()
        skl.ns = data
        return skl

    @staticmethod
    def write(obj: bpy.types.Object, filename: str, bake_texture_path: str = None) -> None:
        data = MshNs()
        assert isinstance(obj.data, bpy.types.Mesh)

        orig_mesh = obj.data

        dup_mesh = obj.data.copy()
        dup_mesh.name = "temp"
        obj.data = dup_mesh

        bm = bmesh.new()
        deps_graph = bpy.context.evaluated_depsgraph_get()
        bm.from_object(obj, deps_graph)
        bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts[:])
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        bm.to_mesh(dup_mesh)

        if bake_texture_path is not None:
            bake_texture(obj, bake_texture_path)
        obj.data = orig_mesh

        bpy.data.meshes.remove(dup_mesh)

        vertex_map: dict[int, int] = {}
        for index, vertex in enumerate(bm.verts):
            vertex_map[vertex.index] = index
            data.vertices.append(Vector(vertex.co))

        uv_layer = bm.loops.layers.uv.verify()
        for face in bm.faces:
            face: BMFace = face
            data.faces.append(tuple[int, int, int]([vertex_map[vert.index] for vert in face.verts]))

            for loop in face.loops:
                data.uvs.append(loop[uv_layer].uv)

        data.write(filename)
