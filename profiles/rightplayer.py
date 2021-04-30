from player import *

def passive():
    # 捏你的角色
    # 請回傳一個限定字的字串，會決定的角色的攻擊(atk)、防禦(dfs)、血量(hp)、魔力(mp)
    # 有 30 點配點，因此我們只會拿前 30 個字去用
    # 規則之外的字母會被忽略
    # 大小寫一樣
    # 你的角色起始有 3000 hp、300 dfs、600 atk、300 mp
    # "H" 代表分配 1 點給 HP，每點 + 100 HP
    # "D" 代表分配 1 點給 dfs，每點 + 10 dfs(防禦減傷率算法為 (dfs/660))
    # "A" 代表分配 1 點給 atk，每點 + 80 atk(傷害算法為 atk*(0.5+技能倍率)*(1-dfs/660))
    # "M" 代表分配 1 點給 mp，每點 + 100 mp(mp 越多可以開越強的技能)
    # 以下為簡單的範例
    # 字母順序不影響效果呈現，我們只會數對應的字母數量有多少
    # 未滿 30 或是前 30 個內有規格外字母，就代表你放棄了這些天賦點

    passive_str = "H" * 0 + "D" * 29 + "A" * 0 + "M" * 1
    return passive_str

def dis(a, b):
    return abs(a - b)

def forward(n):
    return "F" * n

def back(n):
    return "B" * n

def buff(n):
    return "A" * n

def attack(n):
    return "R" * n

def is_danger(enemy_pos, i):
    return dis(enemy_pos, i) <= 4

