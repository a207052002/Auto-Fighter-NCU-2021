import copy
import math

ATK_MP_RATIO = 0.1/1.0
MOVE_MP_RATIO = 10/1.0
ATK_RANGE_MP_RATIO = 5/1.0

HP_PASSIVE_RATIO = 100/1
DEF_PASSIVE_RATIO = 10/1
ATK_PASSIVE_RATIO = 80/1
MP_PASSIVE_RATIO = 10/1

ATK_RATIO_UNIT = 5
MAX_ATTACK_RANGE = 6
MAX_MOVE_RANGE = 6
MAX_POS_EDGE = 16

MAX_PASSIVES_NPC = 50
MAX_PASSIVES_PLAYER = 30
DEF_PARAMS = 660

TEMP_MP = 30

REG_MP_ACTION = 0
USING_POWER_SHOT = 1
USING_AVOID = 2

AVOID_ROUND = 4

# transform the result of skill to attribute


def calSkillAtb(s: str):
    skill_str = s
    # 4 status of skills
    atk_count = skill_str.upper().count("A")
    forward = skill_str.upper().count("F")
    backward = skill_str.upper().count("B")
    atk_range = skill_str.upper().count("R")

    return skill(atk_count, forward, backward, atk_range)


def calAtb(s: str, max_p):
    skill_str = s[:max_p]
    hp = skill_str.upper().count("H") * HP_PASSIVE_RATIO
    dfs = skill_str.upper().count("D") * DEF_PASSIVE_RATIO
    atk = skill_str.upper().count("A") * ATK_PASSIVE_RATIO
    mp = skill_str.upper().count("M") * MP_PASSIVE_RATIO

    return attribute(hp, dfs, atk, mp)


''' you can simply "a" * n
def rep(n, c):
    res = ''
    for i in range(n):
        res += c
    return res
'''


class skill():
    def __init__(self, atk_count=0, forward=0, backward=0, atk_range=0, mp_reg=0, special=False, avoid=False):
        self.atk_ratio = 1 + (atk_count * ATK_RATIO_UNIT) / 100
        self.forward_move = forward - backward
        if(atk_range > MAX_ATTACK_RANGE and not special):
            self.atk_range = MAX_ATTACK_RANGE
        else:
            self.atk_range = atk_range
        if(atk_range == 0):
            atk_mp_offset = 0
        else:
            atk_mp_offset = 1
        self.mp_cost = atk_count * ATK_RATIO_UNIT * ATK_MP_RATIO * atk_mp_offset + \
            abs(self.forward_move) * MOVE_MP_RATIO + \
            self.atk_range * ATK_RANGE_MP_RATIO
        self.mp_reg = mp_reg
        self.mp_cost += 10
        if(special):
            self.mp_cost = 0
        self.avoid = avoid


class attribute:
    def __init__(self, hp: int, dfs: float, atk: int, mp: int):
        self.hp = hp
        self.mp = mp
        self.atk = atk
        self.dfs = dfs
        self.max_hp = hp
        self.max_mp = mp

    def show(self):
        print("hp: %d, mp: %d, atk: %d, dfs: %f" %
              (self.hp, self.mp, self.atk, self.dfs))


