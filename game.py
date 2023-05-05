import pygame
from pygame.locals import * # type: ignore
import os
import random
import sys
import time

# Initialisation de Pygame, mixer et les polices
pygame.init()
pygame.mixer.init()
pygame.font.init()

# Constantes de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Batman Du coup 2 éléctrique boogaloo édition")

# Chargement des images
background_image = "images/Batman_background.jpg"
background_city = "images/City_background.jpg"
player_image_paths = [
    "images/characterbatman.png",
    "images/robin.png",
    "images/Batgirl.png",
    "images/Nightwing.png"
]
enemy_image_path = "images/joker.png"
background = pygame.image.load(background_image).convert()
background_city_image = pygame.image.load(background_city).convert()

# Chargement des sons
son_Batman = pygame.mixer.Sound("BatmanSon.wav")
son_theme = pygame.mixer.Sound("Batman_theme.mp3")
son_game_over = pygame.mixer.Sound("Game over.wav")
son_theme_arcade = pygame.mixer.Sound("Theme arcade_01.wav")

# Chargement des personnages
player_images = [pygame.image.load(path).convert_alpha() for path in player_image_paths]
enemy_image = pygame.image.load(enemy_image_path).convert_alpha()

# Centrage du background
bg_x = (SCREEN_WIDTH - background.get_width()) // 2
bg_y = (SCREEN_HEIGHT - background.get_height()) // 2
SCREEN.blit(background, (bg_x, bg_y))

# Centrage du background_city
bg_city_x = (SCREEN_WIDTH - background_city_image.get_width()) // 2
bg_city_y = (SCREEN_HEIGHT - background_city_image.get_height()) // 2

# Constantes
GRAVITY = 0.5
GROUND_HEIGHT = 50
font = "Gotham black"
max_enemies = 20

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Classe Menu
class Menu:
    def __init__(self, items, font, font_size, font_color, x, y):
        self.items = items
        self.font = pygame.font.SysFont(font, font_size)
        self.font_color = font_color
        self.x = x
        self.y = y
        self.menu_items = []
        self.selected_item = 1

        for index, item in enumerate(items):
            if index == 0:
                label = self.font.render(item, 1, (255, 255, 0)) # type: ignore
                width = label.get_rect().width
                height = label.get_rect().height
                posx = x - (width / 2)
                t_h = len(items) * height
                posy = y - (t_h / 2) + (index * height) - 50
            else:
                label = self.font.render(item, 1, font_color) # type: ignore
                width = label.get_rect().width
                height = label.get_rect().height
                posx = x - (width / 2)
                t_h = len(items) * height
                posy = y - (t_h / 2) + (index * height)
            self.menu_items.append([item, label, (width, height), (posx, posy)])

    def draw(self, surface):
        for item in self.menu_items:
            surface.blit(item[1], item[3])

    def move_up(self):
        if self.selected_item > 1:
            self.selected_item -= 1
            self._update_item_colors()

    def move_down(self):
        if self.selected_item < len(self.items) - 1:
            self.selected_item += 1
            self._update_item_colors()

    def _update_item_colors(self):
        for index, item in enumerate(self.menu_items):
            if index == self.selected_item:
                item[1] = self.font.render(item[0], 1, (255, 0, 0))  # type: ignore
            else:
                item[1] = self.font.render(item[0], 1, self.font_color)  # type: ignore

def difficulty_selection():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    difficulty_menu.move_up()
                elif event.key == K_DOWN:
                    difficulty_menu.move_down()
                elif event.key == K_RETURN:
                    selected_difficulty = difficulty_menu.items[difficulty_menu.selected_item]
                    if selected_difficulty in ["Facile", "Normal", "Difficile", "Cauchemar"]:
                        return selected_difficulty
                    elif selected_difficulty == "Retour":
                        return None

        SCREEN.fill((0, 0, 0))
        SCREEN.blit(background, (bg_x, bg_y))
        difficulty_menu.draw(SCREEN)
        pygame.display.update()
    return None

# Fonction score
def display_score(score):
    font = pygame.font.SysFont("Gotham black", 32)
    score_text = font.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(score_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))
    
# Fonction vie
def display_lives(lives):
    font = pygame.font.SysFont("Gotham black", 32)
    lives_text = font.render(f"Vies: {lives}", True, WHITE)
    SCREEN.blit(lives_text, (10, SCREEN_HEIGHT - 40))

class Player(pygame.sprite.Sprite):
    def __init__(self, image, lives, invincibility_duration):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - GROUND_HEIGHT - self.rect.height // 2)
        self.velocity = pygame.math.Vector2(0, 0)
        self.lives = lives
        self.invincible = False
        self.invincibility_time = 0
        self.visible = True
        self.visibility_timer = 0
        self.invincibility_duration = invincibility_duration

    def update(self):
        self.velocity.y += GRAVITY
        self.rect.move_ip(self.velocity)

        if self.rect.bottom > SCREEN_HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            self.velocity.y = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.velocity.x = -5
        elif keys[pygame.K_RIGHT]:
            self.velocity.x = 5
        else:
            self.velocity.x = 0

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.invincible:
            if time.time() - self.visibility_timer >= 0.1:
                self.visible = not self.visible
                self.visibility_timer = time.time()

        if time.time() - self.invincibility_time >= self.invincibility_duration:
            self.invincible = False
            self.visible = True

        if not self.invincible and not self.visible:
            self.visible = True


    def jump(self):
        self.velocity.y -= 10

