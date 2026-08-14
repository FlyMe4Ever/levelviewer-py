import os
import glob
import xml.etree.ElementTree as ET
import pygame

from atlasmanager import AtlasManager


#sprite atlas and png file dir
XML_DIR = "new/"
PNG_DIR = "new/"


#random (fallback) colors
layer_colors = {
    "Background": (100, 100, 100),
    "Farground": (255, 255, 255),
    "StaticObject":  (255, 0, 0),
    "Texture":(0, 100, 100),
    "DynamicObject":(100, 0, 100),
    "Item":(100, 100, 0),
    "Foreground":(100, 200, 100),
    "Closeground":(200, 0, 100)
}

def get_layer(root, name):
    return root.find(f".//Layer[@Name='{name}']")

def process_layer(layer, map_w, map_h, prefix_id, atlas_mgr):
    layer_w = float(layer.attrib.get("Width", map_w))
    layer_h = float(layer.attrib.get("Height", map_h))
    scale_x = map_w / layer_w
    scale_y = map_h / layer_h
    layer_name = layer.attrib.get("Name", "unknown")
    layer_entry = {"name": layer_name, "objects": []}

    objs = sorted(layer.findall('Obj'),
                  key=lambda o: float(o.attrib.get("Depth", 0)))

    for obj in objs:
        objct = {}
        objct["x"] = float(obj.attrib.get("x", obj.attrib.get("X", 0))) * scale_x
        objct["y"] = map_h - float(obj.attrib.get("y", obj.attrib.get("Y", 0))) * scale_y
        objct["depth"] = float(obj.attrib.get("depth", obj.attrib.get("Depth", 0)))
        objct["rotation"] = float(obj.attrib.get("rotation", obj.attrib.get("Rotation", 0)))
        objct["flip_x"] = obj.attrib.get("IsXFlipped", "false") == "true"

        sprite = None
        seq_id_raw = obj.attrib.get("SeqID")
        if seq_id_raw is not None:
            try:
                seq_id = int(seq_id_raw)    
                sprite = atlas_mgr.get_sprite(prefix_id, seq_id, layer_name)
            except ValueError:
                pass

        if sprite is not None :
            if objct["flip_x"]:
                sprite = pygame.transform.flip(sprite, True, False)
            if objct["rotation"] != 0:
                sprite = pygame.transform.rotate(sprite, -objct["rotation"])
            if scale_x != 1 or scale_y != 1:
                new_size = (max(1, int(sprite.get_width() * scale_x)), max(1, int(sprite.get_height() * scale_y)))
                sprite = pygame.transform.smoothscale(sprite, new_size)


        objct["seq_id"] = seq_id_raw
        objct["sprite"] = sprite
        layer_entry["objects"].append(objct)

    return layer_entry

# this is our level

tree = ET.parse('../level/Level_001')
root = tree.getroot()

suite_el = root.find('./Header/Suite')
suite_id = suite_el.attrib.get('ID') if suite_el is not None else None

map_w = float(root.attrib['Width'])
map_h = float(root.attrib['Height'])

DISPLAY_SCALE = 0.5   # the scale of the window so we can see the entire map on the screen

window_w = int(map_w * DISPLAY_SCALE)
window_h = int(map_h * DISPLAY_SCALE)

screen = pygame.display.set_mode((window_w, window_h))   # real small window
render_surface = pygame.Surface((map_w, map_h))           # original full size content

pygame.init()
clock = pygame.time.Clock()


atlas_mgr = AtlasManager(XML_DIR, PNG_DIR)

all_layers = []
for layer_elem in root.findall('.//Layer'):
    layer_entry = process_layer(layer_elem, map_w, map_h, suite_id, atlas_mgr)
    all_layers.append(layer_entry)


missing = sum(1 for l in all_layers for o in l["objects"] if o["sprite"] is None)
total = sum(len(l["objects"]) for l in all_layers)
print(f"good sprites: {total - missing}/{total} ({missing} is missing)")

print(all_layers) 


for l in all_layers:
    for o in l["objects"]:
        if o["sprite"] is None:
            print(f"  unknown: layer={l['name']!r} seq_id={o.get('seq_id')} "
                  f"x={o['x']:.1f} y={o['y']:.1f}")


# pygame loop so the game is always open until you close
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    render_surface.fill((0, 0, 0))

    for layer_entry in all_layers:
        color = layer_colors.get(layer_entry["name"], (200, 200, 200))
        for obj in layer_entry["objects"]:
            x, y = int(obj["x"]), int(obj["y"])
            sprite = obj["sprite"]
            if sprite is not None:

                # X/Y is the sprite center, like cocos 2d
                rect = sprite.get_rect(center=(x, y))
                render_surface.blit(sprite, rect)
            else:
                pygame.draw.rect(render_surface, color, (x, y, 16, 16))

    # scale down to fit the window
    scaled = pygame.transform.smoothscale(render_surface, (window_w, window_h))
    screen.blit(scaled, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()