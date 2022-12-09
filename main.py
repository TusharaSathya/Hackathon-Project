import pygame_widgets
import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import os
import random
from functools import cache

CELL_SIZE = 80
DISPLAY_WIDTH = CELL_SIZE * 9
DISPLAY_HEIGHT = CELL_SIZE * 9

INTERFACE_WIDTH = 200

WINDOW_WIDTH = DISPLAY_WIDTH + INTERFACE_WIDTH
WINDOW_HEIGHT = DISPLAY_HEIGHT

assert DISPLAY_WIDTH % CELL_SIZE == 0, "WINDOW_WIDTH not multiple of CELL_SIZE"
assert DISPLAY_HEIGHT % CELL_SIZE == 0, "WINDOW_HEIGHT not multiple of CELL_SIZE"

@cache
def get_font_size(no_characters, width_constraint, height_constraint):
  text_width = float('inf')
  text_height = float('inf')
  font_size = 100
  while text_width > width_constraint or text_height > height_constraint:
    font = pygame.font.SysFont('arial', font_size)
    text = font.render('T' * no_characters, True, (0, 0, 0))
    text_width = text.get_rect().width
    text_height = text.get_rect().height
    font_size -= 1
  return font_size

def get_text(input_text, width_constraint, height_constraint, color):
  font_size = get_font_size(len(input_text), width_constraint, height_constraint)
  font = pygame.font.SysFont('arial', font_size)
  text = font.render(input_text, True, color)
  return text