# Classe ennemi
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, 800), 0)
        self.speed = random.randint(1, 6)

    def update(self):
        self.rect.move_ip(0, self.speed)
        self.speed += 0.01

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Fonction de sélection des personnages
def character_selection():
    menu_items = ["Choisissez un personnage", "Batman", "Robin", "Batgirl ", "Nightwing", "Retour"]
    character_menu = Menu(menu_items, font, 32, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    character_menu.move_up()
                elif event.key == K_DOWN:
                    character_menu.move_down()
                elif event.key == K_RETURN:
                    selected_character = character_menu.items[character_menu.selected_item]
                    if selected_character == "Batman":
                        return player_images[0]
                    elif selected_character == "Robin":
                        return player_images[1]
                    elif selected_character == "Batgirl":
                        return player_images[2]
                    elif selected_character == "Nightwing":
                        return player_images[3]
                    elif selected_character == "Retour":
                        return None

        SCREEN.fill((0, 0, 0))
        SCREEN.blit(background, (bg_x, bg_y))
        character_menu.draw(SCREEN)
        pygame.display.update()
    return None

# Fonction pour gérer le jeu
def game(character_image, difficulty):

    def get_character_name(character_image):
        if character_image == player_images[0]:
            return "Batman"
        elif character_image == player_images[1]:
            return "Robin"
        elif character_image == player_images[2]:
            return "Batgirl"
        elif character_image == player_images[3]:
            return "Nightwing"



    # Chargement des images
    player_image = character_image
    enemy_image = pygame.image.load(enemy_image_path).convert_alpha()
    ground_image = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT))
    ground_image.fill(BLACK)
    score = 0
    invincibility_duration = 2.5

    if difficulty == "Facile":
        max_enemies = 10

    elif difficulty == "Normal":
        max_enemies = 20

    elif difficulty == "Difficile":
        max_enemies = 30

    elif difficulty == "Cauchemar":
        max_enemies = 50

    # Création des sprites
    all_sprites = pygame.sprite.Group()
    player = Player(character_image, 3, invincibility_duration)
    all_sprites.add(player)
    background = pygame.image.load(background_city).convert()
    enemies = pygame.sprite.Group()
    for i in range(10):
        enemy = Enemy()
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Ajout de la boucle du jeu
    running = True
    score_timer = time.time()
    while running:

        son_theme_arcade.play()

        # Mise à jour de l'état d'invincibilité
        if player.invincible:
            if time.time() - player.invincibility_time >= invincibility_duration:   # type: ignore
                player.invincible = False

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.jump()

        # Mise à jour des sprites
        all_sprites.update()

        # Gestion des collisions
        if not player.invincible and pygame.sprite.spritecollide(player, enemies, False):
            player.lives -= 1
            if player.lives <= 0:
                running = False
            else:
                player.invincible = True
                player.invincibility_time = time.time() # type: ignore
                pygame.time.delay(1000)

        # Incrémenter le score toutes les secondes
        if time.time() - score_timer >= 1:
            score += 1
            score_timer = time.time()

        # Enlever les ennemis qui sortent de la fenêtre
        for enemy in enemies:
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()

        # Ajouter des ennemis supplémentaires jusqu'à un nombre maximal
        if len(enemies) < max_enemies: # type: ignore
            enemy = Enemy()
            enemies.add(enemy)
            all_sprites.add(enemy)

        # Dessin des sprites et du sol
        SCREEN.blit(background_city_image, (bg_city_x, bg_city_y))
        if player.visible:
            all_sprites.draw(SCREEN)
        else:
            all_sprites.remove(player)
            all_sprites.draw(SCREEN)
            all_sprites.add(player)
        SCREEN.blit(ground_image, (0, SCREEN_HEIGHT - GROUND_HEIGHT))

        # Affichage du score et des vies
        display_score(score)
        display_lives(player.lives)

        # Mise à jour de l'affichage
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    # Ajout de la sauvegarde des données dans le fichier CSV
    character_name = get_character_name(character_image)
    save_data_to_csv(character_name, difficulty, score)


    # Affichage de l'écran "game over"
    game_over()
    



# Fonction Game Over
def game_over():
    game_over_text = pygame.font.SysFont(font, 64).render("Game Over", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    SCREEN.blit(game_over_text, text_rect)
    pygame.display.flip()
    son_theme_arcade.stop()
    son_game_over.play()
    time.sleep(4)
    menu.selected_item = 1
    return True

# Menu difficulté
difficulty_menu_items = ["Sélectionnez la difficulté", "Facile", "Normal", "Difficile", "Cauchemar", "Retour"]
difficulty_menu = Menu(difficulty_menu_items, font, 32, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

# Menu personnage
menu_items = ["Batman et l'attaque des Jokers", "START", "QUIT"]
menu = Menu(menu_items, font, 42, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

# Jouer le son du menu
son_theme.play()

running = True
game_is_over = False
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                menu.move_up()
            elif event.key == K_DOWN:
                menu.move_down()
            elif event.key == K_RETURN:
                if menu.items[menu.selected_item] == "START":
                    son_theme.stop()
                    son_Batman.play()
                    character_image = character_selection()
                    if character_image:
                        difficulty = difficulty_selection()
                        if difficulty:
                            game(character_image, difficulty)
                            game_is_over = True
                            son_theme.play()
                elif menu.items[menu.selected_item] == "QUIT":
                    pygame.quit()
                    sys.exit()
    if game_is_over:
        game_is_over = False
        menu.selected_item = 1

    SCREEN.fill((0, 0, 0))
    SCREEN.blit(background, (bg_x, bg_y))
    menu.draw(SCREEN)
    pygame.display.update()

    def save_data_to_csv(character, difficulty, score):
        import csv
        file_name = "scores.csv"
        headers = ["Character", "Difficulty", "Score"]

        if not os.path.exists(file_name):
            with open(file_name, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)

        with open(file_name, mode="a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([character, difficulty, score])