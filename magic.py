import sys
import random

from player import *
#from profiles import kitting
#from profiles import advanceTankNPC
from profiles import *
from render import Render
from eventmap import *

RENDER = False
MAX_POS = 16

def round(p1, p2, atkRange, move, dmg):
    print(p1.getAtb().hp, p1.getAtb().mp, p2.getAtb().hp,
          p2.getAtb().mp, atkRange, move, dmg)


def build():
    # pos1, pos2 = (0, 16)
    pos1, pos2 = random.randint(0, 7), random.randint(9, 16)
    return [player(pos1, 0), player(pos2, 1)]

def stage():
    eventmap = Eventmap()
    p1, p2 = build()
    p1.setPassives(leftplayer.passive())
    p1.setActionLambda(leftplayer.combatLogic)
    p1.setName(leftplayer.name())

    # p2.advanced()
    p2.setPassives(rightplayer.passive())
    p2.setActionLambda(rightplayer.combatLogic)
    p2.setName(rightplayer.name())
    # p2.cheat()
    if(RENDER):
        renderer = Render(eventmap.getEventMap())
        renderer.startup([p1, p2])

    finish = False

    while(not finish):
        if(random.randint(0,2) == 0):
            eventmap.generateEvent([p1.getPos(), p2.getPos()])
            if(RENDER):
                renderer.mapEventSet(eventmap.getEventMap())

        (atk_range, move, dmg, mp, avoid, trigger_event, recover) = p1.action(p2, eventmap)
        if(RENDER):
            renderer.render([p1, p2], atk_range, move, dmg, mp, avoid, eventmap.getEventMap(), trigger_event, recover)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

        if(finish):
            break

        if(random.randint(0, 2) == 0):
            eventmap.generateEvent([p1.getPos(), p2.getPos()])
            if(RENDER):
                renderer.mapEventSet(eventmap.getEventMap())

        (atk_range, move, dmg, mp, avoid, trigger_event, recover) = p2.action(p1, eventmap)
        if(RENDER):
            renderer.render([p2, p1], atk_range, move, dmg, mp, avoid, eventmap.getEventMap(), trigger_event, recover)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

    if(p1.getAtb().hp <= 0):
        # print("p2: " + p2.getName() + " win")
        if(RENDER):
            renderer.end(p2)
        return 1
    else:
        # print("p1: " + p1.getName() + " win")
        if(RENDER):
            renderer.end(p1)
        return 0

if(__name__ == '__main__'):
    ps = [0, 0]
    loop_time = 100
    while(loop_time > 0):
        result = stage()
        loop_time -= 1
        ps[result] += 1
    print(ps)