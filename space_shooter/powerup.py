import pygame
import random

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type, image):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 800 - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 650:
            self.kill()
