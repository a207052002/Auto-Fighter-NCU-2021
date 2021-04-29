import pygame
import numpy as np
from player import *
from pygame.locals import *

from .effect import *

from .renderplayer import *

GREEN = (0,255,0) # 綠色
RED = (255,0,0) # 紅色
BLUE = (0,0,255) # 藍色
WHITE = (255,255,255) # 白色
BLACK = (0,0,0) # 黑色
YELLOW = (255,255,0) #黃色

LEFT    =   -1
RIGHT   =   1

def eventMonitor():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

class Render:
    def __init__(self, eventmap):
        pygame.init()
        width, height = 1024, 480
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Auto Fighter")
        self.screen.fill((0,0,0))
        # allsprite = pygame.sprite.Group()
        # clock = pygame.time.Clock()
        background = pygame.image.load('./render/background.png')
        self.eventmap = eventmap
        self.frameL = round(1003/17)
        self.xs = [round((1003/17)*i + (1003/17)/2)+10 for i in range(17)]
        self.background = background.convert()
        self.scale = 2
        self.fixy = 480-50-25-32-16
        self.eventy = self.fixy - 20
        self.screen.blit(self.background, [0,50])
        self.clock = pygame.time.Clock()
        self.ticks = 15
        self.mapEventEffect = []

        self.fm = FileManager()
        self.globalEffect = Effect(self.fm)


        for xcoor in self.xs:
            effect = Effect(self.fm)
            effect.setEvent(xcoor, self.eventy, 0)
            self.mapEventEffect.append(effect)


    def switchEvent(self, pos, state):
        self.mapEventEffect[pos].setEventState(state)

    def render(self, players, atkRange, move, dmg, mp, avoid, eventmap, trigger_event):
        pygame.display.update()

        self.trigger_event = trigger_event
        self.turn = players[0]
        self.oppose_avoid = avoid

        if(abs(move) > 0):
            self.wholeMove(players[0], players[0].getPos(), eventmap)
            if(trigger_event == 3):
                self.recover(trigger_event, players[0].getPid())
            if(trigger_event == 4):
                self.recover(trigger_event, players[0].getPid())
        if(atkRange > 0):
            self.wholeAttack(players[0], atkRange, dmg, players[1])
        if(mp > 0):
            self.wholeMp(players[0], mp, players[1])

        if(trigger_event == 2):
            self.triggerAvoid(players[0])

            
        return True

    def mapEventSet(self, eventmap):
        having_change = np.asarray(self.eventmap) != np.asarray(eventmap)
        for idx, ef in enumerate(self.mapEventEffect):
            if(having_change[idx]):
                x,y = ef.rect.center
                finish = False
                ef.reset()
                while(not finish):
                    finish = ef.eventDropAnimate(eventmap[idx], self.xs[idx], self.eventy)
                    self.drawBackground_s(eventmap)
                    self.draw()
                    pygame.display.update()
                    self.clock.tick(self.ticks)
        self.eventmap = eventmap
        

    def end(self, player):
        winner = self.players[player.getPid()]
        loser = self.players[(player.getPid()+1)%2]
        if(loser.rect.center[0] - winner.rect.center[0] >= 0):
            toward = LEFT
        else:
            toward = RIGHT
        finish = False
        while(not finish):
            self.drawBackground()
            self.clock.tick(self.ticks)
            finish = loser.dead(toward)
            self.draw()
            pygame.display.update()
        self.reset()
        self.win(player.getName())

    def wholeMove(self, player, pos, eventmap):
        player_id = player.getPid()
        finish = False
        while(not finish):
            eventMonitor()
            self.drawBackground()
            self.clock.tick(self.ticks)
            finish = self.move(player_id, pos)
            self.draw()
            pygame.display.update()
        self.updateStatus(player)
        if(self.eventmap[pos] is 1):
            self.players[player.getPid()].power_shot_ready = True
        elif(self.eventmap[pos] is 2):
            self.players[player.getPid()].avoid_ready = True
        self.eventmap = eventmap
        self.reset()

    def wholeAttack(self, player, atkRange, damage, oppose):
        finish = False
        while(not finish):
            eventMonitor()
            self.drawBackground()
            self.clock.tick(self.ticks)
            finish = self.attack(player, atkRange, damage, oppose)
            self.draw()
            pygame.display.update()
        self.reset()

    def startup(self, players):
        # setup player status, pos
        atbs = []
        atbs.append(players[0].getAtb())
        atbs.append(players[1].getAtb())
        self.players = []
        self.players.append(RenderPlayer(self.fm, self.fixy, atbs[0].hp, atbs[0].mp, 2))
        self.players.append(RenderPlayer(self.fm, self.fixy, atbs[1].hp, atbs[1].mp, 2, second=True))
        for idx, p in enumerate(self.players):
            p.setName(players[idx].getName())
            p.setPos(self.xs[players[idx].getPos()], -1 + idx*2)
        self.fight()
        return True

    def updateStatus(self, player):
        self.players[player.getPid()].hp = player.getAtb().hp
        self.players[player.getPid()].mp = player.getAtb().mp
        self.players[player.getPid()].power_shot_ready = player.power_shot
        self.players[player.getPid()].avoid_ready = player.avoid
        self.players[player.getPid()].avoid_buff = player.avoid_buff

    def move(self, player, pos):
        current_x = self.players[player].getPos()[0]
        oppose_x = self.players[(player+1)%2].getPos()[0]
        if(oppose_x - current_x > 0):
            toward = RIGHT
        else:
            toward = LEFT
        self.players[(player+1)%2].idle(toward*(-1))
        return self.players[player].jump(self.xs[pos], current_x, toward)

    def fight(self):
        fight_effect = Effect(self.fm)
        fight_effect.reset()
        fight_effect.setFight(round(1024/2), round(480/2))
        finish = False
        while(not finish):
            finish = fight_effect.fight()
            self.drawBackground()
            self.draw()
            fight_effect.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.ticks)

    def attack(self, player, atk_range, damage, oppose):
        current_id = player.getPid()
        oppose_id = oppose.getPid()
        current_x = self.players[current_id].getPos()[0]
        oppose_x = self.players[oppose_id].getPos()[0]
        hit = abs(atk_range * self.frameL) >= abs(oppose_x - current_x)-5
        self.updateStatus(player)
        if(not hit):
            damage = 0

        if(oppose_x - current_x > 0):
            toward = RIGHT
        else:
            toward = LEFT

        if(atk_range <= 3):
            state = self.players[current_id].shortAttack(current_x + toward * atk_range * self.frameL, current_x, toward)
        elif(atk_range <= 6):
            if(abs(atk_range * self.frameL) >= abs(oppose_x - current_x) and self.oppose_avoid == 0):
                state = self.players[current_id].rangedAttack(oppose_x, current_x, toward)
            else:
                state = self.players[current_id].rangedAttack(current_x + toward * atk_range * self.frameL, current_x, toward)
        else:
            state = self.players[current_id].powershot(oppose_x, current_x, toward)

        if(damage > 0):
            if(state == 1):
                self.players[oppose_id].injure(damage, toward*(-1))
            elif(state == 2):
                self.updateStatus(oppose)
                return True and self.players[oppose_id].injure(damage, toward*(-1))
        else:
            self.updateStatus(oppose)
            if(self.oppose_avoid > 0 and hit):
                self.players[oppose_id].avoid(toward * -1)
            else:
                self.players[oppose_id].idle(toward*(-1))
            if(state == 2):
                return True
        return False

    def triggerAvoid(self, player):
        finish = False
        current_id = player.getPid()
        current_x = self.players[current_id].getPos()[0]
        oppose_x = self.players[(current_id+1)%2].getPos()[0]
        if(oppose_x - current_x > 0):
            toward = RIGHT
        else:
            toward = LEFT
        while(not finish):
            eventMonitor()
            self.drawBackground()
            self.clock.tick(self.ticks)
            finish = self.players[current_id].avoid(toward)
            self.players[(current_id+1)%2].idle(toward*(-1))
            self.draw()
            pygame.display.update()
        self.updateStatus(player)
        self.reset()

    def wholeMp(self, player, mp, oppose):
        finish = False
        current_id = player.getPid()
        current_x = self.players[current_id].getPos()[0]
        oppose_x = self.players[(current_id+1)%2].getPos()[0]
        if(oppose_x - current_x > 0):
            toward = RIGHT
        else:
            toward = LEFT
        while(not finish):
            eventMonitor()
            self.drawBackground()
            self.clock.tick(self.ticks)
            finish = self.players[current_id].meditate(toward, mp)
            self.players[(current_id+1)%2].idle(toward*(-1))
            self.draw()
            pygame.display.update()
        self.updateStatus(player)
        self.reset()

    def idle(self, player, toward):
        self.players[player].idle(toward)

    def reset(self):
        for p in self.players:
            p.reset()
            p.effect.reset()

    def win(self, name):
        win_effect = Effect(self.fm)
        win_effect.reset()
        win_effect.setWinner(name, round(1024/2), round(480/2))
        finish = False
        while(not finish):
            finish = win_effect.win()
            self.drawBackground()
            self.draw()
            win_effect.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.ticks)

    def drawBackground_s(self, eventmap):
        self.screen.fill((0,0,0))
        self.screen.blit(self.background, [0,50])
        for idx, p in enumerate(eventmap):
            self.mapEventEffect[idx].setEventState(p)
            self.mapEventEffect[idx].selfBlit(self.screen)

    def drawBackground(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.background, [0,50])
        for idx, p in enumerate(self.eventmap):
            self.mapEventEffect[idx].setEventState(p)
            self.mapEventEffect[idx].selfBlit(self.screen)
    
    def recover(self, type, player_id):
        current_pos = self.players[player_id].getPos()
        oppose_pos = self.players[(player_id+1)%2].getPos()
        if(oppose_pos > current_pos):
            toward = RIGHT
        else:
            toward = LEFT

        finish = False
        while(not finish):
            self.drawBackground()
            self.draw()
            finish = self.players[player_id].heal(type, toward)
            pygame.display.update()
            self.clock.tick(self.ticks)
        self.players[player_id].heal_effect.reset()

    def draw(self):
        for p in self.players:
            p.draw(self.screen)
        for p in self.players:
            self.screen.blit(p.effect.image, p.effect.rect)
            self.screen.blit(p.heal_effect.image, p.heal_effect.rect)
