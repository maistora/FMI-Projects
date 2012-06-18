#!/usr/bin/env python

import pygame
import gun
import random
import sounds
import effects

class Player(pygame.sprite.Sprite):

    gun_cooldown = 0
    gun_cooldown_delay = 0.3
    gun_overflow = 0
    gun_overflow_max = 50
    gun_overflow_step = 6 
    gun_overflow_step_back = 10
    gun_direction = -1
    gun_type = 'green'
    gun_level = 1
    gun_powers = (25, 50)
    gun_speed = 320
    can_shoot = True

    health = 100
    shield = 50
    shield_step_back = 1
    
    move_speed = 300

    kills = 0
    score = 0

    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        self.image = pygame.image.load('images/player.png')
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.radius = 22


    def __movement(self, tick):
        img_left = pygame.image.load('images/player_left.png')
        img_right = pygame.image.load('images/player_right.png')
        img_original = pygame.image.load('images/player.png')

        step = self.move_speed * tick

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.image = img_left
            self.rect.x -= step
        if key[pygame.K_RIGHT]:
            self.image = img_right
            self.rect.x += step
        if key[pygame.K_UP]:
            self.rect.y -= step
            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT]):
                self.image = img_original
        if key[pygame.K_DOWN]:
            self.rect.y += step
            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT]):
                self.image = img_original

        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                self.image = img_original


    def __collide_controller(self, game, last):
        new = self.rect

        for cell in pygame.sprite.spritecollide(self, game.walls, False):
            cell_rect = cell.rect
            if last.right <= cell_rect.left and new.right > cell_rect.left:
                new.right = cell_rect.left
            if last.left >= cell_rect.right and new.left < cell_rect.right:
                new.left = cell_rect.right
            if last.bottom <= cell_rect.top and new.bottom > cell_rect.top:
                new.bottom = cell_rect.top
            if last.top >= cell_rect.bottom and new.top < cell_rect.bottom:
                new.top = cell_rect.bottom

        for enemy in game.enemies.sprites():
            if pygame.sprite.collide_circle(self, enemy):
                enemy.kill()
                effects.Explosion(enemy.rect.midtop, game, game.sprites)
                sounds.Sound('death')

                self.__zero_stats()
                self.kill()
                effects.Explosion(self.rect.midtop, game, game.sprites)
                sounds.Sound('death')


    def __shoot(self, gun1, events, dt, game):
        key = pygame.key.get_pressed()
        if key[pygame.K_LSHIFT] and not self.gun_cooldown and self.can_shoot:
            gun_power = self.__get_gun_power()
            if self.gun_level == 1:
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midtop, 
                        self.gun_direction, 
                        game.sprites
                        )    
                
            if self.gun_level == 2:
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midright, 
                        self.gun_direction, 
                        game.sprites
                        )    
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midleft, 
                        self.gun_direction, 
                        game.sprites)    
            if self.gun_level == 3:
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midright, 
                        self.gun_direction, 
                        game.sprites
                        )    
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midtop, 
                        self.gun_direction, 
                        game.sprites
                        )    
                gun.Gun(
                        self.gun_type, 
                        gun_power, 
                        self.gun_speed, 
                        False, 
                        self.rect.midleft, 
                        self.gun_direction, 
                        game.sprites
                        )    
            self.gun_cooldown = self.gun_cooldown_delay
            self.gun_overflow += self.gun_overflow_step
            if self.gun_overflow >= self.gun_overflow_max:
                self.can_shoot = False
                sounds.Sound('overflow').play()
            sounds.Sound('shot').play()
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        

    def __get_gun_power(self):
        rand = random.randint(self.gun_powers[0], self.gun_powers[1])
        return rand


    def __zero_stats(self):
        self.health = 0
        self.shield = 0


    def __gun_overflow_check(self, tick):
        if self.gun_overflow > 0:
            self.gun_overflow -= self.gun_overflow_step_back * tick
            self.gun_overflow = max(0, self.gun_overflow)
            if self.gun_overflow == 0:
                self.can_shoot = True


    def __shield_check(self, tick):
        if self.shield > 0:
            self.shield -= self.shield_step_back * tick
            self.shield = max(0, self.shield)


    def update(self, tick, game):
        last_position = self.rect.copy()
        self.__movement(tick)
        self.__shoot(1, game.events, tick, game)
        self.__gun_overflow_check(tick)
        self.__shield_check(tick)
        self.__collide_controller(game, last_position)
