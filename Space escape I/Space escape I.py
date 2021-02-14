import pygame
import sys
import random
import os


def load_image(name, color_key=None):
    fullname = os.path.join('data/images', name)
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


def load_sound(name):
    fullname = os.path.join('data/Sounds', name)
    try:
        os.path.isfile(fullname)
    except Exception as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    return fullname


pygame.init()
weight = 1100
height = 800
screen_size = (weight, height)
screen = pygame.display.set_mode((1100, 750))
FPS = 60
screen_rect = (0, 0, weight, height)
pygame.display.set_icon(load_image('main.png'))
tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('empty.png'),
    'Exit_red': load_image('Exit_red.png'),
    'Exit_green': load_image('Exit_green.png'),
    'Exit_blue': load_image('Exit_blue.png'),
    'Exit_yellow': load_image('Exit_yellow.png'),
    'Red_teleport': load_image('Red_teleport.png'),
    'Green_teleport': load_image('Green_teleport.png'),
    'Blue_teleport': load_image('Blue_teleport.png'),
    'Spikes_left': pygame.transform.flip(load_image('Spikes_right_left.png'), True, False),
    'Spikes_right': load_image('Spikes_right_left.png'),
    'Middle': load_image('Middle.png'),
    'Line_up_down': load_image('Line_up_down.png'),
    'Line_left_right': load_image('Line_left_right.png'),
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
        super().__init__(particle_sprites)
        self.image = random.choice(fire)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.velocity = [dx, dy]

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


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.coins = 0
        self.levels = 0
        self.total_coins = 0
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 10)
        self.rotation = 'up'
        self.pos = (pos_x, pos_y)
        self.reloading = False

    def move(self, x, y):
        if not self.reloading:
            self.pos = (x, y)
            self.rect = self.image.get_rect().move(
                tile_width * self.pos[0] + 10, tile_height * self.pos[1] + 10)
            sprite_group.draw(screen)
            sprite_group.update()
            hero_group.draw(screen)
            hero.update()
            particle_sprites.draw(screen)
            particle_sprites.update()
            coin_group.draw(screen)
            coin_group.update()
            pygame.display.flip()
            clock.tick(15)

    def action(self, action):
        x, y = hero.pos
        if action == "up":
            self.image = player_image
            if y > 0 and level_map[y - 1][x] not in ["#", "R", "U", "L", "|", "-"]:
                hero.move(x, y - 1)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.action(hero, "up")
        elif action == "down":
            self.image = player_image
            self.image = pygame.transform.flip(self.image, False, True)
            if y < max_y - 1 and level_map[y + 1][x] not in ["#", "R", "L", "D", "|", "-"]:
                hero.move(x, y + 1)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.action(hero, "down")
        elif action == "left":
            self.image = player_image2
            self.image = pygame.transform.flip(self.image, True, False)
            if x > 0 and level_map[y][x - 1] not in ["#", "L", "U", "D", "|", "-"]:
                hero.move(x - 1, y)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.action(hero, "left")
        elif action == "right":
            self.image = player_image2
            if x < max_x and level_map[y][x + 1] not in ["#", "R", "U", "D", "|", "-"]:
                hero.move(x + 1, y)
                create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 8)
                Player.action(hero, "right")
        elif action == "space":
            self.image = player_image
            if self.coins == coins[self.levels] and level_map[y][x] == 'x' and hero.levels + 1 != len(coins):
                hero.pos = int(teleports[self.levels].split(',')[0]), int(teleports[self.levels].split(',')[1])
                self.levels += 1
                self.total_coins += self.coins
                self.coins = 0
                print('Level', self.levels, 'completed!', '[Location -', locations[location_number - 1] + ']')
                pygame.mixer.Sound.play(next_level_sound)
            elif self.coins < coins[self.levels] and level_map[y][x] == 'x':
                pygame.mixer.Sound.play(error_sound)
                print('Not enough')
            elif hero.levels + 1 == len(coins) and self.coins == coins[self.levels] and level_map[y][x] == 'x':
                self.total_coins += self.coins
                self.levels += 1
                print('Level', self.levels, 'completed!', '[Location -', locations[location_number - 1] + ']')

    def balance(self):
        print(self.total_coins)

    def update(self):
        if level_map[hero.pos[1]][hero.pos[0]] in ['R', 'L', 'U', 'D']:
            self.total_coins += self.coins
            print("YOU DIED!")
            print('You completed', self.levels + 1, 'level(s) and collected', self.total_coins, 'coin(s). Nice score!')
            game_over_screen()
        if pygame.sprite.spritecollide(self, coin_group, True):
            self.coins += 1
            pygame.mixer.Sound.play(coin_sound)
            create_particles((self.pos[0] * tile_width, self.pos[1] * tile_height), 40)