class player:
    # please fill in your character's basic ability
    def __init__(self, p: int, pid: int):
        self.__pid = pid
        self.__name = ""
        self.__atb = attribute(3000, 300, 600, 300)
        self.__pos = p
        self.__max_passive = MAX_PASSIVES_PLAYER

        self.avoid_buff = 0
        self.power_shot = False
        self.avoid = False

        self.__special_actions = []
        self.__special_actions.append(skill(0, 0, 0, 0, 25))
        self.__special_actions.append(skill(400, 0, 0, 25, 0, True))
        self.__special_actions.append(skill(0, 0, 0, 0, 0, True, True))


    def advanced(self):
        self.__max_passive = MAX_PASSIVES_NPC

    def cheat(self):
        self.__atb.hp = 2

    def getName(self):
        return self.__name

    # ... Must copy and pass only value instead of instances(Cuz you are not using primitive type)
    def getAtb(self):
        return copy.copy(self.__atb)

    def getPos(self):
        return self.__pos

    def getPid(self):
        return self.__pid

    def setPassives(self, passive_str):
        attr = calAtb(passive_str, self.__max_passive)
        self.__atb.hp += attr.hp
        self.__atb.mp += attr.mp
        self.__atb.atk += attr.atk
        self.__atb.dfs += attr.dfs
        self.__atb.max_hp = self.__atb.hp
        self.__atb.max_mp = self.__atb.mp

    ''' canceled
    def setSkills(self, skill_str_arr):
        self.skill_set = []
        if(len(skill_str_arr) <= 4):
            skill_str_arr + ["RA"] * (4 - len(skill_str_arr))
        for idx in range(4):
            self.skill_set.append(calSkillAtb(skill_str_arr[idx]))
        # 5th skill is default attack
        self.skill_set.append(calSkillAtb("RA"))
        self.skill_set.append(skill(mp_reg=30))
    '''

    def setActionLambda(self, combatLogic):
        self.combatLogic = combatLogic

    def setName(self, name):
        self.__name = name

    def move(self, move, enemy, event_map):
        # limitation and edge inspection
        if(abs(move) > MAX_MOVE_RANGE):
            move -= int(math.copysign(MAX_MOVE_RANGE - abs(move), move))
        if(self.__pos + move > MAX_POS_EDGE):
            move = MAX_POS_EDGE - self.__pos
        if(self.__pos + move < 0):
            move = 0 - self.__pos

        enemyPos = enemy.getPos()
        # overlapping is not allowed
        if(enemyPos == self.__pos + move):
            move -= int(math.copysign(1, move))
        self.__pos += move

        mapinfo = event_map.getEventMap()
        if(mapinfo[self.__pos] == 1):
            self.power_shot = True
            event_map.clearEvent(self.__pos)
        elif(mapinfo[self.__pos] == 2):
            self.avoid = True
            event_map.clearEvent(self.__pos)
        elif(mapinfo[self.__pos] == 3):
            self.__atb.hp += int(self.__atb.max_hp * 0.2)
            event_map.clearEvent(self.__pos)
        elif(mapinfo[self.__pos] == 4):
            self.__atb.mp += int(self.__atb.max_mp * 0.2)
            event_map.clearEvent(self.__pos)
        
        self.trigger_event = mapinfo[self.__pos] if self.trigger_event != 2 else 0

        return move

    def action(self, enemy, event_map):
        
        skill_str = self.combatLogic(copy.deepcopy(enemy), copy.deepcopy(self), event_map.getEventMap())
        intRet = isinstance(skill_str, int)
        strRet = isinstance(skill_str, str)
        assert intRet or strRet, "角色戰鬥邏輯回應了錯誤的類型，必須是字串或整數"
        self.trigger_event = 0
        if(intRet):
            if(skill_str is 1 and self.power_shot):
                print("select power shot")
                actionAttr = self.__special_actions[skill_str]
                self.power_shot = False
            elif(skill_str is 2 and self.avoid):
                actionAttr = self.__special_actions[skill_str]
                self.avoid = False
            else:
                actionAttr = self.__special_actions[0]
        else:
            actionAttr = calSkillAtb(skill_str)

        # skill = self.skill_set[skill_str]
        actual_mp_reg = 0
        if(actionAttr.mp_reg > 0):
            actual_mp_reg = (actionAttr.mp_reg / 100) * self.__atb.max_mp
            actual_mp_reg = int(actual_mp_reg)
            self.__atb.mp += actual_mp_reg

        mp_cost = actionAttr.mp_cost

        # Players have base 30 temporary mp every round
        if(mp_cost <= TEMP_MP):
            mp_cost = 0
        else:
            mp_cost -= TEMP_MP
        if(self.__atb.mp < mp_cost):
            actionAttr = self.__special_actions[0]

        atk_ratio = actionAttr.atk_ratio
        forward_move = actionAttr.forward_move
        atk_range = actionAttr.atk_range

        if(actionAttr.avoid):
            self.avoid_buff = AVOID_ROUND
            self.trigger_event = 2

        self.__atb.mp -= mp_cost

        # convert relative movement to absolute movement
        absolute_move = forward_move * \
            int(math.copysign(1, enemy.getPos() - self.getPos()))
        move = self.move(absolute_move, enemy, event_map)
        self.buffExpire()
        dmg = enemy.getHurt(self.getAtb(), self.getPos(), atk_ratio, atk_range)
        
        print("atk range: ", atk_range, ", dmg: ", dmg)
        return (atk_range, move, dmg, actual_mp_reg, enemy.avoid_buff, self.trigger_event)
    
    def buffExpire(self):
        if(self.avoid_buff > 0):
            self.avoid_buff -= 1

    # this will change the player's hp
    def getHurt(self, enemyAtb: attribute, enemyPos: int, atk_ratio: float, atk_range: int):
        dmg = int(enemyAtb.atk * (atk_ratio + 0.5) * (1 - self.__atb.dfs /
                  DEF_PARAMS)) if(abs(enemyPos - self.__pos) <= atk_range) else 0
                  
        if(self.avoid_buff > 0):
            dmg = 0

        self.__atb.hp -= dmg
        return dmg