def combatLogic(enemy, me, eventmap):
    # 決定你的角色的自動戰鬥邏輯
    # 我們會幫你把你必須知道的資訊都先放進對應的變數，你們可以參考該變數來決定角色該怎麼動

    # eventmap 是一個跟場地大小等長的陣列(list)，每陣列裡面非 0 的數字代表場地上存在的特殊道具
    # 移動到該格會自動撿起道具
    # 以下為陣列中的數字的意義
    # 1 代表存在 P (Power shot) 撿到後可以一次性開啟無視防禦 25% - 55%(隨角色攻擊提高) 生命的無限距離大招
    # 撿到後透過 return 整數：1 來讓角色使用
    # 2 代表存在 A (Avoid) 撿到後可以一次性開啟一個 buff 持續三回合，期間無條件閃避所有攻擊
    # 以上兩個道具撿到後會存在身上直到使用，已經持有一樣的道具可以再撿但是不會額外增加數量
    # 3 代表存在 H (Heart) 撿到後可以回覆 20% 的生命(對坦克型角色有很好的效果)
    # 4 代表存在 M (Mp) 撿到後可以回覆 20% 魔力
    # 每樣道具都非常強大，並且每回合結束後有一定機率隨機產生在地圖上，建議可以考慮以道具的撿取跟使用優先

    enemy_atb = enemy.getAtb()
    my_atb = me.getAtb()

    # 敵人當前的血量、魔力、攻擊力、防禦力、位置(0-16)
    enemy_hp = enemy_atb.hp
    enemy_mp = enemy_atb.mp
    enemy_atk = enemy_atb.atk
    enemy_dfs = enemy_atb.dfs
    enemy_pos = enemy.getPos()
    enemy_avoid = enemy.avoid
    # 敵人是否持有強力攻擊(免費一次9倍無限距離免魔力的大招)
    enemy_power_shot = enemy.power_shot
    # 敵人的閃避 buff 的剩餘回合數，只要比 0 大就會必定閃避所有攻擊，每輪到敵人動一次就會少一回合
    enemy_avoiding = enemy.avoid_buff

    # 你的角色當前的血量、魔力、攻擊力、防禦力、位置(0-16)
    my_hp = my_atb.hp
    my_max_hp = my_atb.max_hp
    my_mp = my_atb.mp
    my_max_mp = my_atb.max_mp
    my_atk = my_atb.atk
    my_dfs = my_atb.dfs
    my_pos = me.getPos()

    my_avoid = me.avoid
    # 你是否持有強力攻擊(免費一次9倍無限距離免魔力的大招)
    my_power_shot = me.power_shot
    # 你的閃避 buff 的剩餘回合數，只要比 0 大就會必定閃避所有攻擊，每輪到你動一次就會少一回合
    my_avoiding = me.avoid_buff

    # 以下可以開始自由修改與決定你的 AI，上面幫你取好的資訊請盡量不要去動
    # 若回傳數字代表特殊動作如下
    # 0 是冥想，使用後會回 30 mp
    # 1 使用撿到的強力攻擊
    # 2 啟用撿到的迴避能力，持續兩回合(自己回合+敵人回合)，無視所有傷害
    # 不是以上的數字的話，會當成 0 ，冥想
    # 若回傳字串
    # 字串前 30 個字的組合將用來打造你專屬的動作
    # 大小寫一樣
    # "A": 代表攻擊力，每個 A + 5% 的傷害並且額外消耗 0.5 的 MP
    # "F": 代表移動效果，每一個 F 會讓你朝敵人移動一格，每個 F 額外消耗 10 的 MP
    # "B": 同樣移動效果，每一個 B 會讓你遠離敵人移動一格，每個 B 額外消耗 10 的 MP
    # 如果 "F" 跟 "B" 同時出現，會互相扣減。比如 "FFB" 等同於 "F"，MP 消耗也視同只有 "F"
    # "R": 代表攻擊範圍，每一個 R 會讓你該次攻擊的範圍 + 1 格，並額外消耗 5 的 MP
    # 如果沒有 "R" 代表不進行攻擊，則 "A" 也等同於沒有用
    # 移動距離的上限為 6 格
    # 攻擊距離的上限為 6 格
    # 你的技能可以同時有攻擊跟移動的效果，你的人物總是會先移動再攻擊，請善用這個特性

    # 以下為範例
    # "R" 普攻
    # "FF" 往對手的方向移動兩格
    # "BB" 遠離對手的方向移動兩格
    # "R" + "A" * 20 兩倍傷害的強力攻擊
    # "FFR" 往對手的方向跳兩格進行一次 1 格的普攻，突進攻擊的概念
    # "BBBRRRR" 遠離對手的方向跳遠後進行 4 格的普攻，風箏對手的概念
    # 以上含有 "R" 的就代表會攻擊，都可以自由加入 "A" 犧牲耗魔提高傷害
    # 請注意角色之間不能重疊，會強制落在前面一格，同時要注意被逼到角落時，要反過來利用很多 "F" 才能遠離對手

    #----------- 以下請開始撰寫你的程式
    POWER = 1
    AVOID = 2
    HEART = 3
    MP = 4

    danger_dis = 2
    mp_weight = max(5, (200 - my_mp) * 0.01)
    hp_weight = max(100, (2000 - my_hp) * 10)
    best_weight = -999999999
    danger_weight = -7000
    max_attack_dis = 6
    attack_weight = 4000
    buff_weight = 300
    power_weight = 40000
    avoid_weight = 20000
    hp_potion_weight = 43000
    base_pick_item_weight = 50000
    use_avoid_weight = 210000
    use_power_weight = 220000
    position_weight = -8000
    operation = -1
    print('MP %s  HP %s' % (my_mp,my_hp))
    print('MP weight %s  HP weight %s' % (mp_weight,hp_weight))

    def calculate_position_weight(pos):
        weight = 0
        if pos < 7 or pos > 9:
            weight = dis(pos, 8) * position_weight
        if eventmap[i] != 0:
            weight += base_pick_item_weight;
        if (not my_avoiding == 2) and is_danger(enemy_pos, i):
            weight += danger_weight
        if (not my_power_shot) and eventmap[i] == POWER:
            weight += power_weight
        elif (not my_avoid) and eventmap[i] == AVOID:
            weight += avoid_weight
        elif eventmap[i] == HEART:
            weight += hp_potion_weight
            weight += min(my_max_mp - my_hp, my_max_hp * 0.15 + 500) * hp_weight
        return weight

    def calc_weight_and_update_operation(pos, do_attack, buff_cnt):
        nonlocal best_weight
        nonlocal operation
        if do_attack and dis(pos, enemy_pos) > 6:
            return
        weight = 0
        mp_cost = dis(my_pos, pos) * 10
        if (not do_attack) and pos == my_pos:
            mp_cost = - (my_mp) / 3
        weight += calculate_position_weight(i)
        if eventmap[i] == MP:
            mp_cost -= min(my_max_mp - my_mp, my_max_mp / 5)
        attack_count = 0
        if do_attack:
            attack_count = dis(i, enemy_pos)
            mp_cost += dis(i, enemy_pos) * 10
            mp_cost += 10.0 * buff_cnt * 2 / 3
            weight += attack_weight * (buff_cnt * 10.0 + 100) / 100
            weight += buff_cnt * buff_weight
        weight -= mp_cost * mp_weight
        if mp_cost > my_mp:
            return
        if weight > best_weight:
            print('update to %s, weight %s' % (i, weight))
            best_weight = weight
            if i == my_pos:
                if attack_count != 0:
                    operation = attack(attack_count) + buff(buff_cnt)
                else:
                    operation = 0
            elif (i > my_pos and enemy_pos > my_pos) or (i < my_pos and enemy_pos < my_pos):
                operation = forward(dis(my_pos, i))
                if attack_count != 0:
                    operation += attack(attack_count) + buff(buff_cnt)
            else:
                operation = back(dis(my_pos, i))
                if attack_count != 0:
                    operation += attack(attack_count) + buff(buff_cnt)


    for i in range(0, 17):
        if dis(my_pos, i) > 6:
            continue
        if i == enemy_pos:
            continue
        calc_weight_and_update_operation(i, False, 0)
        if enemy_avoiding == 0:
            for j in range (1,3):
                calc_weight_and_update_operation(i, True, j)

    if my_avoid and my_avoiding <= 1 and dis(my_pos, enemy_pos) <= 12:
        if use_avoid_weight > best_weight:
            operation = 2
            best_weight = use_avoid_weight
    if enemy_avoiding == 0 and my_power_shot:
        if use_power_weight + calculate_position_weight(my_pos) > best_weight:
            operation = 1
            best_weight = use_power_weight + calculate_position_weight(my_pos)
    print('Best weight: %s' % best_weight)
    print('Operation: %s' % operation)
    return operation


def name():
    # 取個煞氣的名字吧，會顯示在角色上方
    name = "デバフコ"
    return name