def get_coins(n, name):
    filename = 'data/Locations/' + name
    total_coins_list = []
    lines = location_map_returner(filename)
    coin_adder = 0
    for line in lines[0:n[0]]:
        coin_adder += line[0:line.index('|')].count('$')
    total_coins_list.append(coin_adder)
    coin_adder = 0
    for line in lines[0:n[0]]:
        coin_adder += line[line.index('|'):].count('$')
    total_coins_list.append(coin_adder)
    coin_adder = 0
    for line in lines[n[0]:n[1]]:
        coin_adder += line[line.index('|'):].count('$')
    total_coins_list.append(coin_adder)
    coin_adder = 0
    for line in lines[n[0]:n[1]]:
        coin_adder += line[0:line.index('|')].count('$')
    total_coins_list.append(coin_adder)
    return total_coins_list


class Coin(pygame.sprite.Sprite):
    image = load_image("Coin.png")

    def __init__(self, x, y, group, sheet, col, row):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_width + 10
        self.rect.y = y * tile_height + 10
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
particle_sprites = SpriteGroup()


def terminate():
    pygame.quit()
    print('Closing the game...')
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), screen_size)
    main = pygame.mixer.Channel(1)
    main.play(main_sound)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                pygame.display.set_mode(screen_size)
                main.stop()
                return
        if main.get_busy() == 0:
            main.play(main_sound)
        pygame.display.flip()
        clock.tick(FPS)


def main_menu():
    fon = pygame.transform.scale(load_image('main_menu.png'), screen_size)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = int(event.pos[0]), int(event.pos[1])
                if 251 <= x <= 867 and 317 <= y <= 457:
                    return
                elif 251 <= x <= 867 and 524 <= y <= 663:
                    terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print('You pressed "Q" to quit the game')
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen():
    pygame.mixer.stop()
    pygame.mixer.Sound.play(death_sound)
    pygame.display.set_caption('Space escape I, YOU DIED!')
    fon = pygame.transform.scale(load_image('lost.png'), screen_size)
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print('You pressed "Q" to quit the game')
                    terminate()
                elif event.key == pygame.K_r:
                    hero.pos = (0, 0)
                    screen.fill(pygame.Color("black"))
                    hero.reloading = True
                    return
        pygame.display.flip()
        clock.tick(FPS)


def next_level():
    global location_number
    pygame.mixer.stop()
    pygame.display.set_caption('Space escape I, changing location...')
    if location_number == len(locations):
        victory_screen()
        return
    fon = pygame.transform.scale(load_image('Next_level.png'), screen_size)
    screen.blit(fon, (0, 0))
    pygame.mixer.Sound.play(full_victory_sound)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print('You pressed "Q" to quit the game')
                    terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = int(event.pos[0]), int(event.pos[1])
                if 251 <= x <= 867 and 317 <= y <= 457:
                    location_number += 1
                    hero.reloading = True
                    return
                elif 251 <= x <= 867 and 524 <= y <= 663:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def victory_screen():
    pygame.mixer.stop()
    fon = pygame.transform.scale(load_image('victory.png'), screen_size)
    screen.blit(fon, (0, 0))
    pygame.mixer.Sound.play(full_victory_sound)
    pygame.display.set_caption('Space escape I, VICTORY')
    print('You won the game!')
    print('You totally collected ' + str(all_coins) + ' coins!')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print('You pressed "Q" to quit the game')
                    terminate()
                    return
        pygame.display.flip()
        clock.tick(FPS)


def level_line_counter(filename):
    filename = 'data/Locations/' + filename
    lines = []
    indexes = []
    with open(filename, 'r') as mapFile:
        for line in mapFile:
            lines.append(line)
    count = 0
    for line in lines:
        if '-' in line:
            indexes.append(count)
        count += 1
    return indexes


