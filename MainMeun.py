import tkinter
from tkinter import *
import pygame
from AIFlappyBird import *
from OOP_FlappyBird import *
from QTable import *


# from QTable import *


# This Class is in charge of the layout of the Meun Interface and all it's relevant buttons
class Meun(tkinter.Frame):
    # The frame is setted here
    def __init__(self, master):

        tkinter.Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        # Details of the frame is initialized here
        self.master.geometry("500x800")
        self.master.title("Main Meun")
        canvas = tkinter.Canvas(self.master, bg="blue", height=800, width=500)
        self.bg_photo = tkinter.PhotoImage(file="background/12.png")
        background_label = tkinter.Label(self.master, image=self.bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # This is the start button for the player:
        self.play_btn = tkinter.Button(self.master, command=self.play_btn_click, highlightthickness=0)
        self.play_btn_photo = tkinter.PhotoImage(file="buttons/start.png")
        self.play_btn.config(image=self.play_btn_photo)
        self.play_btn.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)

        # This is the start button for the AI:
        self.start_btn = tkinter.Button(self.master, command=self.start_btn_click, highlightthickness=0)
        self.start_btn_photo = tkinter.PhotoImage(file="buttons/play.png")
        self.start_btn.config(image=self.start_btn_photo)
        self.start_btn.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        # This is the start button for the table:
        self.table_btn = tkinter.Button(self.master, command=self.table_btn_click, highlightthickness=0)
        self.table_btn_photo = tkinter.PhotoImage(file="buttons/table.png")
        self.table_btn.config(image=self.table_btn_photo)
        self.table_btn.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

        # This is the back arrow
        self.pre_btn = tkinter.Button(self.master, command=self.pre_btn_click)
        self.pre_btn_photo = tkinter.PhotoImage(file="buttons/left.png")
        self.pre_btn.config(image=self.pre_btn_photo)
        self.pre_btn.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)

        # This is the next arrow
        self.next_btn = tkinter.Button(self.master, command=self.next_btn_click)
        self.next_btn_photo = tkinter.PhotoImage(file="buttons/right.png")
        self.next_btn.config(image=self.next_btn_photo)
        self.next_btn.place(relx=0.7, rely=0.6, anchor=tkinter.CENTER)

        # Location of the character image 
        self.char_image_pos = 0
        self.char_images = []

        # Appending the images of each character into an array
        self.char_images.append(tkinter.PhotoImage(file="imgs/bird1.png"))
        self.char_images.append(tkinter.PhotoImage(file="imgs/Skull1.png"))
        self.char_images.append(tkinter.PhotoImage(file="imgs/Bat1.png"))

        self.char_label = tkinter.Label(self.master, image=self.char_images[self.char_image_pos])
        self.char_label.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
        Label(self.master, text="Score").grid(row=1, column=1)
        self.display = Label(self.master, text="")
        self.display.grid(row=2, column=1)
        # self.scoreText = tkinter.Text(self.master, height=10, width=50)  # Set the size of the character
        # for score in mergelist:
        #     self.scoreText.insert(tkinter.INSERT, str(score) + "\n")  # Quetion: what is wrong with the text box display
        # print('test')
        # self.scoreText.config(state="disable")  # So the user can't type in the text box
        # self.scoreText.pack()

    # The characters loop throught a circular list
    def pre_btn_click(self):
        if self.char_image_pos > 0:
            self.char_image_pos -= 1
            self.char_label.config(image=self.char_images[self.char_image_pos])

    # A list associating the image with a character image position:
    # 1. Bird
    # 2. Skull
    # 3. Bat

    def next_btn_click(self):
        if self.char_image_pos < len(self.char_images) - 1:
            self.char_image_pos += 1
            self.char_label.config(image=self.char_images[self.char_image_pos])

    def start_btn_click(self):

        self.master.withdraw()  # Hides window

        if self.char_image_pos == 0:
            character = "bird"
        if self.char_image_pos == 1:
            character = "Skull"
        if self.char_image_pos == 2:
            character = "Bat"

        ai_score = start(character)  # This is where the program starts the AI program from running
        mergelist.append(ai_score)
        self.updateScoreBoard()
        self.master.deiconify()  # This allows the prorgram to pop back out to the main meun after the game has finished

    def play_btn_click(self):

        self.master.withdraw()

        if self.char_image_pos == 0:
            character = "bird"
        if self.char_image_pos == 1:
            character = "Skull"
        if self.char_image_pos == 2:
            character = "Bat"

        human_score = human_play(character)  # score is returned from the main() function
        mergelist.append(human_score)
        self.updateScoreBoard()
        # printing for tkinter:
        self.master.deiconify()  # Question: What does this do exactly

    def table_btn_click(self):
        self.master.withdraw()

        if self.char_image_pos == 0:
            character = "bird"
        if self.char_image_pos == 1:
            character = "Skull"
        if self.char_image_pos == 2:
            character = "Bat"

        qtable_score = qtable(character)
        mergelist.append(qtable_score)
        self.updateScoreBoard()
        self.master.deiconify()  # Question: What does this do exactly

    def mergeSort(self, mergelist):

        if len(mergelist) > 1:
            mid = len(mergelist) // 2
            lefthalf = mergelist[:mid]
            righthalf = mergelist[mid:]
            self.mergeSort(lefthalf)
            self.mergeSort(righthalf)
            i = 0
            j = 0
            k = 0
            while i < len(lefthalf) and j < len(righthalf):
                if lefthalf[i] < righthalf[j]:
                    mergelist[k] = lefthalf[i]
                    i += 1
                else:
                    mergelist[k] = righthalf[j]
                    j += 1

                k += 1

            while i < len(lefthalf):
                mergelist[k] = lefthalf[i]
                i += 1
                k += 1

            while j < len(righthalf):
                mergelist[k] = righthalf[j]
                j += 1
                k += 1

    def updateScoreBoard(self):
        scoreboard = ''
        self.mergeSort(mergelist)
        for score in mergelist:
            scoreboard += (str(score) + '\n')
        self.display.configure(text="{}".format(scoreboard))

    # Mergelist is the score


mergelist = []  # This list stores all the score (fior the player, genetic algorithm & Q table)
# game_end = False
# Where the frame is actually called and created:
my_frame = tkinter.Tk()

my_meun = Meun(my_frame)
# root = tkinter.Tk()
# root.title("Score Board")
my_frame.mainloop()

# If (pos == 1):
# Passes another function

# For the animation:
# list1 = [1,2,3,4,5,6,7]
# for i in range (0, len.list1)
# print (list[i])
