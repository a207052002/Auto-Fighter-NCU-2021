import pygame
from .spritesheet import SpriteSheet
import numpy as np

LEFT = -1
RIGHT = 1


class Effect(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.effects = {}
        ss = SpriteSheet('./render/resource/swoosh.png')
        tmp_arr = []
        self.effects['swoosh'] = ss.load_strip((0, 0, 32, 32), 4)
        ss = SpriteSheet('./render/resource/energy_effect_base.png')
        self.font = pygame.freetype.Font(
            './render/resource/TaipeiSansTCBeta-Bold.ttf', 25)
        self.lFont = pygame.freetype.Font(
            './render/resource/TaipeiSansTCBeta-Bold.ttf', 200)
        self.effects['wave'] = ss.load_strip((0, 32*3+1, 32, 32), 7)
        self.effects['power_wave'] = ss.load_strip((64*4+1, 0, 64, 64), 4)
        tmp_wave = ss.load_strip((64*4+1, 64*2 + 1, 64, 64), 4)
        tmp = []
        for p in self.effects['wave']:
            tmp.append(pygame.transform.scale(p, (79, 79)))
        self.effects['wave'] = tmp.copy()
        tmp = []
        for p in self.effects['power_wave']:
            tmp.append(pygame.transform.scale(p, (350, 350)))
        for p in tmp_wave:
            tmp.append(pygame.transform.scale(p, (350, 350)))
        self.effects['power_wave'] = tmp.copy()
        self.effects['avoid_event'] = pygame.image.load('./render/resource/avoid_event.png').convert_alpha()
        self.effects['avoid_event'] = pygame.transform.scale(
                self.effects['avoid_event'], (30, 30))

        self.effects['power_event'] = pygame.image.load('./render/resource/power_event.png').convert_alpha()
        self.effects['power_event'] = pygame.transform.scale(
                self.effects['power_event'], (30, 30))
        self.effects['using_avoid'] = pygame.image.load('./render/resource/power_event_using.png').convert_alpha()
        self.effects['heart'] = pygame.image.load('./render/resource/heart.png').convert_alpha()
        self.effects['heart'] = pygame.transform.scale(
                self.effects['heart'], (30, 30))
        mpss = SpriteSheet('./render/resource/potions.png')
        self.effects['mp'] = mpss.load_strip((0, 16*5+1, 16, 16), 10)[8]
        self.effects['mp'] = pygame.transform.scale(
                self.effects['mp'], (30, 30))
        healingss = SpriteSheet('./render/resource/teleporter_hit.png')
        healling_effect = []
        for idx in range(8):
            tmp = healingss.load_strip((0, 128*idx, 128, 128), 1)[0]
            healling_effect.append(tmp)
        self.effects['heal'] = healling_effect

        self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.actionTimer = 0
        self.state = 'none'

    def update(self, sx, sy, kind, index, toward, scale=1):
        if(index == -1):
            self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
            self.rect = self.image.get_rect()
        else:
            self.image = self.effect[kind][index]
            if(toward is 0):
                self.image = pygame.transform.flip(self.image, True, False)
            self.image = pygame.transform.scale(
                self.image, tuple(np.array(self.image.get_size()) * scale))
            self.rect = self.image.get_rect()
            self.recr.center(sx, sy)

    def reset(self):
        self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        self.actionTimer = 0

    def swoosh(self, dx, sx, horizon, upsidedown=False):
        if(dx - sx):
            offset = 1
        else:
            offset = -1
        self.image = pygame.transform.scale(
            self.effects['swoosh'][self.actionTimer], (round(abs(dx-sx)*1.3), 79))
        width = self.image.get_size()[0]
        self.rect.center = (round((dx + sx)/2) -
                            round(width*0.4) * offset, horizon - round(76/2))
        if(dx - sx < 0):
            self.image = pygame.transform.flip(self.image, True, False)
        if(upsidedown):
            self.image = pygame.transform.flip(self.image, False, True)
        if(self.actionTimer >= 3):
            self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
            return True
        self.actionTimer += 1
        return False

    def wave(self, dx, sx, horizon):
        self.image = pygame.transform.scale(
            self.effects['wave'][self.actionTimer % 4], (64, 64))
        if(dx - sx < 0):
            dx += 20
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            dx -= 20
        if(self.actionTimer < 7):
            size_x = int(self.image.get_size()[0]/2)
            self.rect.center = (sx + round((dx - sx)/6)
                                * self.actionTimer - size_x, horizon)
        if(self.actionTimer >= 7 and self.actionTimer < 9):
            self.image = pygame.transform.scale(
                self.effects['wave'][self.actionTimer - 2], (64, 64))
            if(dx - sx < 0):
                self.image = pygame.transform.flip(self.image, True, False)
            self.actionTimer += 1
            return True
        elif(self.actionTimer >= 9):
            self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
            return True
        self.actionTimer += 1
        return False

    def powerWave(self, dx, sx, horizon):
        self.second_statge = 0
        self.image = self.effects['power_wave'][self.actionTimer % 4]
        if(dx - sx < 0):
            self.image = pygame.transform.flip(self.image, True, False)
            toward = -1
        else:
            toward = 1
        size_y, size_x = self.image.get_size()
        self.rect.center = (sx + 60 * self.actionTimer * toward - int(size_x/2), horizon - int(size_y/2))
        self.actionTimer += 1
        if(self.actionTimer >= 19):
            return True
        return False
        



    def setDamage(self, damage, heal=False):
        if(heal):
            surface, rect = self.font.render(str(damage), (40, 255, 0))
        else:
            surface, rect = self.font.render(str(damage), (255, 0, 0))
        self.damage = surface.convert_alpha()

    def DoDamage(self, x, y):
        if(self.actionTimer <= 10):
            self.image = self.damage
            width = self.image.get_size()[0]
            self.rect.center = (x - round(width/2), y - self.actionTimer * 2)
            self.image.fill(
                (255, 255, 255, 255 - round((self.actionTimer/10)*255)), None, pygame.BLEND_RGBA_MULT)
            self.actionTimer += 1
            return False
        else:
            return True

    def setMPreg(self, mp):
        surface, rect = self.font.render(str(mp), (0, 0, 255))
        self.mp = surface.convert_alpha()

    def doMP(self, x, y):
        if(self.actionTimer <= 10):
            self.image = self.mp
            width = self.image.get_size()[0]
            self.rect.center = (x - round(width/2), y - self.actionTimer * 2)
            self.image.fill(
                (255, 255, 255, 255 - round((self.actionTimer/10)*255)), None, pygame.BLEND_RGBA_MULT)
            self.actionTimer += 1
            return False
        else:
            return True

    def doHeal(self, type, x, y):
        if(self.actionTimer > 6):
            return True
        else:
            self.image = self.effects['heal'][self.actionTimer+1]
        if(type == 3):
            self.image.fill((90, 220, 50, 255), None, pygame.BLEND_RGBA_MULT)
        size_x, size_y = self.image.get_size()
        self.rect.center = (x - int(size_x/2) + 5, y - 60)
        self.actionTimer += 1
        return False

    def setWinner(self, name, x, y):
        self.standardCenter = (x, y)
        winImage, rect = self.lFont.render(name + " WIN!", (255, 20, 20))
        self.winImage = winImage.convert_alpha()
        self.winImage = pygame.transform.scale(self.winImage, tuple(
            np.rint(np.array(self.winImage.get_size()) / 3).astype(int)))

    def win(self):
        self.image = self.winImage
        if((self.actionTimer // 4) % 3 == 1):
            self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        else:
            self.image = self.winImage
        rectSize = self.image.get_size()
        self.rect.center = self.certralize(self.standardCenter, rectSize)
        self.actionTimer += 1
        if(self.actionTimer >= 100):
            return True
        return False

    def setFight(self, x, y):
        self.standardCenter = (x, y)
        readyImage, rect = self.lFont.render("Ready", (255, 20, 20))
        fightImage, rect = self.lFont.render("FIGHT", (255, 20, 20))
        self.readyImage = readyImage.convert_alpha()
        self.fightImage = fightImage.convert_alpha()
        self.readySize = self.readyImage.get_size()
        self.fightSize = self.fightImage.get_size()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def certralize(self, coor, rsize):
        xs = round(rsize[0]/2)
        ys = round(rsize[1]/2)
        return (coor[0] - xs, coor[1] - ys)

    def fight(self):
        if(self.actionTimer <= 7):
            self.image = self.readyImage
            self.image = pygame.transform.scale(self.image, tuple(
                np.rint(np.array(self.readySize) * (1 + (7-self.actionTimer) / 7)).astype(int)))
            self.image.fill((255, 255, 255, round(
                255*(self.actionTimer / 7))), None, pygame.BLEND_RGBA_MULT)
            rectSize = self.image.get_size()
            self.rect.center = self.certralize(self.standardCenter, rectSize)
        elif(self.actionTimer > 7 and self.actionTimer <= 12):
            if(self.actionTimer > 9):
                self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        elif(self.actionTimer > 12 and self.actionTimer <= 19):
            self.image = self.fightImage
            self.image = pygame.transform.scale(self.image, tuple(np.rint(
                np.array(self.fightSize) * (1 + (7-(self.actionTimer - 13)) / 7)).astype(int)))
            self.image.fill((255, 255, 255, round(
                255*((self.actionTimer - 13) / 7))), None, pygame.BLEND_RGBA_MULT)
            rectSize = self.image.get_size()
            self.rect.center = self.certralize(self.standardCenter, rectSize)
        elif(self.actionTimer >= 20):
            self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
            return True
        self.actionTimer += 1
        return False

    def setEvent(self, x, y, event):
        size_x, size_y = 30, 30
        if(event is 1):
            self.image = self.effects['power_event']
        elif(event is 2):
            self.image = self.effects['avoid_event']
        else:
            self.image = pygame.Surface([56, 50], pygame.SRCALPHA)
        self.rect.center = (x - int(size_x/2), y + 35)

    def setEventState(self, event):
        if(event == 1):
            self.image = self.effects['power_event']
        elif(event == 2):
            self.image = self.effects['avoid_event']
        elif(event == 3):
            self.image = self.effects['heart']
        elif(event == 4):
            self.image = self.effects['mp']
        else:
            self.image = pygame.Surface([56, 50], pygame.SRCALPHA)
    def setStatusEvent(self, event, x, y):

        if(event == 1):
            self.image = self.effects['power_event']
        elif(event == 2):
            self.image = self.effects['avoid_event']
        elif(event == 3):
            self.image = self.effects['using_avoid']

        self.image = pygame.transform.scale(self.image, (25, 25))
        (size_x, size_y) = self.image.get_size()
        self.rect.center = (x - int(size_x/2), y - int(size_y/2))
    
    def selfBlit(self, screen):
        screen.blit(self.image, self.rect)