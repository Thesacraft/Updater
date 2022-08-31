import json
import os.path
import subprocess
import tkinter.messagebox
import zipfile
import shutil

import requests

class Updater():
    def __init__(self):
        self.createvars()
    def createvars(self):
        fullpath  = os.path.realpath(__file__)
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
        self.standardConfig = {"info":"U only need the id!","version":"https://drive.google.com/uc?export=download&id=","game":"https://drive.google.com/uc?export=download&id=","ForceUpdate":False,"gamefilename":"example.exe","gamefilepath":"example/example.exe","requireupdate":False,"gamename":"example"}
    def run(self):
        self.readConfig()
    def readConfig(self):
        if not os.path.exists("config.json"):
            with open("config.json","w+") as jsonFile:
                jsonFile.write(json.dumps(self.standardConfig))
        if not os.path.exists("version.txt"):
            with open("version.txt","w+") as fh:
                fh.write("0.0")
        with open("config.json","r") as jsonFile:
            jsonObject = json.load(jsonFile)
            self.gamename = jsonObject["gamename"]
            self.gamelink = jsonObject["game"]
            self.require = jsonObject["requireupdate"]
            self.gamefilepath = jsonObject["gamefilepath"]
            self.gamefilecwd = str(os.getcwd()) + "\\Application\\" + str(self.gamefilepath.replace("/"+jsonObject["gamefilename"],""))
            self.gamefilename = jsonObject["gamefilename"]
            self.versionlink = jsonObject["version"]
            self.forceUpdate = jsonObject["ForceUpdate"]
        with open("version.txt","r") as fh:
            self.version = fh.read()
        self.checkforUpdate()
    def checkforUpdate(self):
        online_version = requests.get(self.versionlink).text
        self.new_version = online_version
        if not self.version == online_version:
            print("Update Available")
            if self.forceUpdate == True:
                self.update(online_version)
            else:
                root = tkinter.Tk()
                root.withdraw()
                response = tkinter.messagebox.askquestion(title=f"{self.gamename} Updater", message=f"The Update({online_version}) of {self.gamename} is available, would you like to update?")#, **options)
                root.destroy()
                if response == "yes":
                    self.update(online_version)
                else:
                    if self.require == False:
                        self.startGame()
        else:
            self.startGame()
    def extract(self):
        print("extracting...")
        with zipfile.ZipFile("Game.zip","r")as zip_ref:
            zip_ref.extractall("Application_new")
        self.updateGame()
    def updateGame(self):
        if os.path.exists("Application"):
            shutil.rmtree("Application")
        #os.makedirs("Application")
        working_path = os.getcwd()
        print(working_path)
        shutil.copytree(r"Application_new",r"Application")
        shutil.rmtree("Application_new")
        with open("version.txt","w") as fh:
            fh.write(str(self.new_version))
        self.startGame()
    def startGame(self):
        subprocess.Popen(self.gamefilecwd+"\\"+self.gamefilename,cwd=self.gamefilecwd)
    def update(self,version):
        if os.path.exists("Application_new"):
            shutil.rmtree("Application_new")
        os.makedirs("Application_new")
        response = requests.get(self.gamelink)

        with open("Game.zip","wb") as handle:
            for data in response.iter_content(chunk_size=1024):
                if data:
                    handle.write(data)
        self.extract()
