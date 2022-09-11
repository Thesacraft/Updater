# importing

import json
import os.path
import shutil
import subprocess
import threading
import time
import tkinter.messagebox
import urllib.request
import zipfile
from tkinter import *
from tkinter.ttk import *

import requests


# defining the Class

class Updater():
    def __init__(self):  # innit function calling the functions for setup
        self.createvars()

    def createvars(self):  # Creating the variables
        fullpath = os.path.realpath(__file__)
        cwd = os.getcwd()
        filename = os.path.split(fullpath)
        if not cwd == filename[0]:
            os.chdir(filename[0])
        self.gamelink = ""
        self.versionlink = ""
        self.forceUpdate = False
        self.Update = False
        self.version = 0.0
        self.gamefile = ""
        self.standardConfig = {"info": "You only need the id!",
                               "version": "https://drive.google.com/uc?export=download&id=",
                               "game": "https://drive.google.com/uc?export=download&id=", "ForceUpdate": False,
                               "gamefilename": "example.exe", "gamefilepath": "example/example.exe",
                               "requireupdate": False, "gamename": "example"}

    def run(self):  # Runs the whole thing
        self.readConfig()

    def createGUI(self):  # Creates the GUI
        self.root = Tk()
        self.root.title(f"{self.gamename} Updater")
        self.Label = Label(self.root, text="Checking for Updates")
        self.Label.pack(pady=10)
        self.progress = Progressbar(self.root, orient=HORIZONTAL, length=200, mode="determinate")
        self.progress.pack(expand=True)
        self.progress["value"] = 0
        self.root.mainloop()

    def readConfig(self):  # Reads the config
        if not os.path.exists("config.json"):  # Checks if the config exists
            with open("config.json", "w+") as jsonFile:
                jsonFile.write(json.dumps(self.standardConfig))
        if not os.path.exists("version.txt"):  # Checks if the version file exists
            with open("version.txt", "w+") as fh:
                fh.write("0.0")
        with open("config.json", "r") as jsonFile:  # exits if the config file is the standard config
            jsonObject = json.load(jsonFile)
            if jsonObject == self.standardConfig:
                root = Tk()
                root.withdraw()
                tkinter.messagebox.showerror(title="Updater", message="You must configure the config first!")
                exit()
            self.gamename = jsonObject["gamename"]
            self.gamelink = jsonObject["game"]
            self.require = jsonObject["requireupdate"]
            self.gamefilepath = jsonObject["gamefilepath"]
            self.gamefilecwd = str(os.getcwd()) + "\\Application\\" + str(
                self.gamefilepath.replace("/" + jsonObject["gamefilename"], ""))
            self.gamefilename = jsonObject["gamefilename"]
            self.versionlink = jsonObject["version"]
            self.forceUpdate = jsonObject["ForceUpdate"]

        with open("version.txt", "r") as fh:
            self.version = fh.read()
        # self.checkforUpdate()
        new_thread = threading.Thread(target=self.checkforUpdate)  # activates threading
        new_thread.daemon = True
        new_thread.start()
        self.createGUI()  # creates the gui on the main thread

    def checkforUpdate(self):  # checks for updates
        online_version = requests.get(self.versionlink).text
        self.new_version = online_version
        if not self.version == online_version:
            print("Update Available")
            self.Label["text"] = "Update Available"
            if self.forceUpdate == True:
                self.update()

            else:
                response = tkinter.messagebox.askquestion(title=f"{self.gamename} Updater",
                                                          message=f"The Update({online_version}) of {self.gamename} is available, would you like to update?")  # , **options)
                if response == "yes":
                    self.update()

                else:
                    if self.require == False:
                        self.startGame()
                    self.root.destroy()
        else:
            self.startGame()

    def extract(self):  # extracts the zip file
        print("extracting...")
        self.Label["text"] = "extracting"
        with zipfile.ZipFile("game.zip", "r") as zip_ref:
            zip_ref.extractall("Application_new")
        self.progress["value"] = 90
        os.remove("game.zip")
        self.updateGame()

    def updateGame(self):  # updates the game folder
        self.Label["text"] = "Copying Files"
        if os.path.exists("Application"):
            shutil.rmtree("Application")
        # os.makedirs("Application")
        working_path = os.getcwd()
        print(working_path)
        self.progress["value"] = 95

        shutil.copytree(r"Application_new", r"Application")
        self.Label["text"] = "Cleaning Up"
        shutil.rmtree("Application_new")
        with open("version.txt", "w") as fh:
            fh.write(str(self.new_version))
        self.progress["value"] = 100
        self.startGame()

    def startGame(self):  # Starts the game
        subprocess.Popen(self.gamefilecwd + "\\" + self.gamefilename, cwd=self.gamefilecwd)
        time.sleep(0.3)
        self.root.destroy()

    def fileSize(self):  # Updates the gui progressbar
        i = os.path.getsize('game.zip')
        i_before = 0
        while i < self.file_size:
            if i_before < i:
                inter = (self.file_size / i)
                step = 100.0 - inter
                step = step * 0.5
                self.progress["value"] = step
            i = os.path.getsize('game.zip')

    def update(self, version=True):  # handles the download
        print(self.new_version)
        self.Label["text"] = f"Downloading Update v{self.new_version}"
        if os.path.exists("Application_new"):
            shutil.rmtree("Application_new")
        os.makedirs("Application_new")
        response = requests.get(self.gamelink)
        file = urllib.request.urlopen(self.gamelink)
        self.file_size = file.length
        with open("game.zip", "wb") as handle:
            thread = threading.Thread(target=self.fileSize)
            thread.daemon = True
            thread.start()
            for data in response.iter_content(chunk_size=1024):
                if data:
                    handle.write(data)
        self.extract()
