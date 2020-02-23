#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Section 3: Q-learning

import time
import pygame
import random
import \
    os  # The OS module in Python provides a way of using operating system dependent functionality (Mainly used to import image in this program)
import numpy as np
import matplotlib.pyplot as plt
from Character import *
import pickle


class Game():

    def __init__(self, character):
        pygame.init()

        # Fonts:
        self.STAT_FONT = pygame.font.SysFont("comicsans", 50)
        self.END_FONT = pygame.font.SysFont("comicsans", 40)

        # All the rewards/punishment that would be given out to the AI agent if he messes up
        self.TOP_PUN = -20
        self.BOT_PUN = -20
        self.DIE_REWARD = - 15
        self.EPISODES = 1000
        self.SCORE_REWARD = 50
        self.SKY_REWARD = -10
        self.DISCRETISATION = 10
        self.epsilon = 1  # randomness (so the AI agent have a small chance of "mutating")
        self.EPS_DECAY = 0.9999  # Every episode will be epsilon*EPS_DECAY
        self.SHOW_EVERY = 500  # how often to play through env visually. (If every frame is shown the time required to train the bird would be too inefficient )

        self.LEARNING_RATE = 0.5
        self.DISCOUNT = 0.95

        self.FRAME_WIDTH = 500
        self.FRAME_HEIGHT = 800

        self.WINDOW = pygame.display.set_mode((self.FRAME_WIDTH, self.FRAME_HEIGHT))
        pygame.display.set_caption("Flappy Crew")

        # The images should all have transparent background or else we could not use a mask for pixel perfect collision
        self.BIRD_IMAGE = [
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '1.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '2.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '3.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '1.png'))))]

        self.PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
        self.GROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
        self.BACKGROUND_IMAGE = pygame.transform.scale(
            pygame.image.load(os.path.join("background", "12.png")).convert_alpha(), (500, 800))

        self.fileName = 'qtable-1582380141.pickle'   # change this name to the pickle you want to use in the game


def appendState(state, q_table):
    # Add state to Q table if not already added
    if state not in q_table:
        q_table[state] = []
        q_table[state].append(0)
        q_table[state].append(0)


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

        # Calculating the offset (used to check the pixel up against each other) (the offset is how far away the two
        # top left corner is from each other)
        top_offset = (self.x - bird.x, self.top - round(
            bird.y))  # We need to round off bird.y as we dont need to put into consideration of decimals in this
        # game (too small to be relevant)
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
        self.y = y  # Location of the gound
        self.x1 = 0  # Two X as we are basically drawing 2 images for our base (Each X indicates where about the next
        # gound is)
        self.WIDTH = game.GROUND_IMAGE.get_width()
        self.IMAGE = game.GROUND_IMAGE
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


def main(episode, game, episode_rewards, q_table):
    bird = Character(230, 350, game)
    ground = Ground(730, game)
    pipes = [Pipes(600, game)]  # x = 700
    window = game.WINDOW
    score = 0
    clock = pygame.time.Clock()
    done = False
    render = False
    if not episode % game.SHOW_EVERY:  # if episode % show_every == 0
        print(f"on #{episode}, epsilon is {game.epsilon}")
        print(f"{game.SHOW_EVERY} ep mean: {np.mean(episode_rewards[-game.SHOW_EVERY:])}")
        render = True
    else:
        render = False
    episode_reward = 0
    while not done and score <= 150:
        clock.tick(1000000)
        reward = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
            pipe_ind = 1  # pipe on the screen for q-table input

        state = (round(abs(bird.x - pipes[pipe_ind].x - pipes[pipe_ind].PIPE_TOP.get_width()) / game.DISCRETISATION),
                 round(abs(bird.y - pipes[pipe_ind].height) / game.DISCRETISATION),
                 round(abs(bird.y - pipes[pipe_ind].bottom) / game.DISCRETISATION),
                 round(abs(bird.y - 0) / game.DISCRETISATION))

        appendState(state, q_table)

        if np.random.random() > game.epsilon:
            # Get action from Q table
            action = np.argmax(q_table[state])
        else:
            # Get random action
            action = np.random.randint(0, 2)  # either jump or do nothing

        if action == 1:
            bird.jump()

        else:
            bird.move()

        # Handling all the moving funtions:
        bird.move()
        add_pipe = False
        rem = []

        for pipe in pipes:
            if pipe.collide(bird) or bird.y > 680 or bird.y < 10:
                reward = game.DIE_REWARD
                done = True
                # end_screen(window)

            if bird.y < 10:
                reward = reward + game.SKY_REWARD
                done = True

            if bird.y == 0:
                reward = reward + game.TOP_PUN
                done = True

            if bird.y == 730:
                reward = reward + game.BOT_PUN
                done = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # To generate multiple pipes
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()  # To display the pipes

        if add_pipe:
            global s
            score += 1
            s=score
            pipes.append(Pipes(600, game))
            reward = game.SCORE_REWARD

        for r in rem:
            pipes.remove(r)

        ground.move()

        pipe_ind = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
            pipe_ind = 1  # pipe on the screen for q-table input

        new_state = (
        round(abs(bird.x - pipes[pipe_ind].x - pipes[pipe_ind].PIPE_TOP.get_width()) / game.DISCRETISATION),
        round(abs(bird.y - pipes[pipe_ind].height) / game.DISCRETISATION),
        round(abs(bird.y - pipes[pipe_ind].bottom) / game.DISCRETISATION),
        round(abs(bird.y - 0) / game.DISCRETISATION))

        appendState(new_state, q_table)

        max_future_q = np.max(q_table[new_state])
        current_q = q_table[state][action]

        if reward == game.SCORE_REWARD:
            new_q = game.SCORE_REWARD
        else:
            new_q = (1 - game.LEARNING_RATE) * current_q + game.LEARNING_RATE * (reward + game.DISCOUNT * max_future_q)
            # Question: is this the equation

        q_table[state][action] = new_q

        if render:
            draw_window(window, bird, pipes, ground, score, game)  # They will all be displayed here

        episode_reward += reward
    return episode_reward  # Question: Whta is this reward
    # pygame.quit()


def qtable(character):
    game = Game(character)
    try:
        with open(game.fileName, 'rb') as f:
            q_table = pickle.load(f)

            # Else start fresh training
    except FileNotFoundError:
        print('New Learning')
        q_table = {}

    episode_rewards = []

    for episode in range(game.EPISODES):  # each episode is one game
        print(f"episode:{episode}")
        episode_reward = main(episode, game, episode_rewards, q_table)
        episode_rewards.append(episode_reward)
        game.epsilon *= game.EPS_DECAY

    moving_avg = np.convolve(episode_rewards, np.ones((game.SHOW_EVERY,)) / game.SHOW_EVERY, mode='valid')

    # plt.plot([i for i in range(len(moving_avg))], moving_avg)
    # plt.ylabel(f"Reward {game.SHOW_EVERY}ma")
    # plt.xlabel("episode #")
    # plt.show()

    with open(f"qtable-{int(time.time())}.pickle", "wb") as f:
        pickle.dump(q_table, f)
    return s
# How can I used a pickle

s = 0