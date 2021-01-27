import pygame
import os
import sys
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
weight = 1000
height = 700
screen_size = (weight, height)
screen = pygame.display.set_mode(screen_size)
FPS = 60
screen_rect = (50, 50, 800, 800)

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('empty.png'),
    'exit': load_image('exit.png'),
    'Spikes_left': pygame.transform.flip(load_image('Spikes_right_left.png'), True, False),
    'Spikes_right': load_image('Spikes_right_left.png'),
    'Spikes_up': pygame.transform.flip(load_image('Spikes_down_up.png'), False, True),
    'Spikes_down': load_image('Spikes_down_up.png')
}
player_image = load_image('main.png')
player_image2 = load_image('main2.png')

tile_width = tile_height = 50


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy):
        images = ['Red', 'Orange', 'Yellow', 'Green', 'Blue',
                  'Dark_blue', 'Purple', 'White']
        fire = [load_image(str(random.choice(images) + random.choice(['_star.png',
                                                                      '_circle.png', '_dot.png'])), -1)]
        for scale in (5, 10, 20):
            fire.append(pygame.transform.scale(fire[0], (scale, scale)))
        super().__init__(coin_sprites)
        self.image = random.choice(fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position, particle_count):
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle((position[0] + 15, position[1] + 15), random.choice(numbers), random.choice(numbers))


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.coins = 0
        self.levels = 0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.rotation = 'up'
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(
            tile_width * self.pos[0] + 15, tile_height * self.pos[1] + 5)
        sprite_group.draw(screen)
        sprite_group.update()
        hero_group.draw(screen)
        hero.update()
        coin_sprites.draw(screen)
        coin_sprites.update()
        coin_group.draw(screen)
        coin_group.update()
        pygame.display.flip()
        clock.tick(16)

    def move1(self, movement):
        x, y = hero.pos
        if movement == "up":
            for coin in coin_sprites:
                coin.kill()
            self.image = player_image
            if y > 0 and level_map[y - 1][x] != "#":
                hero.move(x, y - 1)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.move1(hero, "up")
        elif movement == "down":
            self.image = player_image
            self.image = pygame.transform.flip(self.image, False, True)
            if y < max_y - 1 and level_map[y + 1][x] != "#":
                hero.move(x, y + 1)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.move1(hero, "down")
        elif movement == "left":
            self.image = player_image2
            self.image = pygame.transform.flip(self.image, True, False)
            if x > 0 and level_map[y][x - 1] != "#":
                hero.move(x - 1, y)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.move1(hero, "left")
        elif movement == "right":
            self.image = player_image2
            if x < max_x and level_map[y][x + 1] != "#":
                hero.move(x + 1, y)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.move1(hero, "right")
        elif movement == "space":
            self.image = player_image
            if self.coins == coins and level_map[y][x] == 'x':
                self.levels += 1
                print('Level', self.levels, 'completed!')
                pygame.mixer.Sound.play(victory_sound)
                if self.levels == 1:
                    hero.move(x - 7, y + 4)
            elif self.coins < coins and level_map[y][x] == 'x':
                print('Not enough')
            else:
                print('ERROR')
                terminate()

    def balance(self):
        print(self.coins)

    def update(self):
        if level_map[hero.pos[1]][hero.pos[0]] in ['R', 'L', 'U', 'D']:
            print("YOU DIED!")
            terminate()
        if pygame.sprite.spritecollide(self, coin_group, True):
            self.coins += 1
            pygame.mixer.Sound.play(coin_sound)
            create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 40)


def get_coins(n):
    filename = 'data/map.map'
    with open(filename, 'r') as mapFile:
        coins = 0
        lines = []
        for line in mapFile:
            lines.append(line)
        for line in lines[0:n]:
            coins += line.count('$')
    return coins


def level_line_counter():
    filename = 'data/map.map'
    lines = []
    indexes = []
    with open(filename, 'r') as mapFile:
        for line in mapFile:
            lines.append(line)
    for line in lines:
        if '|' in line:
            indexes.append(lines.index(line))
    return indexes


class Coin(pygame.sprite.Sprite):
    image = load_image("Coin.png")

    def __init__(self, x, y, group, sheet, col, row):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.x = x * 50 + 10
        self.rect.y = y * 50 + 10
        self.frames = []
        self.cut_sheet(sheet, col, row)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


player = None
running = True
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
coin_group = SpriteGroup()
coin_sprites = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Pixel escape", "",
                  "",
                  "Dungeon 1"]

    fon = pygame.transform.scale(load_image('fon.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('green'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = []
        for line in mapFile:
            level_map.append(line.strip())
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'L':
                Tile('Spikes_left', x, y)
            elif level[y][x] == 'R':
                Tile('Spikes_right', x, y)
            elif level[y][x] == 'U':
                Tile('Spikes_up', x, y)
            elif level[y][x] == 'D':
                Tile('Spikes_down', x, y)
            elif level[y][x] == 'x':
                Tile('exit', x, y)
            elif level[y][x] == '$':
                Coin(x * tile_width + 12, y * tile_height + 12, coin_group, load_image('Coin_sheet.png'), 8, 1)
                Tile('empty', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


coin_sound = pygame.mixer.Sound('data/Coin.mp3')
leap_sound = pygame.mixer.Sound('data/Leap.mp3')
victory_sound = pygame.mixer.Sound('data/Victory.mp3')
start_screen()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
level_indexes = level_line_counter()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                pygame.mixer.Sound.play(leap_sound)
                Player.move1(hero, "up")
                for coin in coin_sprites:
                    coin.kill()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                pygame.mixer.Sound.play(leap_sound)
                Player.move1(hero, "down")
                for coin in coin_sprites:
                    coin.kill()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                pygame.mixer.Sound.play(leap_sound)
                Player.move1(hero, "left")
                for coin in coin_sprites:
                    coin.kill()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                pygame.mixer.Sound.play(leap_sound)
                Player.move1(hero, "right")
                for coin in coin_sprites:
                    coin.kill()
            elif event.key == pygame.K_c:
                Player.balance(hero)
            elif event.key == pygame.K_SPACE:
                Player.move1(hero, "space")
    screen.fill(pygame.Color("black"))
    coin_group.draw(screen)
    hero.move(hero.pos[0], hero.pos[1])
    sprite_group.draw(screen)
    hero_group.draw(screen)
    coin_group.draw(screen)
    pygame.display.flip()
    for coin in coin_sprites:
        coin.kill()
    if hero.levels == len(level_indexes):
        pygame.time.delay(1800)
        terminate()
    coins = get_coins(int(level_indexes[hero.levels]) - 1)
pygame.quit()