def paint_display(screen, grid, servers):

  grid_height = len(grid)
  grid_width = len(grid[0]) if grid else 0

  for row_no in range(grid_width):
    for col_no in range(grid_height):
      cell_x = col_no * CELL_SIZE
      cell_y = row_no * CELL_SIZE

      if grid[row_no][col_no] == 'GRASS':
        screen.blit(BASE_TILE_1, (cell_x, cell_y))
      else:
        screen.blit(BASE_TILE_0, (cell_x, cell_y))

  for row_no in range(grid_width):
    for col_no in range(grid_height):
      cell_x = col_no * CELL_SIZE
      cell_y = row_no * CELL_SIZE

      type = grid[row_no][col_no]

      if type == 'PLAYER':
        screen.blit(USER_TILE, (cell_x, cell_y))

  for server in servers:
    col_no = server['location'][0]
    row_no = server['location'][1]
    cell_x = col_no * CELL_SIZE
    cell_y = row_no * CELL_SIZE
    screen.blit(SERVER_TILE, (cell_x, cell_y))

    if server['info']['Status']:
      text = get_text('Online', CELL_SIZE, float('inf'), (0, 255, 0))
    else:
      text = get_text('Offline', CELL_SIZE, float('inf'), (255, 0, 0))
    screen.blit(text, (cell_x + (CELL_SIZE - text.get_rect().width)//2, cell_y + (CELL_SIZE//6 - text.get_rect().height)//2))

    server_info_tile = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA, 32)
    server_info_tile = server_info_tile.convert_alpha()
    cell_x += CELL_SIZE

    text = get_text('CPU', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, 0 + (CELL_SIZE//6 - text.get_rect().height)//2))

    text = get_text(str(round(server['info']['CPU Utilization'], 2)) + '%' if server['info']['Status'] else '--', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, CELL_SIZE//6 + (CELL_SIZE//6 - text.get_rect().height)//2))

    text = get_text('Throughput', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, 2*CELL_SIZE//6 + (CELL_SIZE//6 - text.get_rect().height)//2))

    text = get_text(str(round(server['info']['Throughput'], 2)) if server['info']['Status'] else '--', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, 3*CELL_SIZE//6 + (CELL_SIZE//6 - text.get_rect().height)//2))

    text = get_text('Latency', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, 4*CELL_SIZE//6 + (CELL_SIZE//6 - text.get_rect().height)//2))

    text = get_text(str(round(server['info']['Latency'], 2)) + ' ms' if server['info']['Status'] else '--', CELL_SIZE, CELL_SIZE//6, (255, 255, 255))
    server_info_tile.blit(text, ((CELL_SIZE - text.get_rect().width)//2, 5*CELL_SIZE//6 + (CELL_SIZE//6 - text.get_rect().height)//2))

    screen.blit(server_info_tile, pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE))

    if is_connected:
      sorted_servers = sorted(servers, key=lambda x: x['info']['Score'], reverse=True)
      for server in sorted_servers:
        if server['info']['Status']:
          pygame.draw.line(screen, (0, 255, 0), (player_x * CELL_SIZE + CELL_SIZE//2, player_y * CELL_SIZE + CELL_SIZE//2), (server['location'][0] * CELL_SIZE + CELL_SIZE//2, server['location'][1] * CELL_SIZE + CELL_SIZE//2), 10)
          break

def paint_interface(screen, connect_pos, rebuild_pos):
  interface_surface = pygame.Surface((INTERFACE_WIDTH, DISPLAY_HEIGHT))
  interface_surface.fill((158, 227, 79))

  interface_surface.blit(BUTTON_CONNECT_TO_SERVER, connect_pos)
  interface_surface.blit(BUTTON_REBUILD_MAP, rebuild_pos)

  screen.blit(interface_surface, (DISPLAY_WIDTH, 0))
  
def insert_server(grid):
  grid_height = len(grid)
  grid_width = len(grid[0]) if grid else 0

  invalid_coords = []

  for row_no in range(grid_height):
    for col_no in range(grid_width):

      type = grid[row_no][col_no]
      if type == 'PLAYER' or type == 'SERVER':
        invalid_coords.append((col_no, row_no))
        
  server_x = random.randint(0, grid_width - 1) 
  server_y = random.randint(0, grid_height - 1)

  def is_valid_insertion_coord(grid, invalid_coords, server_coord):
    if server_coord[0] == grid_width - 1:
      return False
    for coord in invalid_coords:
      if (server_coord == coord or server_coord == (coord[0] - 1, coord[1]) 
          or server_coord == (coord[0] + 1, coord[1]) or server_coord == (coord[0], coord[1] - 1) 
          or server_coord == (coord[0], coord[1] + 1)):
        return False
    return True

  while not is_valid_insertion_coord(grid, invalid_coords, (server_x, server_y)):

    server_x = random.randint(0, grid_width - 1) 
    server_y = random.randint(0, grid_height - 1)

  grid[server_y][server_x] = 'SERVER'

  return (server_x, server_y)

def insert_grass(grid):
  grid_height = len(grid)
  grid_width = len(grid[0]) if grid else 0

  invalid_coords = []

  for row_no in range(grid_height):
    for col_no in range(grid_width):

      type = grid[row_no][col_no]
      if type == 'PLAYER' or type == 'SERVER' or type == 'GRASS':
        invalid_coords.append((col_no, row_no))
        
  server_x = random.randint(0, grid_width - 1) 
  server_y = random.randint(0, grid_height - 1)

  def is_valid_insertion_coord(grid, invalid_coords, server_coord):
    if server_coord[0] == grid_width - 1:
      return False
    for coord in invalid_coords:
      if (server_coord == coord or server_coord == (coord[0] - 1, coord[1]) 
          or server_coord == (coord[0] + 1, coord[1]) or server_coord == (coord[0], coord[1] - 1) 
          or server_coord == (coord[0], coord[1] + 1)):
        return False
    return True

  while not is_valid_insertion_coord(grid, invalid_coords, (server_x, server_y)):

    server_x = random.randint(0, grid_width - 1) 
    server_y = random.randint(0, grid_height - 1)

  grid[server_y][server_x] = 'GRASS'

def init_grid(no_servers):
  grid = []
  for i in range(grid_height):
    row = []
    for j in range(grid_width):
      row.append('EMPTY')
    grid.append(row)

  grid[player_y][player_x] = 'PLAYER'

  servers = []
  for i in range(no_servers):
    server_location = insert_server(grid)
    server_information = { 
      'CPU Utilization': random.randint(2000, 8000)/100, 
      'Throughput': random.randint(100,1000)/100, 
      'Status': bool(random.randint(0, 1)),
      'Latency': 5 * ((server_location[0] - player_x) ** 2 + (server_location[1] - player_y) ** 2) ** (1/2)
    }
    server_information['Score'] = - server_information['Latency']/20 - server_information['CPU Utilization']/80 + server_information['Throughput']/10

    server_info = {}
    server_info['info'] = server_information
    server_info['location'] = server_location

    servers.append(server_info)

  for i in range(grid_height*grid_width//8):
    insert_grass(grid)
  
  return grid, servers

pygame.init()

BASE_TILE_0 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'base_0.png')), (CELL_SIZE, CELL_SIZE))
BASE_TILE_1 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'base_1.png')), (CELL_SIZE, CELL_SIZE))
USER_TILE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'user.png')), (CELL_SIZE, CELL_SIZE))
SERVER_TILE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'server.png')), (CELL_SIZE, CELL_SIZE))

