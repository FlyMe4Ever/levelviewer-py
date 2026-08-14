import os
import glob
import xml.etree.ElementTree as ET
import pygame

# this is the function that handle the management of the sprite atlas:  parsing,splitting, caching and extracting 

class AtlasManager:

    def __init__(self, xml_dir, png_dir):
        self.png_dir = png_dir
        self.atlases = {}
        self._sprite_cache = {}

        for xml_path in sorted(glob.glob(os.path.join(xml_dir, "*.xml"))):
            atlas_name = os.path.splitext(os.path.basename(xml_path))[0]
            atlas_root = ET.parse(xml_path).getroot()
            texture_path = os.path.join(png_dir, atlas_root.attrib["Texture"])
            if not os.path.isfile(texture_path):
                print(f"warning: atlas {atlas_name} wants texture "
                      f"{atlas_root.attrib['Texture']}, not found in {texture_path}")
                continue

            surface = pygame.image.load(texture_path).convert_alpha()
            frames = {}  # for animated
            for frame in atlas_root.findall("Frame"):
                prefix = frame.attrib.get("Prefix")
                seq_id = frame.attrib.get("SeqID")
                if prefix is not None and seq_id is not None:
                    frames[(prefix, int(seq_id))] = frame.attrib
            self.atlases[atlas_name] = {"surface": surface, "frames": frames}

        print(f"loaded {len(self.atlases)}")

    def get_sprite(self, prefix_id, seq_id, layer_name=None):
        cache_key = (prefix_id, seq_id, layer_name)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        names = list(self.atlases)
        if prefix_id is not None:
            suffix = f"S{prefix_id}"
            names.sort(key=lambda n: 0 if n.endswith(suffix) else 1)

        sprite = None
        for atlas_name in names:
            atlas = self.atlases[atlas_name]
            key = (layer_name if layer_name else prefix_id, seq_id)
            frame = atlas["frames"].get(key)
            if frame is not None:
                sprite = self._extract(atlas["surface"], frame)
                break

        self._sprite_cache[cache_key] = sprite
        return sprite

    @staticmethod
    def _extract(atlas_surface, frame):
        x, y = int(frame["X"]), int(frame["Y"])
        w, h = int(frame["W"]), int(frame["H"])
        offx, offy = float(frame["OffX"]), float(frame["OffY"])
        srcw, srch = int(frame["SrcW"]), int(frame["SrcH"])
        rotated = frame["Rotated"] == "true"

        if rotated:
            piece = atlas_surface.subsurface(pygame.Rect(x, y, h, w)).copy()
            piece = pygame.transform.rotate(piece, 90)
        else:
            piece = atlas_surface.subsurface(pygame.Rect(x, y, w, h)).copy()

        canvas = pygame.Surface((srcw, srch), pygame.SRCALPHA)
        paste_x = int(srcw / 2 + offx - piece.get_width() / 2)
        paste_y = int(srch / 2 - offy - piece.get_height() / 2)
        canvas.blit(piece, (paste_x, paste_y))
        return canvas