from player import *
import random
from numpy.random import choice


class Eventmap:
    
    def __init__(self):
        self.max_pos = MAX_POS_EDGE
        self.max_size = MAX_POS_EDGE + 1
        self.mapInfo = self.max_size * [0]
        self.round = 0

    def addround(self):
        self.round += 1

    def generateEvent(self, playerPos):
        map_idx = list(range(self.max_size))
        for i in playerPos:
            map_idx.remove(i)
        for idx, i in enumerate(self.mapInfo):
            if(i > 0):
                map_idx.remove(idx)
        if(len(map_idx) != 0):
            event_pos = random.choice(map_idx)
            event = choice(list(range(1,5)), 1, p=[0.2, 0.2, 0.3, 0.3])
            if(event == 3):
                if(random.randint(1, 30) >= self.round):
                    self.addround()
                    event = random.choice([1,2,4])
            self.mapInfo[event_pos] = event
    
    def getEventMap(self):
        return self.mapInfo.copy()
    
    def clearEvent(self, pos):
        self.mapInfo[pos] = 0