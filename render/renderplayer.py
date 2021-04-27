import sys
sys.path.append('./render')
import pygame
import spritesheet
import numpy as np
from Effect import *
import pygame.freetype

def coor(t):
    return 10*t - 0.5*5*t**2

MAX_HP  =   10000
MAX_MP  =   10000
LEFT    =   -1
RIGHT   =   1


class RenderPlayer(pygame.sprite.Sprite):
    def __init__(self, horizon, max_hp, max_mp, scale=1, second=False):
        pygame.sprite.Sprite.__init__(self)
        self.ss = spritesheet.spritesheet('./render/resource/sprite_base_addon_2012_12_14.png', second)
        self.ssm = spritesheet.spritesheet('./render/resource/cat2_base.png', second)
        self.images =   {}
        self.images['meditate'] = self.ssm.load_strip((0, 0, 64, 64), 7)
        self.images['idle']   =   self.ss.load_strip((0, 0, 64, 64), 4)
        self.images['walk']  =   self.ss.load_strip((0, 64*1+1, 64, 64), 6)
        tmp =  self.ss.load_strip((0, 64*2+1, 64, 64), 8)
        self.images['jump']  = [tmp[0], tmp[1], tmp[2], tmp[3], tmp[4], tmp[5], tmp[6], tmp[7]]
        self.images['dead']   =   self.ss.load_strip((0, 64*4+1, 64, 64), 7)
        self.images['injure'] = [self.images['dead'][0],
                                self.images['dead'][1],
                                self.images['dead'][2],
                                self.images['dead'][3],
                                self.images['dead'][2],
                                self.images['dead'][1]]
        self.images['punch']  =   self.ss.load_strip((0, 64*6+1, 64, 64), 10)
        self.images['shot']   =   self.ss.load_strip((0, 64*5+1, 64, 64), 7)
        self.images['downwardkick']   =   self.ss.load_strip((0, 64*12+1, 64, 64), 8)
        self.images['roundkick'] = self.ss.load_strip((0, 64*14+1, 64, 64), 8)
        self.horizon = horizon
        self.max_hp = max_hp
        self.max_mp = max_mp
        self.hp = max_hp
        self.mp = max_mp
        self.bar_shape = (80, 16)
        self.bar = pygame.Surface(self.bar_shape)
        self.bar.fill((0,0,0))
        self.font = pygame.freetype.Font('./render/resource/TaipeiSansTCBeta-Bold.ttf', 16)
        self.effect = Effect()

        for k, v in self.images.items():
            for idx, img in enumerate(v):
                self.images[k][idx] = pygame.transform.scale(img, (64*scale, 64* scale))

        self.jumpRefer = [round(coor(x)) for x in np.linspace(0, 4, 10)]
        self.jumpRefer = np.array(self.jumpRefer) * 3

        self.state = 'idle'
        self.actionTimer = 0
        self.injureTimer = 0

        self.image  = self.images['idle'][0]
        self.rect   = self.image.get_rect()
    
    def update(self, sx, sy, action, index, toward):
        self.image = self.images[action][index]
        if(toward is LEFT):
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (sx, sy)

    def updateImg(self, action, index, toward):
        self.image = self.images[action][index]
        if(toward is LEFT):
            self.image = pygame.transform.flip(self.image, True, False)

    def setBar(self, hp, mp):
        self.hp = hp
        self.mp = mp

    def idle(self, toward):
        if(self.state != 'idle'):
            self.actionTimer = 0
            self.state = 'idle'
        self.updateImg('idle', self.actionTimer % 4, toward)
        self.actionTimer += 1

    def shortAttack(self, dx, sx, toward):
        if(self.state != 'downwardkick'):
            self.state = 'downwardkick'
            self.actionTimer = 0
            self.updateImg('downwardkick', 0, toward)
            self.actionTimer += 1
            self.effect.reset()
            return 0
        else:
            if(self.actionTimer < 8):
                self.updateImg('downwardkick', self.actionTimer, toward)
                self.actionTimer += 1
                if(self.actionTimer >= 5):
                    self.effect.swoosh(dx, sx, self.horizon)
                    if(self.actionTimer >= 7):
                        return 1
                    else:
                        return 0
                return 0
            elif(self.actionTimer >= 8 and self.actionTimer <= 14):
                if(self.actionTimer == 8):
                    self.effect.reset()
                    self.updateImg('roundkick', 3, toward)
                elif(self.actionTimer == 9):
                    self.updateImg('roundkick', 2, toward)
                else:
                    self.effect.swoosh(dx, sx, self.horizon, True)
                    self.updateImg('roundkick', self.actionTimer - 7, toward)
                self.actionTimer += 1
                return 1
            else:
                self.updateImg('idle', self.actionTimer % 4, toward)
                self.effect.reset()
                return 2

    def rangedAttack(self, dx, sx, toward):
        finish = False
        hit = False
        if(self.state != 'shot'):
            self.state = 'shot'
            self.actionTimer = 0
            self.updateImg('shot', 0, toward)
            self.actionTimer += 1
            self.effect.reset()
            return 0
        else:
            if(self.actionTimer >= 5):
                hit = self.effect.wave(dx, sx, self.horizon)
            if(self.actionTimer <= 6):
                self.updateImg('shot', self.actionTimer, toward)
            else:
                self.updateImg('idle', self.actionTimer%4, toward)
                finish = True
            if(hit and finish):
                return 2
            if(hit and not finish):
                return 1
            self.actionTimer += 1
        return 0
    
    def injure(self, damage, toward):
        if(self.state != 'injure'):
            self.effect.reset()
            self.effect.setDamage(damage)
            self.effect.DoDamage(self.rect.center[0], self.rect.center[1] - 100)
            self.state = 'injure'
            self.actionTimer = 1
            surface, rect = self.font.render(str(damage), (255, 0, 0))
            self.damage = surface.convert_alpha()
            self.image = self.images['injure'][self.actionTimer]
            if(toward is LEFT):
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            damaged = self.effect.DoDamage(self.rect.center[0], self.rect.center[1] - 100)
            if(self.actionTimer < 6):
                self.image = self.images['injure'][self.actionTimer]
                if(toward is LEFT):
                    self.image = pygame.transform.flip(self.image, True, False)
                self.actionTimer += 1
            else:
                self.image = self.images['idle'][self.actionTimer % 4]
                if(toward is LEFT):
                    self.image = pygame.transform.flip(self.image, True, False)
                self.actionTimer += 1
                return True and damaged
        return False

    def reset(self):
        self.injureTimer = 0
        self.actionTimer = 0
        self.state = 'idle'

    def meditate(self, toward, mp):
        if(self.state != 'meditate'):
            self.effect.setMPreg(mp)
            self.effect.doMP(self.rect.center[0], self.rect.center[1] - 100)
            self.state = 'meditate'
            self.actionTimer = 0
            self.updateImg('meditate', self.actionTimer, toward)
            self.actionTimer += 1
        else:
            bmp = self.effect.doMP(self.rect.center[0], self.rect.center[1] - 100)
            if(self.actionTimer < 7):
                self.updateImg('meditate', self.actionTimer, toward)
                self.actionTimer += 1
            else:
                self.updateImg('idle', 0, toward)
                self.actionTimer += 1
                return bmp
        return False

    def jump(self, dx, sx, toward):
        if(self.state != 'jump'):
            self.state = 'jump'
            self.actionTimer = 0
            self.update(sx, self.horizon, 'jump', 0, toward)
            self.actionTimer += 1
            return False
        else:
            if(self.actionTimer < 5):
                y = self.horizon - self.jumpRefer[self.actionTimer*2]
                x = round(((dx - sx)/5) * self.actionTimer) + sx
                self.update(x, y, 'jump', self.actionTimer, toward)
                self.actionTimer += 1
                return False
            else:
                y = self.horizon
                x = dx
                if(self.actionTimer > 5):
                    self.update(x, y, 'idle', self.actionTimer % 4, toward)
                else:
                    self.update(x, y, 'jump', self.actionTimer, toward)
                self.actionTimer += 1
                return True

    def setPos(self, x, toward):
        self.update(x, self.horizon, 'idle',0 , toward)
    
    def getPos(self):
        return self.rect.center

    def hud(self, screen):
        pos = self.rect.center
        pos = (pos[0] - round(self.bar_shape[0]/2), pos[1] - 38)

        self.bar.fill((0,0,0))

        hp_len = round(self.bar_shape[0] * (self.hp/self.max_hp))
        mp_len = round(self.bar_shape[0] * (self.mp/self.max_mp))
        width  = round(self.bar_shape[1]/2)
        # hp
        pygame.draw.rect(self.bar, (255, 0, 0), pygame.Rect(0, 0, hp_len, width))
        pygame.draw.rect(self.bar, (0, 0, 255), pygame.Rect(0, width+1, mp_len, width))
        screen.blit(self.bar, pos)
    def dead(self, toward):
        print(self.actionTimer, " dead")
        if(self.state != 'dead'):
            self.state = 'dead'
            self.actionTimer = 0
            self.image = self.images['dead'][self.actionTimer]
            if(toward is LEFT):
                self.image = pygame.transform.flip(self.image, True, False)
            self.actionTimer += 1
        else:
            self.image = self.images['dead'][self.actionTimer]
            if(toward is LEFT):
                self.image = pygame.transform.flip(self.image, True, False)
            x, y = self.rect.center
            self.rect.center = (x, y - 2 * toward)
            self.actionTimer += 1
            if(self.actionTimer > 6):
                return True
        return False
    def setName(self, name):
        self.name_img, rect = self.font.render(name, (0, 0, 0))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        name_width = self.name_img.get_size()[0]
        screen.blit(self.name_img, (self.rect.center[0] - round(name_width/2), self.rect.center[1] - 57))
        screen.blit(self.effect.image, self.effect.rect)
        self.hud(screen)

    

