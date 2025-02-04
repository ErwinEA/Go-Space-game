import os
import time
import random
import pygame
import sys
pygame.init()


WIDTH, HEIGHT = 800, 500
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GO SPACE")
icon= pygame.image.load(os.path.join("assets", "logo2.png"))
pygame.display.set_icon(icon)


# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
FINAL_BOSS = pygame.image.load(os.path.join("assets", "fina_boss.png"))
ROYAL_SHIP = pygame.image.load(os.path.join("assets", "Webp.net-resizeimage.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
PURPLE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_purple.png"))

#Sounds & Sound Effects
BULLET_SOUND = pygame.mixer.Sound(os.path.join("sound", "Laser_shot.wav"))
BULLET_SOUND.set_volume(0.1)
MUSIC = pygame.mixer.music.load(os.path.join("sound", "background_music.wav"))
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)
# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship, Laser):
    def __init__(self, x, y, increment, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.increment = increment
    
    def move_lasers(self, vel, objs):
        
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.increment()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
                "royal": (ROYAL_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            

class Boss(Ship):
    BOSS_MAP = {
                "black": (FINAL_BOSS, PURPLE_LASER)
                }

    def __init__(self, x, y, boss, health=200):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.BOSS_MAP[boss]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            

    
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    score = 0
    run = True
    FPS = 70
    lives = 3
    main_font = pygame.font.Font(os.path.join("text", "LondrinaSolid-Light.ttf"), 30)
    lost_font = pygame.font.Font(os.path.join("text", "LondrinaSolid-Thin.ttf"), 50)

    
    bosses = []
    enemies = []
    wave_length = 5
    wave2_length = 0
    enemy_vel = 1
    boss_vel = 1

    player_vel = 5
    laser_vel = 5
    
    
    def increment():
        nonlocal score
        score+= 1


    player = Player(250, 375, increment)


    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    

    def redraw_window():
        
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        points_label = main_font.render(f"Score: {score}" , 1, (255,255,255))
        

        WIN.blit(lives_label, (10, 10))
        WIN.blit(points_label, (10,40))
        

        for enemy in enemies:
            enemy.draw(WIN)
        
        for boss in bosses:
            boss.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!! ", 1, (255,255,255))
            score_label = lost_font.render(f"Your Score is {score}", 1, (255,255,255))
            WIN.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2, 200))
            WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 300))
 
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 2:
                run = False
            else:
                continue

        

        if len(enemies) == 0:
            
            wave_length += 5
            

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green", "royal"]))
                enemies.append(enemy)

            if score % 100 == 0:
                for i in range(wave2_length):
                    boss = Boss(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["black"]))
                    bosses.append(boss)
            
                
        
        
        
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
                


        # LEFT CONTROLS
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left ARROW
            player.x -= player_vel
        # RIGHT CONTROLS
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right ARROW
            player.x += player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right 
            player.x += player_vel
        
        # UP CONTROLS
        if keys[pygame.K_w] and player.y - player_vel  > 0: # up 
            player.y -= player_vel
        if keys[pygame.K_UP] and player.y - player_vel  > 0: # up ARROW
            player.y -= player_vel

        #DOWN CONTROLS
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT: # down ARROW
            player.y += player_vel
        
        # shoot controls
        if keys[pygame.K_SPACE]:
            BULLET_SOUND.play()
            player.shoot()
        

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                

            
                

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                score += 1
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)


        for boss in bosses[:]:
            boss.move(boss_vel)
            boss.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                boss.shoot()
                

            
                

            if collide(boss, player):
                player.health -= 20
                bosses.remove(boss)
                score += 1
            elif boss.y + boss.get_height() > HEIGHT:
                lives -= 1
                bosses.remove(boss)
            

        player.move_lasers(-laser_vel, enemies)
        player.move_lasers(-laser_vel, bosses)


#Main Menu
def main_menu():
    title_font = pygame.font.Font(os.path.join("text", "LondrinaSolid-light.ttf"), 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        # logo on the menu
        WIN.blit(icon, (WIDTH/2 - icon.get_width()/2, 20))
        
        start_label = title_font.render("Press ENTER To Begin", 1, (255,255,255))
        WIN.blit(start_label, (WIDTH/2 - start_label.get_width()/2, 250))
        
        
        pygame.display.update()

        keyz = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if keyz[pygame.K_RETURN]:
                main()

    pygame.quit()

main_menu()




