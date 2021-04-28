from player import *

def passive():
    # 捏你的角色
    # 請回傳一個限定字的字串，會決定的角色的攻擊(atk)、防禦(dfs)、血量(hp)、魔力(mp)
    # 有 30 點配點，因此我們只會拿前 30 個字去用
    # 規則之外的字母會被忽略
    # 大小寫一樣
    # 你的角色起始有 3000 hp、300 dfs、600 atk、100 mp
    # "H" 代表分配 1 點給 HP，每點 + 100 HP
    # "D" 代表分配 1 點給 dfs，每點 + 10 dfs(防禦減傷率算法為 (dfs/660))
    # "A" 代表分配 1 點給 atk，每點 + 80 atk(傷害算法為 atk*技能倍率*(1-dfs/660))
    # "M" 代表分配 1 點給 mp，每點 + 10 mp(mp 越多可以開越強的技能)
    # 以下為簡單的範例
    # 字母順序不影響效果呈現，我們只會數對應的字母數量有多少
    # 未滿 30 或是前 30 個內有規格外字母，就代表你放棄了這些天賦點

    passive_str = "H" * 20 + "D" * 0 + "A" * 5 + "M" * 5
    return passive_str

def action_set():

    # 請回傳一個陣列，並且包含四個字串
    # 陣列的順序直接影響技能編號
    # 字串前 30 個字將用來打造你的技能
    # 大小寫一樣
    # "A": 代表攻擊力，每個 A + 5% 的傷害並且額外消耗 0.5 的 MP
    # "F": 代表移動效果，每一個 F 會讓你朝敵人移動一格，每個 F 額外消耗 10 的 MP
    # "B": 同樣移動效果，每一個 B 會讓你遠離敵人移動一格，每個 B 額外消耗 10 的 MP
    # 如果 "F" 跟 "B" 同時出現，會互相扣減。比如 "FFB" 等同於 "F"
    # "R": 代表攻擊範圍，每一個 R 會讓你該次攻擊的範圍 + 1 格，並額外消耗 5 的 MP
    # 如果沒有 "R" 代表不進行攻擊，則 "A" 也等同於沒有用
    # 移動距離的上限為 6 格
    # 攻擊距離的上限為 6 格
    # 你的技能可以同時有攻擊跟移動的效果，你的人物總是會先移動再攻擊，請善用這個特性
    # 如果陣列未滿，則對應編號都會當普通辦理
    # 以下為範例陣列，請不要沿用，你的角色技能會很廢
    # 字母順序不影響判定，如 "RRA" 的技能跟 "RAR" 是一樣的

    # NPC 電腦的
    # 如 "RA" 就是一格的普攻，"RRA" 就是兩格的普攻，"RRAA" 就是兩格又痛一點點的普攻
    action_set_str = ["RRRRA", "A" * 500 + "R", "FF", "BB"]

    return action_set_str

def combatLogic(enemy, me, eventmap):
    # 決定你的角色的自動戰鬥邏輯
    # 我們會幫你把你必須知道的資訊都先放進對應的變數，你們可以參考該變數來決定角色該怎麼動
    
    enemy_atb = enemy.getAtb()
    my_atb = me.getAtb()

    # 敵人當前的血量、魔力、攻擊力、防禦力、位置(0-12)
    enemy_hp = enemy_atb.hp
    enemy_mp = enemy_atb.mp
    enemy_atk = enemy_atb.atk
    enemy_dfs = enemy_atb.dfs
    enemy_pos = enemy.getPos()

    # 你的角色當前的血量、魔力、攻擊力、防禦力、位置(0-12)
    my_hp = my_atb.hp
    my_mp = my_atb.mp
    my_atk = my_atb.atk
    my_dfs = my_atb.dfs
    my_pos = me.getPos()
    enemy_pos = enemy.getPos()

    # 以下可以開始自由修改與決定你的 AI，上面幫你取好的資訊請盡量不要去動
    if(abs(enemy_pos - my_pos) < 2):
        if(my_hp < 2000):
            skill_number = 3
        else:
            skill_number = 1
    elif(abs(enemy_pos - my_pos) > 4):
        skill_number = 2
    elif(abs(enemy_pos - my_pos) >= 2):
        skill_number = 0

    # 這邊決定你要使用的技能編號，0-3 選一個。如果不在 0-3 內會視為普攻
    return skill_number

def name():
    # 取個煞氣的名字吧，會顯示在角色上方
    name = "欸欸欸名字可以自己取欸"
    return name