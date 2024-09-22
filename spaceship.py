import pygame
import random
import os
import math
import sys
from leaderboard import load_leaderboard, save_leaderboard, update_leaderboard, draw_leaderboard, get_player_name, MAX_LEADERBOARD_SIZE

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions (default)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Load the space-themed font
title_font_path = 'fonts/Orbitron/static/Orbitron-Bold.ttf'  # Adjust the path as needed
menu_font_path = 'fonts/Orbitron/static/Orbitron-Regular.ttf'   # Can be the same or different

# Set up fonts
font = pygame.font.Font(menu_font_path, 36)
hud_font = pygame.font.Font(menu_font_path, 28)
big_font = pygame.font.Font(menu_font_path, 72)

navigate_sound = pygame.mixer.Sound('sounds/click.wav')
select_sound = pygame.mixer.Sound('sounds/select.wav')

# Load images (ensure correct path)
spaceship_image = pygame.image.load("images/spaceship.png")
bullet_image = pygame.image.load("images/bullet.png")
enemy_image = pygame.image.load("images/alien.png")
explosion_image = pygame.image.load("images/explosion.png")
rapid_fire_image = pygame.image.load("images/rapid_fire.png")
shield_image = pygame.image.load("images/shield.png")
bomb_image = pygame.image.load("images/bomb.png")

# Resize images
spaceship_image = pygame.transform.scale(spaceship_image, (50, 50))
bullet_image = pygame.transform.scale(bullet_image, (5, 10))
enemy_image = pygame.transform.scale(enemy_image, (40, 40))
explosion_image = pygame.transform.scale(explosion_image, (40, 40))
rapid_fire_image = pygame.transform.scale(rapid_fire_image, (30, 30))
shield_image = pygame.transform.scale(shield_image, (30, 30))
bomb_image = pygame.transform.scale(bomb_image, (30, 30))

# Game state variables
game_active = False
tutorial_active = False
difficulty = 'medium'  # Default difficulty level
difficulty_selected = 1  # Default is medium
difficulty_levels = ['easy', 'medium', 'hard']  # Difficulty options

# Function to display difficulty selection
def display_difficulty_selection(screen, selected_index):
    screen.fill(BLACK)
    title_text = big_font.render("Select Difficulty", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
    
    for i, level in enumerate(difficulty_levels):
        color = GREEN if i == selected_index else WHITE
        option_text = font.render(level.capitalize(), True, color)
        screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 200 + i * 50))
    
    pygame.display.flip()

# Function to handle difficulty selection with up/down keys
def handle_difficulty_selection(screen):
    global difficulty_selected, difficulty
    
    selected_index = difficulty_selected
    selecting = True
    
    while selecting:
        display_difficulty_selection(screen, selected_index)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(difficulty_levels)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(difficulty_levels)
                elif event.key == pygame.K_RETURN:
                    difficulty = difficulty_levels[selected_index]
                    selecting = False

