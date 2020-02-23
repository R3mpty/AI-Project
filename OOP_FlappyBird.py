#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries:
import pygame
import neat
# import time
import random
import \
    os  # The OS module in Python provides a way of using operating system dependent functionality (Mainly used to import image in this program)
from Character import *

class Game():
    def __init__(self, character):
        pygame.init()

        # Fonts:
        self.STAT_FONT = pygame.font.SysFont("comicsans", 50)
        self.END_FONT = pygame.font.SysFont("comicsans", 40)
        self.FRAME_WIDTH = 500
        self.FRAME_HEIGHT = 800
        self.WINDOW = pygame.display.set_mode((self.FRAME_WIDTH, self.FRAME_HEIGHT))
        pygame.display.set_caption("NEA Project 2019/20")
        # The images should all have transparent background or else we could not use a mask for pixel perfect collision
        self.BIRD_IMAGE = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character+ '1.png')))),
                           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character+ '2.png')))),
                           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character+ '3.png')))),
                           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character+ '1.png'))))]

        self.PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
        self.GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
        self.BACKGROUND_IMAGE = pygame.transform.scale(
            pygame.image.load(os.path.join("background", "12.png")).convert_alpha(),
            (500, 800))


class Pipes:
    GAP = 200  # The gaps between each pipes
    PIPE_VELOCITY = 5  # The speed at which the pipe moves toward the bird

    def __init__(self, x, game):
        self.x = x
        self.height = 0

        self.top = 0  # Keeping track of where the top of the pipe is being drawn and where the bottom of the pipe is being drawn
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(game.PIPE_IMAGE, False, True)  # Flipping the image
        self.PIPE_BOTTOM = game.PIPE_IMAGE  # Storing the image defined in the class so the program doesn't have to refer back to the gobal variables at the top

        self.passed = False  # A detection of whether the bird has passed the pipe
        self.set_height()

    def set_height(self):  # Setting the height of the pipes
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP  # Doing so allow each gap to be standardised

    def move(self):  # Minujsing it self by the velocity to move the pipes towards the bird
        self.x = self.x - self.PIPE_VELOCITY  # Moving the pipe slightly left each frame/loop

    def draw(self, window):  # Drawing the pipes
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Calculating the offset (used to check the pixel up against each other) (the offset is how far away the two top left corner is from each other)
        top_offset = (self.x - bird.x, self.top - round(
            bird.y))  # We need to round off bird.y as we dont need to put into consideration of decimals in this game (too small to be relevant)
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Seeing if there is any colision with the mask:
        top_point = bird_mask.overlap(top_mask, top_offset)
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if top_point or bottom_point:
            return True  # Basically saying that this two actions is not "none"
        return False


class Ground:
    GROUND_VELOCITY = 5

    def __init__(self, y, game):
        self.WIDTH = game.GROUND_IMAGE.get_width()
        self.IMAGE = game.GROUND_IMAGE
        self.y = y  # Location of the gound
        self.x1 = 0  # Two X as we are basically drawing 2 images for our base (Each X indicates where about the next gound is)
        self.x2 = self.WIDTH

    def move(self):
        self.x1 = self.x1 - self.GROUND_VELOCITY  # We are moving the images to the left so the it seems like the ground is moving
        self.x2 = self.x2 - self.GROUND_VELOCITY

        if self.x1 + self.WIDTH < 0:  # As soon as one images moves off the screen, the other one will come in and shuffle the original images to the back
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMAGE, (self.x1, self.y))
        window.blit(self.IMAGE, (self.x2, self.y))


def draw_window(window, bird, pipes, ground,
                score, game):  # Linking all the "draw" function in each class so the graphics can be displayed

    window.blit(game.BACKGROUND_IMAGE, (0, 0))  # (What we wanna draw, where we wanna place it)

    for pipe in pipes:
        pipe.draw(window)  # Needs to be "pipe" as we are printing accordingly to where in the pipe list the program is

    ground.draw(window)

    '''
    for bird in bird:
        bird.draw(window)
        '''
    bird.draw(window)

    score_label = game.STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(score_label, (game.FRAME_WIDTH - score_label.get_width() - 50, 10))

    pygame.display.update()


def end_screen(window, game):
    switch = True
    text_label = game.END_FONT.render("Press Space to Restart", 1, (255, 0, 0))
    while switch:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                switch = False

            if event.type == pygame.KEYDOWN:
                main()

        window.blit(text_label, (game.FRAME_WIDTH / 2 - text_label.get_width() / 2, 500))

        pygame.display.update()

    pygame.quit()
    quit()


def human_play(character):
    game = Game(character) # pass in to the game, which gives the character a new skin
    bird = Character(230, 350, game) 
    ground = Ground(730, game)
    pipes = [Pipes(600, game)]  # x = 700
    window = game.WINDOW
    score = 0
    clock = pygame.time.Clock()

    switch = True
    while switch:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                switch = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        # Handling all the moving funtions:
        bird.move()
        add_pipe = False
        rem = []

        for pipe in pipes:
            if pipe.collide(bird) or bird.y > 680:
                switch = False
                # end_screen(window,game)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # To generate multiple pipes
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()  # To display the pipes

        if add_pipe:
            score = score + 1
            pipes.append(Pipes(600, game))

        for r in rem:
            pipes.remove(r)

        ground.move()
        draw_window(window, bird, pipes, ground, score, game)  # They will all be displayed here
    return score
    pygame.quit()
