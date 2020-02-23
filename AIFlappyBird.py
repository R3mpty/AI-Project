#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Libraries:
import pygame
import neat
import random
from Character import *
import \
    os  # The OS module in Python provides a way of using operating system dependent functionality (Mainly used to import image in this program)
import pickle


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

        self.BIRD_IMAGE = [
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '1.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '2.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '3.png')))),
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "{}".format(character + '1.png'))))]

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

    for bird in bird:
        bird.draw(window)

    score_label = game.STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(score_label, (game.FRAME_WIDTH - score_label.get_width() - 50, 10))

    pygame.display.update()


'''def end_screen(window):
    switch = True
    text_label = END_FONT.render("Press Space to Restart", 1, (255,0,0))
    while switch:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                switch = False

            if event.type == pygame.KEYDOWN:
                main()

        window.blit(text_label, (FRAME_WIDTH/2 - text_label.get_width()/2, 500))
        
        pygame.display.update()

    pygame.quit()
    quit()'''


def main(genomes, config):  # These two variables passed in so we can implement the fitness function

    nets = []  # Keeping track of the neural network and the Genomes
    ge = []
    birds = []
    game = Game(c)
    # We have to do this as gnomes is actually a tuple
    for _, g in genomes:  # Creating a neutral network for the Genomes
        g.fitness = 0  # Letting the fitness score to be 0 each generations
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Character(230, 350, game))
        ge.append(g)

    ground = Ground(730, game)
    pipes = [Pipes(600, game)]  # x = 700
    window = game.WINDOW
    score = 0
    clock = pygame.time.Clock()

    switch = True
    while switch:
        clock.tick(1000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                switch = False
                pygame.quit()
                break

            # if event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_SPACE:
            # bird.jump()

        pipe_ind = 0  # Setting the pipe index into 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # Comparing bird's X with the Pipes's coordinates to see if it has moved passed the pipe
                pipe_ind = 1

        else:
            switch = False  # Ends the game if every bird in it's genration has died
            break

        # Enumerate() method adds a counter to an iterable and returns it in a form of enumerate object.
        # This enumerate object can then be used directly in for loops or be converted into a list of tuples using list() method.

        for x, bird in enumerate(birds):
            bird.move()
            ge[
                x].fitness += 0.1  # Rewarding the bird for moving foward (only a little bit cuz this loop is being ran 30 times each seconds)
            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # I have used a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

            # output = nets[x].activate((birds))

        # Handling all the moving funtions:
        add_pipe = False
        rem = []

        for pipe in pipes:
            for x, bird in enumerate(birds):  # So we are able to keep track of the loaction of the bird
                if pipe.collide(bird):
                    ge[x].fitness = ge[
                                        x].fitness - 1  # If a bird hits a pipe, we will be removing a fitness score from that bird
                    birds.pop(x)  # This gets rid of all the variable associated with that bird
                    nets.pop(x)
                    ge.pop(x)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            text = game.STAT_FONT.render("Score " + str(score), 1, (255, 255, 255))
            window.blit(text, (game.FRAME_WIDTH - 10 - text.get_width(),
                               10))  # This allow the score to shift right and will therefore allow the score to diplay as long as requried

            pipe.move()  # To display the pipes

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # To generate multiple pipes
                rem.append(pipe)

        if add_pipe:
            score = score + 1
            for g in ge:
                g.fitness = g.fitness + 5
            pipes.append(Pipes(600, game))

        for r in rem:  # rem is the short form for remove, this is nessesary as we have to get rid of pipes that aren't displayed on screen inorder to prevent the game from lagging as it goes on
            pipes.remove(r)

        # Another form of collision detection:
        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= 730 or bird.y < 0:
                ge[x].fitness = ge[
                                    x].fitness - 1  # If a bird hits a pipe, we will be removing a fitness score from that bird
                birds.pop(x)  # This gets rid of all the variable associated with that bird
                nets.pop(x)
                ge.pop(x)

        # bird.move()
        ground.move()

        draw_window(window, birds, pipes, ground, score, game)  # They will all be displayed here
        # break if score gets large enough
        if score > 20:
             pickle.dump(nets[0], open("best.pickle", "wb"))
             break

        global s
        s = score
        #return score  # Question: why does this not pass through


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)


    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 5)  # I have changed this into 1 so that the player has a chance
    # Or I should let the user choose how many times they would allow the generation to run
    # I have no idea how to pass the character to the AI

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


def start(character):
    global c
    c = character
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'Config.txt')
    run(config_path)
    return s

c = ''
s = 0