# Define the spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shield = False  # Tracks whether the shield is active
        self.shield_timer = 0  # Timer for how long the shield lasts
    
    def update(self):
        """Update spaceship position and handle power-ups."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

        # Update timers for power-ups
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False


    def activate_rapid_fire(self, duration=300):
        self.rapid_fire = True
        self.rapid_fire_timer = duration  # Lasts for 300 frames (5 seconds at 60 FPS)

    def activate_shield(self, duration=300):
        self.shield = True
        self.shield_timer = duration  # Lasts for 5 seconds (300 frames at 60 FPS)


# Define the bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed=7):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:  # If the bullet goes off the top
            self.kill()

# Define the enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, speed, missed_callback, player):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)  # Start slightly above the screen
        self.speed = speed
        self.missed_callback = missed_callback  # Store the callback function
        self.player = player  # Store reference to the player object

    def update(self):
        """Move the enemy down the screen unless the shield is active."""
        if not self.player.shield:  # Check if the player's shield is active
            self.rect.y += self.speed  # Move enemy downward only if shield is inactive
        if self.rect.top > SCREEN_HEIGHT:  # Check if the enemy has crossed the bottom of the screen
            self.kill()  # Remove enemy from the screen
            print(f"Alien missed!")  # Debugging message for missed aliens
            self.missed_callback()  # Call the callback to increment missed aliens


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type, image):
        super().__init__()
        self.powerup_type = powerup_type  # Type of power-up (e.g., 'rapid_fire', 'shield', 'bomb')
        self.image = image  # Power-up image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)  # Random x-position
        self.rect.y = random.randint(-100, -40)  # Start slightly off-screen
        self.speed = 2  # Falling speed of the power-up

    def update(self):
        """
        Update the position of the power-up. 
        If it falls below the bottom of the screen, remove it.
        """
        self.rect.y += self.speed  # Move the power-up downward
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # Remove the power-up if it goes off-screen

# Define the explosion effect when an alien is hit
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = explosion_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.lifetime = 15  # Explosion will last for 15 frames (0.25 seconds)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.reset_game()
        self.player_name = "" # Initialize player_name as an empty string
        self.hud_font = pygame.font.Font(menu_font_path, 28)

    def reset_game(self):
        """Resets the game state for a new playthrough."""
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Load images
        self.spaceship_image = spaceship_image
        self.bullet_image = bullet_image
        self.enemy_image = enemy_image
        self.rapid_fire_image = rapid_fire_image
        self.shield_image = shield_image
        self.bomb_image = bomb_image

        # Player initialization
        self.player = Spaceship(self.spaceship_image)
        self.all_sprites.add(self.player)

        # Game state
        self.missed_aliens = 0
        self.level = 1
        self.max_missed_aliens = 15  # Game over condition
        self.level_duration = 15000  # Each level lasts 15 seconds (in ms)
        self.level_start_time = pygame.time.get_ticks()
        self.hud_color = WHITE  # Default HUD color
        self.score = 0
        self.game_active = True  # Track whether the game is active

        # Difficulty settings
        self.enemy_speed_multiplier = 1.0  # Enemies' speed starts at normal
        self.enemy_spawn_rate = 0.01  # Base enemy spawn rate
        self.level_duration_multiplier = 1.0  # Duration multiplier for each level

    def game_over(self):
        """Handles game over logic and checks for leaderboard updates."""
        # If the player has a score, check if it's a high score
        if self.score > 0:
            leaderboard = load_leaderboard()
            
            # Check if the leaderboard has less than 5 entries, or the score is higher than the lowest score
            if len(leaderboard) < MAX_LEADERBOARD_SIZE or self.score > leaderboard[-1]['score']:
                # Player qualifies for a high score, prompt for name
                self.player_name = get_player_name(self.screen, pygame.font.Font(None, 36))  # Set player_name
                update_leaderboard(self.player_name, self.score)
        
        # Show the game over screen with the leaderboard
        self.show_game_over_screen()



    def increment_missed_aliens(self):
        """Increments the missed aliens counter and checks if game over."""
        self.missed_aliens += 1
        print(f"Missed aliens count: {self.missed_aliens}")  # Debugging message
        if self.missed_aliens >= self.max_missed_aliens:
            self.game_active = False  # End the game if 15 aliens are missed
            print("Game Over! You missed too many aliens.")  # Debugging message

    def level_up(self):
        """Increases the level and makes the game harder."""
        self.level += 1  # Increment the game level
        print(f"Level Up! You are now on level {self.level}")  # Debugging message

        # Reset the missed aliens for the new level
        self.missed_aliens = 0

        # Increase the difficulty:
        self.enemy_speed_multiplier += 0.1  # Enemies get 10% faster each level
        self.enemy_spawn_rate += 0.005  # Enemies spawn faster with each level
        self.level_duration_multiplier -= 0.05  # Levels get shorter by 5%

        # Adjust level duration by multiplier, ensure it doesn't go below a minimum threshold
        self.level_duration = max(int(15000 * self.level_duration_multiplier), 5000)  # Min duration of 5 seconds

        # Reset the level start time
        self.level_start_time = pygame.time.get_ticks()

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Fire bullets when spacebar is pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game_active:  # Only fire bullets when the game is active
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top, self.bullet_image)
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)

            if self.game_active:
                self.update_game_state()
            else:
                self.game_over()

            pygame.display.flip()
            clock.tick(60)

    def update_game_state(self):
        """Handles updating the game state when the game is active."""
        # Check for level timer and difficulty scaling
        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time >= self.level_duration:
            self.level_up()
            self.level_start_time = pygame.time.get_ticks()

        # Spawn enemies and powerups
        self.spawn_enemy()  # Ensure that enemies are spawned at the correct rate
        if self.level >= 3:
            self.spawn_powerup()

        # Update sprites
        self.all_sprites.update()

        # Check for collisions between bullets and enemies
        collisions = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for collision in collisions:
            explosion = Explosion(collision.rect.centerx, collision.rect.centery)
            self.all_sprites.add(explosion)
            self.score += 10

        # Check for power-up collisions
        self.check_powerup_collisions()

        # Clear screen and draw everything
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.draw_hud()

    def spawn_enemy(self):
        """Spawns enemies at a random location with increasing speed as the level goes up."""
        if random.random() < self.enemy_spawn_rate + (self.level * 0.005):  # Adjust enemy spawn rate as the level increases
            enemy_speed = (1 + (self.level * 0.2)) * self.enemy_speed_multiplier  # Enemies get faster each level
            enemy = Enemy(self.enemy_image, enemy_speed, self.increment_missed_aliens, self.player)  # Pass player to enemy
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)


    def spawn_powerup(self):
        """Spawns powerups randomly."""
        if random.random() < 0.005:
            powerup_type = random.choice(['rapid_fire', 'shield', 'bomb'])
            powerup = PowerUp(powerup_type, getattr(self, f'{powerup_type}_image'))
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

    def check_powerup_collisions(self):
        """Handles the logic for power-up collisions."""
        powerup_collisions = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_collisions:
            if powerup.powerup_type == 'rapid_fire':
                self.player.activate_rapid_fire()
            elif powerup.powerup_type == 'shield':
                self.player.activate_shield()
            elif powerup.powerup_type == 'bomb':
                enemies_on_screen = len(self.enemies)
                for enemy in self.enemies:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    self.all_sprites.add(explosion)
                    enemy.kill()
                self.score += enemies_on_screen * 10

    def draw_hud(self):
        """Draws the heads-up display (HUD) when the game is active."""
        pygame.draw.rect(self.screen, (0, 0, 255), (0, 0, SCREEN_WIDTH, 50))  # Blue background

        # Display level, missed aliens, time left, and score
        level_text = self.hud_font.render(f"Level: {self.level}", True, (0, 255, 255))
        self.screen.blit(level_text, (10, 10))

        missed_text = self.hud_font.render(f"Missed: {self.missed_aliens}/{self.max_missed_aliens}", True, (255, 0, 0))
        self.screen.blit(missed_text, (200, 10))

        time_left = (self.level_duration - (pygame.time.get_ticks() - self.level_start_time)) // 1000
        timer_text = self.hud_font.render(f"Time: {time_left}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (400, 10))

        score_text = self.hud_font.render(f"Score: {self.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

        # Active power-up indicators (e.g., shield, rapid-fire)
        powerups_active_icons = []
        if self.player.shield:  # Show shield indicator
            powerups_active_icons.append((shield_image, self.player.shield_timer // 60))  # 60 FPS -> seconds
        if self.player.rapid_fire:  # Show rapid-fire indicator
            powerups_active_icons.append((rapid_fire_image, self.player.rapid_fire_timer // 60))

        # Draw the power-up indicators
        for i, (icon, timer) in enumerate(powerups_active_icons):
            self.screen.blit(icon, (10 + i * 50, 60))  # Display the icon
            timer_text = self.hud_font.render(f"{timer}s", True, (255, 255, 255))
            self.screen.blit(timer_text, (10 + i * 50, 90))

        pygame.display.flip()


    def show_game_over_screen(self):
        """Displays the game-over screen and the leaderboard."""
        self.screen.fill((0, 0, 0))  # Black background
        font = pygame.font.Font(None, 64)

        game_over_text = font.render("Game Over", True, (255, 0, 0))  # Red text
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 50))

        # Display the leaderboard, highlight the player's score
        draw_leaderboard(self.screen, pygame.font.Font(menu_font_path, 36), self.player_name, self.score)

        your_score = font.render("Your score: " + str(self.score), True, (255, 255, 255))
        restart_text = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))  # White text
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 100))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()  # Restart the game
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        exit()




def set_difficulty(level, game):
    """
    Sets the difficulty of the game by adjusting key parameters
    like screen width, max missed aliens, and level duration.
    """
    global SCREEN_WIDTH
    if level == 'easy':
        game.max_missed_aliens = 15
        game.level_duration = 20000  # Easier level lasts longer
        SCREEN_WIDTH = 800
    elif level == 'medium':
        game.max_missed_aliens = 10
        game.level_duration = 15000  # Default level duration
        SCREEN_WIDTH = 900
    elif level == 'hard':
        game.max_missed_ali

def start_screen(screen):
    """Displays the animated start screen."""
    clock = pygame.time.Clock()
    title_font_size = 80
    menu_font_size = 40

    # Load fonts
    title_font = pygame.font.Font(title_font_path, title_font_size)
    menu_font = pygame.font.Font(menu_font_path, menu_font_size)

    title_text = "Space Shooter"
    menu_options = ["Start Game", "Settings", "Exit"]
    selected_option = 0  # Index of the currently selected option

    running = True
    while running:
        screen.fill(BLACK)

        # Animate the title text (pulsing effect)
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2  # Value between 0 and 1
        animated_title_size = int(title_font_size + 10 * pulse)
        animated_title_font = pygame.font.Font(title_font_path, animated_title_size)
        title_surface = animated_title_font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_surface, title_rect)

        # Draw the menu options
        for i, option in enumerate(menu_options):
            color = YELLOW if i == selected_option else WHITE
            option_surface = menu_font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))
            screen.blit(option_surface, option_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                    navigate_sound.play()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                    navigate_sound.play()
                elif event.key == pygame.K_RETURN:
                    select_sound.play()
                    if menu_options[selected_option] == "Start Game":
                        running = False  # Proceed to the game
                    elif menu_options[selected_option] == "Settings":
                        # You can implement the settings screen if needed
                        pass
                    elif menu_options[selected_option] == "Exit":
                        pygame.quit()
                        exit()

        pygame.display.flip()
        clock.tick(60)


# Main entry point
def main():
    global game_active, tutorial_active

    clock = pygame.time.Clock()  # Limit FPS to avoid too-fast rendering

    # Initialize screen and game
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen)

    # Display the start screen
    start_screen(screen)

    # Proceed to the difficulty selection if needed
    handle_difficulty_selection(screen)
    set_difficulty(difficulty, game)  # Set the game difficulty based on user selection

    game_active = True
    if game_active:
        game.run()

if __name__ == '__main__':
    main()

