from __future__ import annotations

import re
from dataclasses import dataclass
from os import path

import bpy
from ..settings.BakeSettings import BakeSettings
from ..helpers import save_mat_texture

from .MshFile import MshFile


@dataclass
class CgoMesh:
    model: str = ""
    texture: str = ""


class CgoFile:
    meshes: list[CgoMesh]
    directory: str

    def __init__(self, meshes: list[CgoMesh], directory: str) -> None:
        self.meshes = meshes
        self.directory = directory
        pass

    def create(self):
        for index, mesh in enumerate(self.meshes):
            texture = None
            if mesh.texture is not None:
                print(mesh.texture)
                texture = bpy.data.images.load(path.join(self.directory, mesh.texture))

            msh = MshFile.read(path.join(self.directory, mesh.model))
            msh.create(texture, f"mesh{index}")

    @staticmethod
    def read(filename: str) -> CgoFile:
        with open(filename, 'r') as file:
            data = file.read()
            match = re.search(r"nummeshes=(\d+)", data)
            assert match

            num_meshes = int(match[1])
            meshes: list[CgoMesh] = []

            for index in range(num_meshes):
                mesh = re.search(rf"^mesh{index}=(.*)$", data, flags=re.MULTILINE)[1]
                texture = None
                texture_match = re.search(rf"^texture{index}=(.*)$", data, flags=re.MULTILINE)
                if texture_match:
                    texture = texture_match[1]

                meshes.append(CgoMesh(mesh, texture))

            return CgoFile(meshes, path.dirname(filename))

    @staticmethod
    def write(filename: str, objects: list[bpy.types.Object], bake_settings: BakeSettings) -> None:
        meshes: list[bpy.types.Object] = list(filter(lambda e: isinstance(e.data, bpy.types.Mesh), objects))

        if len(meshes) == 0:
            raise Exception("No available meshes found")

        base_dir = path.dirname(filename)
        name = path.splitext(path.basename(filename))[0]

        lines = [
            "[meshes]",
            "",
            f"nummeshes={len(meshes)}",
            ""
        ]

        for index, mesh in enumerate(meshes):
            mesh_path = f"{name}{index}.msh"
            texture_path = f"{name}{index}.jpg"

            if bake_settings.bake_materials:
                MshFile.write(mesh, path.join(base_dir, mesh_path), path.join(base_dir, texture_path))
            else:
                MshFile.write(mesh, path.join(base_dir, mesh_path))
                assert isinstance(mesh.data, bpy.types.Mesh)

                found = False
                
                if len(mesh.data.materials) > 0:
                    found = save_mat_texture(mesh.data.materials[0], path.join(base_dir, texture_path))

                if not found:
                    raise Exception("Cannot find texture for mesh " + mesh.name)

            lines.append(f"mesh{index}={mesh_path}")
            if texture_path is not None:
                lines.append(f"texture{index}={texture_path}")

        lines.append("[bounds]")
        lines.append("")
        lines.append("numbounds=0")

        with open(filename, 'w') as file:
            file.writelines([line + "\n" for line in lines])
