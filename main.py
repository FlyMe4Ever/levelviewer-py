import xml.etree.ElementTree as ET
import pygame


#random colors
# to do : make the textures
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

def process_layer(layer, map_w, map_h):
    layer_w = float(layer.attrib.get("Width", map_w))
    layer_h = float(layer.attrib.get("Height", map_h))
    scale_x = map_w / layer_w
    scale_y = map_h / layer_h
    layer_entry = {"name": layer.attrib.get("Name", "unknown"), "objects": []}
    for obj in layer.findall('Obj'):
        objct = {}
        objct["x"] = float(obj.attrib.get("x", obj.attrib.get("X", 0))) * scale_x
        objct["y"] = float(obj.attrib.get("y", obj.attrib.get("Y", 0))) * scale_y
        objct["depth"] = float(obj.attrib.get("depth", obj.attrib.get("Depth", 0)))
        layer_entry["objects"].append(objct)
    return layer_entry

# this is our level

tree = ET.parse('../level/Level_001')

root = tree.getroot()

x = float(root.attrib['Width'])
y = float(root.attrib['Height'])

pygame.init()
screen = pygame.display.set_mode((x, y))
clock = pygame.time.Clock()


all_layers = []
for layer_elem in root.findall('.//Layer'):
	layer_entry = process_layer(layer_elem, x, y)
	all_layers.append(layer_entry)
	
print(all_layers) 

#pygame loop so the game is always open until you close
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for layer_entry in all_layers:
        color = layer_colors.get(layer_entry["name"], (200, 200, 200))
        for obj in layer_entry["objects"]:
            x = int(obj["x"])
            y = int(obj["y"])
            pygame.draw.rect(screen, color, (x, y, 16, 16))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()