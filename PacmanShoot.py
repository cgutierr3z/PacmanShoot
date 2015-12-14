#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################

# This file is part of PacmanShoot.

# PacmanShoot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PacmanShoot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PacmanShoot.  If not, see <http://www.gnu.org/licenses/>.

#######################################################################

import random
import sys

import pygame
from pygame.locals import *

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

START, STOP = 0, 1

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_SIZE = [SCREEN_WIDTH,SCREEN_HEIGHT]
screen =  pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("PacmanShoot")
clock = pygame.time.Clock()

back = pygame.image.load('fondo.jpg').convert()
back = pygame.transform.scale(back,(SCREEN_WIDTH,SCREEN_HEIGHT))

sprites_activos = pygame.sprite.Group()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Explosion, self).__init__()
        sheet = pygame.image.load("explosion_strip16.png")
        self.images = []
        for i in range(0, 1536, 96):
            rect = pygame.Rect((i, 0, 96, 96))
            image = pygame.Surface(rect.size)
            image.blit(sheet, (0, 0), rect)
            image.set_colorkey(BLACK)
            self.images.append(image)

        self.image = self.images[0]
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.add(sprites_activos)

    def update(self):
        self.image = self.images[self.index]
        self.index += 1
        if self.index >= len(self.images):
            self.kill()


class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Bala, self).__init__()

        self.image = pygame.image.load('bala.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(32,32))
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        x, y = self.rect.center
        x += 20
        self.rect.center = x, y
        if y <= 0:
            self.kill()


class Enemigo(pygame.sprite.Sprite):
    def __init__(self, y_pos, groups):
        super(Enemigo, self).__init__()
        self.image = pygame.image.load('enemigo.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(64,64))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH, y_pos)

        self.velocidad = random.randint(3, 5)

        self.add(groups)
        self.explosion = pygame.mixer.Sound("Arcade Explo A.wav")
        self.explosion.set_volume(0.4)

    def update(self):
        x, y = self.rect.center

        if x < 0:
            x, y = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
            self.velocidad = random.randint(3, 5)
        else:
            x, y = x - self.velocidad, y

        self.rect.center = x, y

    def kill(self):
        x, y = self.rect.center
        if pygame.mixer.get_init():
            self.explosion.play(maxtime=1000)
            Explosion(x, y)
        super(Enemigo, self).kill()


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self, jugador, groups):
        super(ScoreBoard, self).__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, 30))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(default_font, 20)

        self.jugador = jugador
        self.add(groups)

    def update(self):
        puntos = self.font.render("Vida : {}%   -   Puntos : {}".format(self.jugador.vida, self.jugador.puntos), True, (150, 50, 50))
        size = self.font.size("Vida : {}%   -   Puntos : {}")
        self.image.fill(WHITE)
        self.image.blit(puntos, (SCREEN_WIDTH//2 - size[0]//2, 0))


class Pacman(pygame.sprite.Sprite):
    def __init__(self, groups, weapon_groups):
        super(Pacman, self).__init__()

        self.image = pygame.image.load('pacman.png')
        self.image = self.image.convert()
        self.color = self.image.get_at((0,0))
        self.image.set_colorkey(self.color, RLEACCEL)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.dx = self.dy = 0
        self.fuego = self.shot = False
        self.vida = 100
        self.puntos = 0

        self.groups = [groups, weapon_groups]

    def update(self):
        pos = pygame.mouse.get_pos()
        x, y = pos[0],pos[1]

        #print x,y,self.rect.x,self.rect.y

        # dispara
        if self.fuego:
            self.shot = Bala(x, y)
            self.shot.add(self.groups)

        if self.vida < 0:
            self.kill()

        # movimiento
        self.rect.center = x + self.dx, y + self.dy

    def shoot(self, operation):
        if operation == START:
            self.fuego = True
        if operation == STOP:
            self.fuego = False


def texto(texto, font):
    txt = font.render(texto, True, WHITE)
    return txt, txt.get_rect()


def mensaje(msg):
    font = pygame.font.Font('freesansbold.ttf',115)
    txt, txtRect = texto(msg, font)
    txtRect.center = ((SCREEN_WIDTH/2),(SCREEN_HEIGHT/2))
    screen.blit(txt, txtRect)

    pygame.display.update()


def main():
    end_game = False

    pygame.font.init()
    pygame.mixer.init()

    enemigos = pygame.sprite.Group()
    disparos = pygame.sprite.Group()

    jugador = Pacman(sprites_activos, disparos)
    jugador.add(sprites_activos)

    puntaje = ScoreBoard(jugador, sprites_activos)

    #enemigos
    for i in range(10):
        pos = random.randint(30, SCREEN_HEIGHT)
        Enemigo(pos, [sprites_activos, enemigos])

    # musca de fondo
    if pygame.mixer.get_init():
        pygame.mixer.music.load("DST-AngryMod.mp3")
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

    while True:
        clock.tick(30)
        screen.blit(back, (0,0))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit()

            if not end_game:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    jugador.shoot(START)
                elif event.type == pygame.MOUSEBUTTONUP:
                    jugador.shoot(STOP)

        #colision enemigos y jugador
        hit_pacman = pygame.sprite.spritecollide(jugador, enemigos, True)
        for i in hit_pacman:
            jugador.vida -= 5

        if jugador.vida < 0:
            mensaje("HAS PERDIDO")
            sys.exit()

        #colision enemigos y balas
        hit_enemigos = pygame.sprite.groupcollide(enemigos, disparos, True, True)
        for k, v in hit_enemigos.iteritems():
            k.kill()
            for i in v:
                i.kill()
                jugador.puntos += 10

        if len(enemigos) < 20 and not end_game:
            pos = random.randint(30, SCREEN_HEIGHT)
            Enemigo(pos, [sprites_activos, enemigos])


        #modificadores de la velocidad de los enemigos de acuerdo al puntaje
        if jugador.puntos >= 100:
            for i in enemigos:
                i.velocidad = random.randint(5, 10)

        if jugador.puntos >= 1000:
            for i in enemigos:
                i.velocidad = random.randint(10, 15)

        if jugador.puntos >= 5000:
            for i in enemigos:
                i.velocidad = random.randint(15, 20)

        if jugador.puntos >= 9000:
            for i in enemigos:
                i.velocidad = random.randint(20, 30)

        # fin del juego
        if jugador.puntos >= 10000:
            mensaje("HAS GANADO")
            end_game = True
            for i in enemigos:
                i.kill()

            jugador.shoot(STOP)

        if end_game:
            sys.exit()

        sprites_activos.update()
        sprites_activos.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()