def check_location(name):
    filename = 'data/Locations/' + name
    if not os.path.isfile(filename):
        print('No such file in directory', filename)
        return False
    if name.split('.')[-1] != 'map':
        print('Location', filename, 'is incorrect')
        return False
    if word_counter(location_map_returner(filename), '|') == 0:
        print('Location', filename, 'is incorrect, no symbols "|"')
        return False
    if word_counter(location_map_returner(filename), '-') == 0:
        print('Location', filename, 'is incorrect, no symbols "-"')
        return False
    if word_counter(location_map_returner(filename), 'x') > 4:
        print('Location', filename, 'is incorrect, too many exits')
        return False
    if word_counter(location_map_returner(filename), 'x') < 4:
        print('Location', filename, 'is incorrect, not enough exits')
        return False
    if word_counter(location_map_returner(filename), '@') != 1:
        print('Location', filename, 'is incorrect, having a problem with a hero number')
        return False
    if word_counter(location_map_returner(filename), 'r') != 1:
        print('Location', filename, 'is incorrect, having a problem with a number of teleports')
        return False
    if word_counter(location_map_returner(filename), 'g') != 1:
        print('Location', filename, 'is incorrect, having a problem with a number of teleports')
        return False
    if word_counter(location_map_returner(filename), 'b') != 1:
        print('Location', filename, 'is incorrect, having a problem with a number of teleports')
        return False
    if not location_positions_checker(name):
        print('Location', filename, 'is incorrect, having a problem with a position of something')
        return False
    return True


def location_positions_checker(name):
    location = location_map_returner('data/Locations/' + name)
    indexes = level_line_counter(name)
    for y in range(len(location)):
        for x in range(len(location[y])):
            if location[y][x] == '@':
                if y >= indexes[0] or x >= location[y].index('|'):
                    return False
            elif location[y][x] == 'r':
                if y >= indexes[0] or x <= location[y].index('|'):
                    return False
            elif location[y][x] == 'g':
                if y <= indexes[0] or x <= location[y].index('|'):
                    return False
            elif location[y][x] == 'b':
                if y <= indexes[0] or x >= location[y].index('|'):
                    return False
    return True


def load_level(filename):
    filename = "data/Locations/" + filename
    with open(filename, 'r') as mapFile:
        lvl_map = []
        for line in mapFile:
            lvl_map.append(line.strip())
    max_width = max(map(len, lvl_map))
    return list(map(lambda x: list(x.ljust(max_width)), lvl_map))


def get_teleport(filename):
    filename = "data/Locations/" + filename
    location = location_map_returner(filename)
    teleport_returner = []
    for y in range(len(location)):
        for x in range(len(location[y])):
            if location[y][x] == 'r':
                teleport_returner.insert(0, '{},{}'.format(x, y))
            if location[y][x] == 'g':
                teleport_returner.insert(1, '{},{}'.format(x, y))
            if location[y][x] == 'b':
                teleport_returner.insert(2, '{},{}'.format(x, y))
    return teleport_returner


def location_map_returner(file):
    location_map = []
    with open(file, 'r') as mapFile:
        for i in mapFile:
            location_map.append(i)
    return location_map


def word_counter(list, word):
    count = 0
    for line in list:
        count += ''.join(line).count(word)
    return count


