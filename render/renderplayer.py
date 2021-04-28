import numpy as np
import pygame
import pygame.freetype

from .effect import *
from .spritesheet import SpriteSheet


def coor(t):
    return 10*t - 0.5*5*t**2

MAX_HP  =   10000
MAX_MP  =   10000
LEFT    =   -1
RIGHT   =   1


class RenderPlayer(pygame.sprite.Sprite):
    def __init__(self, horizon, max_hp, max_mp, scale=1, second=False):
        pygame.sprite.Sprite.__init__(self)
        self.ss = SpriteSheet('./render/resource/sprite_base_addon_2012_12_14.png', second)
        self.ssm = SpriteSheet('./render/resource/cat2_base.png', second)
        self.images =   {}
        self.images['meditate'] = self.ssm.load_strip((0, 0, 64, 64), 7)
        self.images['powershot'] = self.ssm.load_strip((0, 0, 64, 64), 13)
        self.images['powershot'] = list(np.repeat(self.images['powershot'], 2))
        self.images['powershot'] = self.images['powershot'][:8] + self.images['powershot'][8:12] * 3 + self.images['powershot'][12:]
        self.images['avoid'] = self.ss.load_strip((0, 64*8+1, 64, 64), 13)
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

        self.power_shot_effect = Effect()
        self.avoid_effect = Effect()
        self.avoid_buff_effect = Effect()
        self.heal_effect = Effect()
        self.power_shot_ready = False
        self.avoid_ready = False
        self.avoid_buff = 0

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

    def powershot(self, dx, sx, toward):
        hit = False
        finish = False
        if(self.state != 'powershot'):
            self.effect.reset()
            self.actionTimer = 0
            self.state = 'powershot'
            self.updateImg('powershot', self.actionTimer, toward)
            self.actionTimer += 1
        else:
            if(self.actionTimer > 20):
                hit = self.effect.powerWave(dx, sx, self.horizon)
            if(self.actionTimer < 34):
                self.updateImg('powershot', self.actionTimer, toward)
                self.actionTimer += 1
            else:
                finish = True
                self.updateImg('idle', self.actionTimer%4, toward)
                self.actionTimer += 1
        if(finish and hit):
            return 2
        elif(hit):
            return 1
        else:
            return 0


    def avoid(self, toward):
        if(self.state != 'avoid'):
            self.actionTimer = 0
            self.state = 'avoid'
            self.updateImg('avoid', self.actionTimer, toward)
            self.actionTimer += 1
        else:
            if(self.actionTimer < 13):
                if(self.actionTimer > 2):
                    (x, y) = self.rect.center
                    self.rect.center = (x, self.horizon - int((self.jumpRefer[self.actionTimer - 3])/2) )
                self.updateImg('avoid', self.actionTimer, toward)
                self.actionTimer += 1
            else:
                self.updateImg('idle', self.actionTimer%4, toward)
                self.actionTimer += 1
                return True
        return False

            
    def heal(self, type, toward):
        if(self.state != 'heal'):
            if(type == 3):
                self.effect.reset()
                self.effect.setDamage(int(self.max_hp*0.2), True)
                self.effect.DoDamage(self.rect.center[0], self.rect.center[1] - 100)
            else:
                self.effect.reset()
                self.effect.setMPreg(int(self.max_mp*0.2))
                self.effect.doMP(self.rect.center[0], self.rect.center[1] - 100)
            self.state = 'heal'
            self.actionTimer = 0
            self.updateImg('idle', self.actionTimer%4, toward)
            self.actionTimer += 1
        else:
            if(type == 3):
                healed = self.effect.DoDamage(self.rect.center[0], self.rect.center[1] - 100)
            else:
                healed = self.effect.doMP(self.rect.center[0], self.rect.center[1] - 100)
            self.updateImg('idle', self.actionTimer%4, toward)
            self.actionTimer += 1
            return self.heal_effect.doHeal(type, self.rect.center[0], self.horizon) and healed
        return False

    def injure(self, damage, toward):
        
        if(self.state != 'injure'):
            self.effect.reset()
            self.effect.setDamage(damage)
            self.effect.DoDamage(self.rect.center[0], self.rect.center[1] - 100)
            self.state = 'injure'
            self.actionTimer = 0
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

        if(self.power_shot_ready):
            self.power_shot_effect.setStatusEvent(1, pos[0] + 15, pos[1] - 30)
            self.power_shot_effect.selfBlit(screen)
        if(self.avoid_ready):
            self.avoid_effect.setStatusEvent(2, pos[0] + 40, pos[1] - 30)
            self.avoid_effect.selfBlit(screen)
        if(self.avoid_buff > 0):
            self.avoid_buff_effect.setStatusEvent(3, pos[0] + 75, pos[1] - 30)
            self.avoid_buff_effect.selfBlit(screen)
            self.avoid_buff_surface, rect = self.font.render(str(self.avoid_buff), (255, 190, 20))
            self.avoid_buff_surface = pygame.transform.scale(self.avoid_buff_surface, (14, 14)).convert_alpha()
            screen.blit(self.avoid_buff_surface, self.avoid_buff_effect.rect)
        screen.blit(self.bar, pos)
        

    def dead(self, toward):
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
            self.rect.center = (x - 2 * toward, y)
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
        # screen.blit(self.effect.image, self.effect.rect)
        self.hud(screen)

    

