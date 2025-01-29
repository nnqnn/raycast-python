import pygame
import math

# Инициализация Pygame
pygame.init()

# Параметры экрана
WIDTH, HEIGHT = 800, 600
FOV = math.pi / 3  # Поле зрения (60 градусов)
NUM_RAYS = 200  # Количество лучей (больше = сглаженные стены)
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS
TILE = 100  # Размер одной ячейки карты
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D")
clock = pygame.time.Clock()

# Карта лабиринта
MAP = [
    "########",
    "#......#",
    "#.####.#",
    "#.#..#.#",
    "#.#..#.#",
    "#.#..#.#",
    "#....#E#",
    "########",
]

MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)

# Игрок
player_pos = [150, 150]
player_angle = 0
player_speed = 3

def cast_ray(x, y, angle):
    """Кастует один луч и находит точку пересечения со стеной"""
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)

    # Вертикальные пересечения
    if cos_a > 0:
        x_vert = (x // TILE) * TILE + TILE
        dx = TILE
    else:
        x_vert = (x // TILE) * TILE - 0.0001
        dx = -TILE

    depth_vert = float('inf')
    y_vert = y + (x_vert - x) * (sin_a / cos_a)

    while 0 <= int(y_vert // TILE) < MAP_HEIGHT and 0 <= int(x_vert // TILE) < MAP_WIDTH:
        if MAP[int(y_vert // TILE)][int(x_vert // TILE)] == "#":
            depth_vert = (x_vert - x) / cos_a
            break
        x_vert += dx
        y_vert += dx * (sin_a / cos_a)

    # Горизонтальные пересечения
    if sin_a > 0:
        y_hor = (y // TILE) * TILE + TILE
        dy = TILE
    else:
        y_hor = (y // TILE) * TILE - 0.0001
        dy = -TILE

    depth_hor = float('inf')
    x_hor = x + (y_hor - y) * (cos_a / sin_a)

    while 0 <= int(y_hor // TILE) < MAP_HEIGHT and 0 <= int(x_hor // TILE) < MAP_WIDTH:
        if MAP[int(y_hor // TILE)][int(x_hor // TILE)] == "#":
            depth_hor = (y_hor - y) / sin_a
            break
        y_hor += dy
        x_hor += dy * (cos_a / sin_a)

    return min(depth_vert, depth_hor)

def cast_rays():
    """Рендеринг 3D сцены"""
    x, y = player_pos
    angle = player_angle - FOV / 2

    for ray in range(NUM_RAYS):
        depth = cast_ray(x, y, angle)
        depth *= math.cos(player_angle - angle)  # Исправление перспективы
        wall_height = min(HEIGHT, TILE * 500 / (depth + 0.0001))
        color_intensity = 255 / (1 + depth * depth * 0.00002)
        color = (color_intensity, color_intensity // 1.2, color_intensity // 1.5)
        pygame.draw.rect(screen, color, (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))
        angle += DELTA_ANGLE

def check_collision(new_x, new_y):
    col, row = int(new_x // TILE), int(new_y // TILE)
    return MAP[row][col] == "#"

def move_player():
    """Обновление позиции игрока"""
    global player_pos, player_angle
    x, y = player_pos
    sin_a = math.sin(player_angle)
    cos_a = math.cos(player_angle)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        new_x = x + player_speed * cos_a
        new_y = y + player_speed * sin_a
        if not check_collision(new_x, y):
            player_pos[0] = new_x
        if not check_collision(x, new_y):
            player_pos[1] = new_y
    if keys[pygame.K_s]:
        new_x = x - player_speed * cos_a
        new_y = y - player_speed * sin_a
        if not check_collision(new_x, y):
            player_pos[0] = new_x
        if not check_collision(x, new_y):
            player_pos[1] = new_y
    if keys[pygame.K_a]:
        player_angle -= 0.05
    if keys[pygame.K_d]:
        player_angle += 0.05

def check_win():
    """Проверка достижения выхода."""
    x, y = player_pos
    col, row = int(x // TILE), int(y // TILE)
    return MAP[row][col] == "E"

# Основной игровой цикл
running = True
win = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    if not win:
        move_player()
        cast_rays()
        win = check_win()
    else:
        font = pygame.font.Font(None, 74)
        text = font.render("You Win!", True, GREEN)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
