import math
import copy

ATK_MP_RATIO = 1/0.01
MOVE_MP_RATIO = 10/1.0
ATK_RANGE_MP_RATIO = 5/1.0

HP_PASSIVE_RATIO = 100/1
DEF_PASSIVE_RATIO = 10/1
ATK_PASSIVE_RATIO = 80/1
MP_PASSIVE_RATIO = 10/1

ATK_RATIO_UNIT = 5
MAX_ATTACK_RANGE = 6
MAX_MOVE_RANGE = 6
MAX_POS_EDGE = 12

DEF_PARAMS = 660

# transform the result of skill to attribute
def calSkillAtb(s:str):
	skill_str = s[0:30]
	# 4 status of skills
	atk_ratio = skill_str.upper().count("A")
	forward = skill_str.upper().count("F")
	backward = skill_str.upper().count("B")
	atk_range = skill_str.upper().count("R")

	return skill(atk_ratio, forward, backward, atk_range)

def calAtb(s:str):
	skill_str = s[0:30]
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
	def __init__(self, atk_ratio, forward, backward, atk_range):
		self.atk_ratio = 1 + (atk_ratio * ATK_RATIO_UNIT) / 100
		self.forward_move = forward - backward
		if(atk_range > MAX_ATTACK_RANGE):
			self.atk_range = MAX_ATTACK_RANGE
		else:
			self.atk_range = atk_range
		self.mp_cost = self.atk_ratio * ATK_MP_RATIO + abs(self.forward_move) * MOVE_MP_RATIO + self.atk_range * ATK_RANGE_MP_RATIO

class attribute:
	def __init__(self, hp:int, dfs:float, atk:int, mp:int):
		self.hp = hp
		self.mp = mp
		self.atk = atk
		self.dfs = dfs
	def show(self):
			print("hp: %d, mp: %d, atk: %d, dfs: %f" % (self.hp, self.mp, self.atk, self.dfs))

class player:
	#please fill in your character's basic ability
	def __init__(self, p:int, pid:int):
		self.__pid = pid
		self.__name = ""
		self.__atb = attribute(3000, 300, 600, 100)
		self.__pos = p
	
	def cheat(self):
		self.__atb.hp = 2

	def getName(self):
		return self.__name

	#... Must copy and pass only value instead of instances(Cuz you are not using primitive type)
	def getAtb(self):
		return copy.copy(self.__atb)

	def getPos(self):
		return self.__pos

	def getPid(self):
		return self.__pid 

	def setPassives(self, passive_str):
		attr = calAtb(passive_str)
		self.__atb.hp += attr.hp
		self.__atb.mp += attr.mp
		self.__atb.atk += attr.atk
		self.__atb.dfs += attr.dfs

	def setSkills(self, skill_str_arr):
		self.skill_set = []
		if(len(skill_str_arr) <= 4):
			skill_str_arr + ["RA"] * (4 - len(skill_str_arr))
		for idx in range(4):
			self.skill_set.append(calSkillAtb(skill_str_arr[idx]))
		# 5th skill is default attack
		self.skill_set.append(calSkillAtb("RA"))

	def setActionLambda(self, combatLogic):
		self.combatLogic = combatLogic

	def setName(self, name):
		self.__name = name

	def move(self, move, enemy):
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
		return move

	def action(self, enemy):
		skill_num = self.combatLogic(copy.deepcopy(enemy), copy.deepcopy(self))
		skill = self.skill_set[skill_num]

		mp_cost = skill.mp_cost

		# Players have base 30 temporary mp every round
		if(mp_cost <= 30):
			mp_cost = 0
		else:
			mp_cost -= 30
		
		if(self.__atb.mp < mp_cost):
			skill = self.skill_set[4]

		atk_ratio = skill.atk_ratio
		forward_move = skill.forward_move
		atk_range = skill.atk_range
		mp_cost = skill.mp_cost
		
		# convert relative movement to absolute movement
		absolute_move = forward_move * int(math.copysign(1, enemy.getPos() - self.getPos()))
		move = self.move(absolute_move, enemy)
		dmg = enemy.getHurt(self.getAtb(), self.getPos(), atk_ratio, atk_range)
		return (atk_range, move, dmg)


	# this will change the player's hp
	def getHurt(self, enemyAtb:attribute, enemyPos:int, atk_ratio:float, atk_range:int):
		print("HURT!")
		dmg = int(enemyAtb.atk * atk_ratio * (1 - self.__atb.dfs / DEF_PARAMS)) if(abs(enemyPos - self.__pos) <= atk_range) else 0
		self.__atb.hp -= dmg
		return dmg