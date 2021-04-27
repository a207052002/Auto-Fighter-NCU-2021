import sys
sys.path.append('./render')
sys.path.append('./profiles')
import random
from Render import *
from player import *
import leftplayer
import rightplayer
import standardNPC

# import player


def round(p1, p2, atkRange, move, dmg):
    print(p1.getAtb().hp, p1.getAtb().mp, p2.getAtb().hp,
          p2.getAtb().mp, atkRange, move, dmg)


def build():
    pos1, pos2 = random.randint(0, 5), random.randint(7, 12)
    return [player(pos1, 0), player(pos2, 1)]


if(__name__ == '__main__'):
    p1, p2 = build()
    p1.setPassives(leftplayer.passive())
    p1.setSkills(leftplayer.skill_set())
    p1.setActionLambda(leftplayer.combatLogic)
    p1.setName(leftplayer.name())

    p2.setPassives(standardNPC.passive())
    p2.setSkills(standardNPC.skill_set())
    p2.setActionLambda(standardNPC.combatLogic)
    p2.setName(standardNPC.name())
    p2.cheat()
    renderer = Render()
    renderer.startup([p1, p2])

    print("player0:")
    p1.getAtb().show()
    print(p1.getPos())
    print("player1:")
    p2.getAtb().show()
    print(p2.getPos())

    finish = False

    while(not finish):
        (atk_range, move, dmg) = p1.action(p2)
        round(p1, p2, atk_range, move, dmg)
        print(p1.getPos(), p2.getPos())
        renderer.render([p1, p2], atk_range, move, dmg)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

        if(finish):
            break

        (atk_range, move, dmg) = p2.action(p1)
        round(p1, p2, atk_range, move, dmg)
        print(p1.getPos(), p2.getPos())
        renderer.render([p2, p1], atk_range, move, dmg)

        finish = p1.getAtb().hp <= 0 or p2.getAtb().hp <= 0

    if(p1.getAtb().hp <= 0):
        print("p2 win")
        renderer.end(p2)
    else:
        print("p1 win")
        renderer.end(p1)
