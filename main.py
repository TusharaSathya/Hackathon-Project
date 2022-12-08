import pygame
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

def paint_interface(screen):
  interface_surface = pygame.Surface((INTERFACE_WIDTH, DISPLAY_HEIGHT))
  interface_surface.fill((158, 227, 79))
  screen.blit(interface_surface, (DISPLAY_WIDTH, 0))
  
  color = (158, 227, 79)
  interface_x = DISPLAY_WIDTH
  interface_y = 0
  interface_width = INTERFACE_WIDTH
  interface_height = DISPLAY_HEIGHT
  pygame.draw.rect(screen, color, pygame.Rect(interface_x, interface_y, interface_width, interface_height))

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

pygame.init()

BASE_TILE_0 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'base_0.png')), (CELL_SIZE, CELL_SIZE))
BASE_TILE_1 = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'base_1.png')), (CELL_SIZE, CELL_SIZE))
USER_TILE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'user.png')), (CELL_SIZE, CELL_SIZE))
SERVER_TILE = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'server.png')), (CELL_SIZE, CELL_SIZE))

grid_width = DISPLAY_WIDTH//CELL_SIZE
grid_height = DISPLAY_HEIGHT//CELL_SIZE

grid = []
for i in range(grid_height):
  row = []
  for j in range(grid_width):
    row.append('EMPTY')
  grid.append(row)

player_x = grid_width//2
player_y = grid_height//2
grid[player_y][player_x] = 'PLAYER'

servers = []
for i in range(4):
  server_location = insert_server(grid)
  server_information = { 
    'CPU Utilization': random.randint(20, 80000)/100, 
    'Throughput': random.randint(100,1000)/100, 
    'Status': bool(random.randint(0, 1)),
    'Latency': 5 * ((server_location[0] - player_x) ** 2 + (server_location[1] - player_y) ** 2) ** (1/2)
  }

  server_info = {}
  server_info['info'] = server_information
  server_info['location'] = server_location

  servers.append(server_info)

for i in range(grid_height*grid_width//8):
  insert_grass(grid)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Load Balancing')

running = True
while running:

  events = pygame.event.get()

  for event in events:

    if event.type == pygame.QUIT:
      running = False

  paint_display(screen, grid, servers)
  paint_interface(screen)
  pygame.display.flip()

  # change this for framerate
  pygame.time.delay(100)

pygame.quit()