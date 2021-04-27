import pygame
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

class Render:
    def __init__(self):
        pygame.init()
        width, height = 1024, 480
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Auto Fighter")
        self.screen.fill((0,0,0))
        # allsprite = pygame.sprite.Group()
        # clock = pygame.time.Clock()
        background = pygame.image.load('./render/background.png')
        self.frameL = round(988/13)
        self.xs = [round((988/13)*i + (988/13)/2)+18 for i in range(13)]
        self.background = background.convert()
        self.scale = 2
        self.fixy = 480-50-25-32-16
        self.screen.blit(self.background, [0,50])
        self.clock = pygame.time.Clock()
        self.ticks = 15

    
    def render(self, players, atkRange, move, dmg, mp):
        pygame.display.update()

        if(abs(move) > 0):
            self.wholeMove(players[0], players[0].getPos())
        if(atkRange > 0):
            self.wholeAttack(players[0], atkRange, dmg, players[1])
        if(mp > 0):
            self.wholeMp(players[0], mp, players[1])
        return True

    def end(self, player):
        winner = self.players[player.getPid()]
        loser = self.players[(player.getPid()+1)%2]
        if(loser.rect.center[0] - winner.rect.center[0] >= 0):
            toward = LEFT
        else:
            toward = RIGHT
        finish = False
        while(not finish):
            pygame.event.get()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
            self.clock.tick(self.ticks)
            finish = loser.dead(toward)
            self.draw()
            pygame.display.update()
        self.reset()
        self.win(player.getName())

    def wholeMove(self, player, pos):
        self.updateStatus(player)
        player_id = player.getPid()
        finish = False
        while(not finish):
            pygame.event.get()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
            self.clock.tick(self.ticks)
            finish = self.move(player_id, pos)
            self.draw()
            pygame.display.update()
        self.reset()

    def wholeAttack(self, player, atkRange, damage, oppose):
        finish = False
        while(not finish):
            pygame.event.get()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
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
        self.players.append(RenderPlayer(self.fixy, atbs[0].hp, atbs[0].mp, 2))
        self.players.append(RenderPlayer(self.fixy, atbs[1].hp, atbs[1].mp, 2, second=True))
        for idx, p in enumerate(self.players):
            p.setName(players[idx].getName())
            p.setPos(self.xs[players[idx].getPos()], -1 + idx*2)
        self.fight()
        return True

    def updateStatus(self, player):
        self.players[player.getPid()].hp = player.getAtb().hp
        self.players[player.getPid()].mp = player.getAtb().mp

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
        fight_effect = Effect()
        fight_effect.reset()
        fight_effect.setFight(round(1024/2), round(480/2))
        finish = False
        while(not finish):
            finish = fight_effect.fight()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
            self.draw()
            fight_effect.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.ticks)

    def attack(self, player, atk_range, damage, oppose):
        injuring = False
        current_id = player.getPid()
        current_x = self.players[current_id].getPos()[0]
        oppose_x = self.players[(current_id+1)%2].getPos()[0]
        hit = abs(atk_range * self.frameL) >= abs(oppose_x - current_x)
        self.updateStatus(player)
        if(not hit):
            damage = 0
        if(oppose_x - current_x > 0):
            toward = RIGHT
        else:
            toward = LEFT
        if(atk_range <= 3):
            state = self.players[current_id].shortAttack(current_x + toward * atk_range * self.frameL, current_x, toward)
        else:
            if(abs(atk_range * self.frameL) >= abs(oppose_x - current_x)):
                state = self.players[current_id].rangedAttack(oppose_x, current_x, toward)
            else:
                state = self.players[current_id].rangedAttack(current_x + toward * atk_range * self.frameL, current_x, toward)
        if(state >= 1):
            if(damage > 0):
                self.players[(current_id+1)%2].injure(damage, toward*(-1))
                self.updateStatus(oppose)
            if(state == 2 and damage > 0):
                injuring = True
                return True and self.players[(current_id+1)%2].injure(damage, toward*(-1))
            elif(state == 2):
                if(not injuring):
                    self.players[(current_id+1)%2].idle(toward*(-1))
                return True
        if(not injuring):
            self.players[(current_id+1)%2].idle(toward*(-1))
        return False

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
            pygame.event.get()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
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
        win_effect = Effect()
        win_effect.reset()
        win_effect.setWinner(name, round(1024/2), round(480/2))
        finish = False
        while(not finish):
            finish = win_effect.win()
            self.screen.fill((0,0,0))
            self.screen.blit(self.background, [0,50])
            self.draw()
            win_effect.draw(self.screen)
            pygame.display.update()
            self.clock.tick(self.ticks)

    def draw(self):
        for p in self.players:
            p.draw(self.screen)
