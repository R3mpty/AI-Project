import pygame


class Character:
    MAXIMUM_ROTATION = 25  # The maximum amount the bird is allow to tilt
    ROTATION_VELOCITY = 20
    ANIMATION_FRAME = 5  # Rate at which the bird flaps its bird

    def __init__(self, x, y, game):
        self.IMAGE = game.BIRD_IMAGE
        self.x = x  # x and y is the starting position of the bird
        self.y = y
        self.tilt = 0  # How much the bird is currently tilting
        self.tickcount = 0
        self.velocity = 0
        self.height = self.y
        self.image_count = 0  # To keep track of which image we are on
        self.image = self.IMAGE[0]  # To call in images in the bird images arrary

    def jump(self):
        self.velocity = -10.5  # Top left is (0,0) so negative goes up
        self.tickcount = 0  # Noting down when the bird last jump
        self.height = self.y  # Originally where the bird started

    def move(self):
        self.tickcount = self.tickcount + 1
        displacement = self.velocity * self.tickcount + 1.5 * self.tickcount ** 2  # This creates an arc for each jump of the bird

        if displacement >= 16:  # Makes sure this is the highest the bird can jump
            displacement = 16
        if displacement < 0:  # Fine tunes the jump (if we are moving upwards, move up 2 more pixels)
            displacement = displacement - 2

        self.y = self.y + displacement  # Changes bird's y position based on the displacement, making it the "initial starting point"

        # This part is done in the move section as we are trying to make the bird tilt by seeing if it's going up or down by referencing whether or not the bird is still going up or not by comparing it's current location it's starting location
        if displacement < 0 or self.y < self.height + 50:  # Judging from how it's going up, we will be tilting the bird by 50 degrees
            if self.tilt < self.MAXIMUM_ROTATION:  # If the bird is going up, we will be tilting the bird upwards
                self.tilt = self.MAXIMUM_ROTATION
        else:
            if self.tilt > -90:  # Similar to before, but since the bird is dropping it will be 90 degree completely
                self.tilt = self.tilt - self.ROTATION_VELOCITY

    def draw(self, window):
        self.image_count = self.image_count + 1  # How many times we have already shown one image

        for i in range(1, 5):
            if self.image_count < self.ANIMATION_FRAME * i:  # This all the animations for each jump
                self.image = self.IMAGE[i - 1]  # this is a list change list to Circular Queue

        if self.image_count == self.ANIMATION_FRAME * 4 + 1:
            self.image = self.IMAGE[0]
            self.image_count = 0

        if self.tilt <= -80:
            self.image = self.IMAGE[1]
            self.image_count = self.ANIMATION_FRAME * 2

        # Now to ratate the image with the information noted down in the "move" funtion above
        rotate_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotate_image.get_rect(center=self.image.get_rect(topleft=(self.x,
                                                                             self.y)).center)  # As everything in pygame starts in the top left corner, this is no exception, and we will be setting the top left as a pivot point to rotate my bird
        window.blit(rotate_image, new_rect.topleft)

    def mask(self):  # A masks figure out where the pixels of a image is
        return pygame.mask.from_surface(self.image)

    # A mask would turn pixle of an image into an array and compare the images to see if there is collision
