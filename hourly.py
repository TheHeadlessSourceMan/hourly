"""
Tool to generate hourly chimes
"""
import typing
import time
import random
import json
import datetime
from tkinter import messagebox


class HourlyItem:
    """
    A single item that can come up in an hourly chime
    """
    def __init__(self,
        soundFile:str='',
        message:str='',
        jsonData:typing.Dict=None,
        jsonFile:str=''):
        """ """
        self._watchThread:typing.Optional[typing.Any]=None
        self.randomWeight=1.0
        self.soundFile=soundFile
        self.message=message
        if jsonData is not None:
            self.jsonData=jsonData
        if jsonFile:
            self.load(jsonFile)

    @property
    def jsonData(self):
        """
        This object as json
        """
        return {} # later
    @jsonData.setter
    def jsonData(self,jsonData):
        if isinstance(jsonData,str):
            jsonData=json.loads(jsonData)
        self.soundFile=jsonData.get("soundFile","")
        self.message=jsonData.get("message","")
        self.randomWeight=float(jsonData.get("randomWeight","1.0"))

    def __call__(self):
        """
        Run this item
        """
        if self.soundFile:
            print("TODO: play sound")
        if self.message:
            print(self.message)
            messagebox.showwarning("Hourly Task",self.message)
    def doit(self):
        """
        Run this item
        """
        self()

    def unwatch(self):
        """
        stop watching the current file
        """
        if self._watchThread is not None:
            self._watchThread.stop() # pylint: disable=no-member
            self._watchThread=None

    def watch(self,filename:str):
        """
        Watch a file and reaload if it changes
        """
        from paths.fileWatch import watchForFileChange,FileChange
        def _onFileChange(change:FileChange):
            self.load(change.filename,andSetWatch=False)
        self.unwatch()
        self._watchThread=watchForFileChange(filename,_onFileChange)

    def load(self,filename:str,andSetWatch:bool=True):
        """
        Load object from a file
        """
        with open(filename,"r",encoding="utf-8") as f:
            if andSetWatch:
                self.watch(str)
            self.jsonData=f.read()

    def __repr__(self)->str:
        return f"{self.message}"


class HourlyItemSet:
    """
    A set of hourly items
    """

    def __init__(self):
        self.randomize:bool=False
        self.items:typing.List[HourlyItem]=[]
        self._nextHourlyItemIdx:int=0

    def weightToIdx(self,weight:float)->int:
        """
        Convert a weight to an item index
        """
        total=0
        for i,item in enumerate(self.items):
            total+=item.randomWeight
            if total>=weight:
                if i<0:
                    return 0
                return i
        return 0

    def getNextItem(self)->HourlyItem:
        """
        Get the next item (either consecutive or weighted random)
        """
        item=self.items[self._nextHourlyItemIdx]
        if self.randomize:
            weightIdx=random.random()*self.totalRandomWeight
            self._nextHourlyItemIdx=self.weightToIdx(weightIdx)
        else:
            self._nextHourlyItemIdx=self._nextHourlyItemIdx+1%len(self.items)
        return item

    @property
    def totalRandomWeight(self)->float:
        """
        Total weight of all items combined
        """
        total=0.0
        for item in self.items:
            total+=item.randomWeight
        return total


class HourlyChime(HourlyItemSet):
    """
    Tool to generate hourly chimes
    """
    def __init__(self,
        relativeMinutes:int=-5,
        items:typing.Iterable[HourlyItem]=(),
        randomize:bool=False,
        jsonData:typing.Dict=None,
        jsonFile:str=''):
        """ """
        HourlyItemSet.__init__(self)
        self.relativeMinutes=relativeMinutes
        self.randomize=randomize
        self.items=list(items)
        if jsonData is not None:
            self.jsonData=jsonData
        if jsonFile:
            self.load(jsonFile)

    @property
    def jsonData(self):
        """
        This object as jsom
        """
        return {} # later
    @jsonData.setter
    def jsonData(self,jsonData):
        if isinstance(jsonData,str):
            jsonData=json.loads(jsonData)
        self.relativeMinutes=int(jsonData.get("minutes",-5))
        self.randomize=jsonData.get("randomize","f")[0] in ('f','F')
        self.items=[]
        for itemData in jsonData["items"]:
            self.items.append(HourlyItem(jsonData=itemData))

    def load(self,filename:str):
        """
        Load this object from json file
        """
        with open(filename,"r",encoding="utf-8") as f:
            self.jsonData=f.read()

    def loop(self):
        """
        Loop forever doing hourly chimes
        """
        while True:
            now=datetime.datetime.now()
            nextTime=datetime.datetime(
                year=now.year,month=now.month,day=now.day,
                hour=now.hour+1,minute=0,second=now.second)
            nextTime=nextTime+datetime.timedelta(minutes=self.relativeMinutes)
            delta=nextTime-now
            while delta.total_seconds()<=0:
                nextTime=nextTime+datetime.timedelta(hours=1)
                delta=nextTime-now
            sec=delta.total_seconds()
            print(f"*** now={now} next={nextTime} in {sec}s ***")
            time.sleep(delta.total_seconds())
            item=self.getNextItem()
            item()


c=HourlyChime(jsonFile="hourly.json")
c.loop()