BUTTON_CONNECT_TO_SERVER_raw = pygame.image.load(os.path.join('assets', 'button_connect-to-server.png'))
padding = 10
new_width = INTERFACE_WIDTH - 2 * padding
old_width = BUTTON_CONNECT_TO_SERVER_raw.get_rect().width
old_height = BUTTON_CONNECT_TO_SERVER_raw.get_rect().height
factor = new_width / old_width
new_height = factor * old_height
BUTTON_CONNECT_TO_SERVER = pygame.transform.scale(BUTTON_CONNECT_TO_SERVER_raw, (new_width, new_height))

button_connect_pos = ((INTERFACE_WIDTH - new_width)//2, DISPLAY_HEIGHT//2 - new_height//2)
button_connect_rect = pygame.Rect(
  DISPLAY_WIDTH + button_connect_pos[0], 
  button_connect_pos[1],
  BUTTON_CONNECT_TO_SERVER.get_rect().width,
  BUTTON_CONNECT_TO_SERVER.get_rect().height
)

BUTTON_REBUILD_MAP_raw = pygame.image.load(os.path.join('assets', 'button_rebuild-map.png'))
padding = 10
old_width = BUTTON_REBUILD_MAP_raw.get_rect().width
old_height = BUTTON_REBUILD_MAP_raw.get_rect().height
new_height = new_height
factor = new_height / old_height
new_width = factor * old_width
BUTTON_REBUILD_MAP = pygame.transform.scale(BUTTON_REBUILD_MAP_raw, (new_width, new_height))

button_rebuild_pos = ((INTERFACE_WIDTH - new_width)//2, 20)
button_rebuild_rect = pygame.Rect(
  DISPLAY_WIDTH + button_rebuild_pos[0], 
  button_rebuild_pos[1],
  BUTTON_REBUILD_MAP.get_rect().width,
  BUTTON_REBUILD_MAP.get_rect().height
)

grid_width = DISPLAY_WIDTH//CELL_SIZE
grid_height = DISPLAY_HEIGHT//CELL_SIZE

player_x = grid_width//2
player_y = grid_height//2

min_servers = 0
max_servers = grid_width * grid_height // 10
current_no_servers = max_servers // 2

grid, servers = init_grid(current_no_servers)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Load Balancing')

padding = 15
new_width = INTERFACE_WIDTH - 2 * padding
new_y = button_connect_rect.y + button_connect_rect.height + padding
height = 15
slider = Slider(screen, DISPLAY_WIDTH + (INTERFACE_WIDTH - new_width)//2, new_y, new_width, height, min = min_servers, max = max_servers, step = 1)

padding = 5
new_y = new_y + height + 3 * padding
output = TextBox(screen, DISPLAY_WIDTH + padding, new_y, INTERFACE_WIDTH - 2 * padding, 40, fontSize=30)
output.disable()

is_connected = False
running = True
while running:

  events = pygame.event.get()

  for event in events:

    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.MOUSEBUTTONDOWN:
      pos = pygame.mouse.get_pos()
      if button_rebuild_rect.collidepoint(pos):
        grid, servers = init_grid(current_no_servers)
        is_connected = False
      if button_connect_rect.collidepoint(pos):
        is_connected = True

  paint_display(screen, grid, servers)
  paint_interface(screen, button_connect_pos, button_rebuild_pos)

  requested_no_servers = slider.getValue()
  output.setText(requested_no_servers)

  if requested_no_servers != current_no_servers:
    current_no_servers = requested_no_servers
    grid, servers = init_grid(current_no_servers)

  pygame_widgets.update(events)
  pygame.display.flip()

  # change this for framerate
  pygame.time.delay(100)

pygame.quit()