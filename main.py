import sys
import random

from player import *
#from profiles import kitting
#from profiles import advanceTankNPC
from profiles import *
from render import Render
from eventmap import *


MAX_POS = 16

def round(p1, p2, atkRange, move, dmg):
    print(p1.getAtb().hp, p1.getAtb().mp, p2.getAtb().hp,
          p2.getAtb().mp, atkRange, move, dmg)


def build():
    pos1, pos2 = (0, 16)
    # pos1, pos2 = random.randint(0, 5), random.randint(7, 12)
    return [player(pos1, 0), player(pos2, 1)]


if(__name__ == '__main__'):
    eventmap = Eventmap()
    p1, p2 = build()
    p1.setPassives(leftplayer.passive())
    p1.setActionLambda(leftplayer.combatLogic)
    p1.setName(leftplayer.name())

    p2.advanced()
    p2.setPassives(advanceTankNPC.passive())
    p2.setActionLambda(advanceTankNPC.combatLogic)
    p2.setName(advanceTankNPC.name())
    # p2.cheat()
    renderer = Render(eventmap.getEventMap())
    renderer.startup([p1, p2])
    

    print("player0:")
    p1.getAtb().show()
    print(p1.getPos())
    print("player1:")
    p2.getAtb().show()
    print(p2.getPos())

    finish = False

    while(not finish):
        if(random.randint(0,2) == 0 or True):
            eventmap.generateEvent([p1.getPos(), p2.getPos()])
            renderer.mapEventSet(eventmap.getEventMap())

        (atk_range, move, dmg, mp, avoid, trigger_event) = p1.action(p2, eventmap)
        round(p1, p2, atk_range, move, dmg)

        renderer.render([p1, p2], atk_range, move, dmg, mp, avoid, eventmap.getEventMap(), trigger_event)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

        if(finish):
            break

        if(random.randint(0, 2) == 0 or True):
            eventmap.generateEvent([p1.getPos(), p2.getPos()])
            renderer.mapEventSet(eventmap.getEventMap())

        (atk_range, move, dmg, mp, avoid, trigger_event) = p2.action(p1, eventmap)
        round(p1, p2, atk_range, move, dmg)

        renderer.render([p2, p1], atk_range, move, dmg, mp, avoid, eventmap.getEventMap(), trigger_event)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

    if(p1.getAtb().hp <= 0):
        print("p2 win")
        renderer.end(p2)
    else:
        print("p1 win")
        renderer.end(p1)
