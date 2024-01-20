from __future__ import annotations

from dataclasses import dataclass
from os import path
from pathlib import Path
from ..bake import bake_texture

import bpy
from ..helpers import save_mat_texture

from .SklFile import SklFile
from .AnmFile import AnmFile

class ChrFile:
    model: str = ""
    texture: str = ""

    def create(self, directory: str, load_at_0z: bool):
        # TODO: error handling
        image = bpy.data.images.load(path.join(directory, self.texture))
        skl = SklFile.read(path.join(directory, self.model))
        if load_at_0z:
            skl.moveTo0z()
        return skl.create(Path(self.model).stem, (0, 0, 0), image)

    def createSimplified(self, anm, directory: str, load_at_0z: bool):
        # TODO: error handling
        image = bpy.data.images.load(path.join(directory, self.texture))
        skl = SklFile.read(path.join(directory, self.model))
        skl.simplify(anm)
        if load_at_0z:
            skl.moveTo0z()
        return skl.create(Path(self.model).stem, (0, 0, 0), image)

    def __init__(self, model: str, texture: str) -> None:
        self.model = model
        self.texture = texture
        pass
        
    @staticmethod
    def __decode(data: bytes) -> str:
        str = data.decode("utf-8")
        if '\x00' in str:
            str = str[:str.index('\x00')]
        return str

    @staticmethod
    def read(filename: str) -> ChrFile:
        with open(filename, 'rb') as file:
            model = ChrFile.__decode(file.read(32))
            texture = ChrFile.__decode(file.read(32))
            
            return ChrFile(model, texture)
        
    def isComplex(self, directory: str):
        skl = SklFile.read(path.join(directory, self.model))
        return skl.isComplex()


    @staticmethod
    def write(filename: str, object: bpy.types.Object, texture_name: str, bake: bool = True):
        name = Path(filename).stem
        base_dir = path.dirname(filename)

        texture_name = texture_name.strip()
        if texture_name != "" and not texture_name.endswith(".jpg"):
            texture_name = texture_name + ".jpg"

        chr = ChrFile(name + ".skl", texture_name if texture_name != "" else (name + ".jpg"))

        mesh = object.children[0]

        if bake:
            bake_texture(mesh, path.join(base_dir, chr.texture))
        else:
            found = False
            if len(mesh.data.materials) > 0:
                found = save_mat_texture(mesh.data.materials[0], path.join(base_dir, chr.texture))

            if not found:
                raise Exception("Cannot find texture for mesh " + mesh.name)
        
        SklFile.write(object, path.join(base_dir, chr.model))

        with open(filename, 'wb') as file:
            file.write(chr.model.encode("utf-8")[:31])
            file.write(b'\0' * (32 - min(31, len(chr.model))))
            file.write(chr.texture.encode("utf-8")[:31])
            file.write(b'\0' * (32 - min(31, len(chr.texture))))