def generate_level(level):
    successful = []
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'L':
                Tile('Spikes_left', x, y)
            elif level[y][x] == 'r':
                Tile('Red_teleport', x, y)
            elif level[y][x] == 'g':
                Tile('Green_teleport', x, y)
            elif level[y][x] == 'b':
                Tile('Blue_teleport', x, y)
            elif level[y][x] == 'R':
                Tile('Spikes_right', x, y)
            elif level[y][x] == 'U':
                Tile('Spikes_up', x, y)
            elif level[y][x] == 'D':
                Tile('Spikes_down', x, y)
            elif level[y][x] == 'x':
                if x < level[y].index('|') and 'RED' not in successful:
                    Tile('Exit_red', x, y)
                    successful.append('RED')
                elif x > level[y].index('|') and 'GREEN' not in successful:
                    Tile('Exit_green', x, y)
                    successful.append('GREEN')
                elif x < level[y].index('|') and 'RED' in successful:
                    Tile('Exit_yellow', x, y)
                    successful.append('YELLOW')
                elif x > level[y].index('|') and 'GREEN' in successful:
                    Tile('Exit_blue', x, y)
                    successful.append('BLUE')
            elif level[y][x] == '$':
                Coin(x * tile_width + 12, y * tile_height + 12, coin_group, load_image('Coin_sheet.png'), 8, 1)
                Tile('empty', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '-':
                Tile('Line_left_right', x, y)
            elif level[y][x] == '|':
                if level[y][x + 1] == '-':
                    Tile('Middle', x, y)
                else:
                    Tile('Line_up_down', x, y)
    return new_player, x, y


pygame.display.set_caption('Space escape I')
coin_sound = pygame.mixer.Sound(load_sound('Coin.mp3'))
leap_sound = pygame.mixer.Sound(load_sound('Leap.mp3'))
next_level_sound = pygame.mixer.Sound(load_sound('next_level.mp3'))
full_victory_sound = pygame.mixer.Sound(load_sound('Victory_full.mp3'))
death_sound = pygame.mixer.Sound(load_sound('death.mp3'))
main_sound = pygame.mixer.Sound(load_sound('Space escape.mp3'))
error_sound = pygame.mixer.Sound(load_sound('Error_sound.mp3'))
start_screen()
main_menu()
location_number = 1
locations = [f for f in os.listdir('data/Locations') if check_location(f)]
if len(locations) == 0:
    print('All locations are incorrect, unable to load them')
    terminate()
map_file = locations[location_number - 1]
level_map = load_level(map_file)
teleports = get_teleport(map_file)
hero, max_x, max_y = generate_level(level_map)
level_indexes = level_line_counter(map_file)
coins = get_coins(level_indexes, map_file)
pygame.display.set_caption('Space escape I, level - ' + str(locations[0]))
all_coins = 0
while running:
    if hero.reloading:
        print('Reloading level...')
        pygame.mixer.stop()
        player = None
        running = True
        sprite_group = SpriteGroup()
        hero_group = SpriteGroup()
        coin_group = SpriteGroup()
        particle_sprites = SpriteGroup()
        map_file = locations[location_number - 1]
        if not check_location(map_file):
            print('Location deleted or changed')
            terminate()
        level_map = load_level(map_file)
        teleports = get_teleport(map_file)
        hero, max_x, max_y = generate_level(level_map)
        level_indexes = level_line_counter(map_file)
        coins = get_coins(level_indexes, map_file)
        pygame.display.set_caption('Space escape I, level - ' + str(locations[location_number - 1]))
        hero.coins = 0
        hero.total_coins = 0
        screen.fill(pygame.Color("black"))
        coin_group.draw(screen)
        hero.move(hero.pos[0], hero.pos[1])
        sprite_group.draw(screen)
        hero_group.draw(screen)
        coin_group.draw(screen)
        pygame.display.flip()
        hero.reloading = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                print('You pressed "Q" to quit the game')
                terminate()
            elif event.key == pygame.K_r:
                hero.pos = (0, 0)
                screen.fill(pygame.Color("black"))
                hero.reloading = True
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                pygame.mixer.Sound.play(leap_sound)
                Player.action(hero, "up")
                for particle in particle_sprites:
                    particle.kill()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                pygame.mixer.Sound.play(leap_sound)
                Player.action(hero, "down")
                for particle in particle_sprites:
                    particle.kill()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                pygame.mixer.Sound.play(leap_sound)
                Player.action(hero, "left")
                for particle in particle_sprites:
                    particle.kill()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                pygame.mixer.Sound.play(leap_sound)
                Player.action(hero, "right")
                for particle in particle_sprites:
                    particle.kill()
            elif event.key == pygame.K_c:
                Player.balance(hero)
            elif event.key == pygame.K_SPACE:
                Player.action(hero, "space")
    screen.fill(pygame.Color("black"))
    hero.move(hero.pos[0], hero.pos[1])
    sprite_group.draw(screen)
    hero_group.draw(screen)
    coin_group.draw(screen)
    pygame.display.flip()
    for particle in particle_sprites:
        particle.kill()
    if hero.levels == len(coins):
        pygame.mixer.Sound.play(next_level_sound)
        print('You have completed the location and collected', hero.total_coins, 'coins. Congrats!')
        all_coins += hero.total_coins
        next_level()
pygame.quit()
