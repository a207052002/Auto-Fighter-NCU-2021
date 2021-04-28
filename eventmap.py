from player import *
import random


class Eventmap:
    
    def __init__(self):
        self.max_pos = MAX_POS_EDGE
        self.max_size = MAX_POS_EDGE + 1
        self.mapInfo = self.max_size * [0]

    def generateEvent(self, playerPos):
        map_idx = list(range(self.max_size))
        for i in playerPos:
            map_idx.remove(i)
        event_pos = random.choice(map_idx)
        event = random.randint(1,2)
        self.mapInfo[event_pos] = event
    
    def getEventMap(self):
        return self.mapInfo.copy()
    
    def clearEvent(self, pos):
        self.mapInfo[pos] = 0