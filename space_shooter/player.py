import pygame

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = 400  # Center horizontally
        self.rect.bottom = 640  # Bottom of the screen
        self.speed = 5
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shield = False
        self.shield_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed

        # Rapid fire timer
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False

        # Shield timer
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

    def activate_rapid_fire(self, duration):
        self.rapid_fire = True
        self.rapid_fire_timer = duration

    def activate_shield(self, duration):
        self.shield = True
        self.shield_timer = duration
