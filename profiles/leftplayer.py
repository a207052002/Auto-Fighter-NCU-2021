from player import *

def passive():
    # 捏你的角色
    # 請回傳一個限定字的字串，會決定的角色的攻擊(atk)、防禦(dfs)、血量(hp)、魔力(mp)
    # 有 30 點配點，因此我們只會拿前 30 個字去用
    # 規則之外的字母會被忽略
    # 大小寫一樣
    # 你的角色起始有 5000 hp、330 dfs、1000 atk、200 mp
    # "H" 代表分配 1 點給 HP，每點 + 500 HP
    # "D" 代表分配 1 點給 dfs，每點 + 7 dfs(防禦減傷率算法為 (dfs/660))
    # "A" 代表分配 1 點給 atk，每點 + 30 atk(傷害算法為 atk*(0.5+技能倍率)*(1-dfs/660))
    # "M" 代表分配 1 點給 mp，每點 + 10 mp(mp 越多可以用更強的動作)
    # 以下為簡單的範例
    # 字母順序不影響效果呈現，我們只會數對應的字母數量有多少
    # 未滿 30 或是前 30 個內有規格外字母，就代表你放棄了這些天賦點

    passive_str = "H" * 0 + "D" * 0 + "A" * 20 + "M" * 10
    return passive_str

def combatLogic(enemy, me, eventmap):
    # 決定你的角色的自動戰鬥邏輯
    # 我們會幫你把你必須知道的資訊都先放進對應的變數，你們可以參考該變數來決定角色該怎麼動

    # eventmap 是一個跟場地大小等長的陣列(list)，每陣列裡面非 0 的數字代表場地上存在的特殊道具
    # 場地長度 = 17，陣列(0-16)
    # 移動到該格會自動撿起道具
    # 以下為陣列中的數字的意義
    # 1 代表存在 P (Power shot) 撿到後可以一次性開啟無視防禦 25% - 55%(隨角色攻擊提高) 生命的無限距離大招
    # 撿到後透過 return 整數：1 來讓角色使用
    # 2 代表存在 A (Avoid) 撿到後可以一次性開啟一個 buff 持續三回合，期間無條件閃避所有攻擊
    # 以上兩個道具撿到後會存在身上直到使用，已經持有一樣的道具可以再撿但是不會額外增加數量
    # 3 代表存在 H (Heart) 撿到後可以回覆 15%+500 的生命(對坦克型角色有很好的效果)
    # 4 代表存在 M (Mp) 撿到後可以回覆 20% 魔力(MP 高的角色收益高)
    # 每樣道具都非常強大，並且每回合結束後有一定機率隨機產生在地圖上，建議可以考慮以道具的撿取跟使用優先

    enemy_atb = enemy.getAtb()
    my_atb = me.getAtb()

    # 敵人當前的血量、魔力、攻擊力、防禦力、位置(0-16)
    enemy_hp = enemy_atb.hp
    enemy_mp = enemy_atb.mp
    enemy_max_hp = enemy_atb.max_hp
    enemy_max_mp = enemy_atb.max_mp
    enemy_atk = enemy_atb.atk
    enemy_dfs = enemy_atb.dfs
    enemy_pos = enemy.getPos()

    enemy_avoid = enemy.avoid
    # 敵人是否持有強力攻擊
    enemy_power_shot = enemy.power_shot
    # 敵人的閃避 buff 的剩餘回合數，只要比 0 大就會必定閃避所有攻擊，每輪到敵人動一次就會少一回合
    enemy_avoiding = enemy.avoid_buff

    # 你的角色當前的血量、魔力、攻擊力、防禦力、位置(0-16)
    my_hp = my_atb.hp
    my_mp = my_atb.mp
    my_max_hp = my_atb.max_hp
    my_max_mp = my_atb.max_mp
    my_atk = my_atb.atk
    my_dfs = my_atb.dfs
    my_pos = me.getPos()

    my_avoid = me.avoid
    # 你是否持有強力攻擊
    my_power_shot = me.power_shot
    # 你的閃避 buff 的剩餘回合數，只要比 0 大就會必定閃避所有攻擊，每輪到你動一次就會少一回合
    my_avoiding = me.avoid_buff

    # 以下可以開始自由修改與決定你的 AI，上面幫你取好的資訊請盡量不要去動
    # 最後你 return 在這個 function 的東西會決定你角色該回合的動作
    # 可以接受的回傳有整數或字串
    # 若回傳數字代表特殊動作如下
    # 0 是冥想，使用後會回 30 mp
    # 1 使用撿到的強力攻擊
    # 2 啟用撿到的迴避能力，持續兩回合(自己回合+敵人回合)，無視所有傷害
    # 數字若不是以上的數字的話，會當成 0 ，冥想

    # 若回傳字串
    # 字串的組合將用來打造你專屬的動作
    # 大小寫一樣
    # "A": 代表攻擊力，每個 A + 10% 的傷害並且額外消耗 + 10*(2/3) 的 MP
    # "F": 代表移動效果，每一個 F 會讓你朝敵人移動一格，每個 F 額外消耗 10 的 MP
    # "B": 同樣移動效果，每一個 B 會讓你遠離敵人移動一格，每個 B 額外消耗 10 的 MP
    # 如果 "F" 跟 "B" 同時出現，會互相扣減。比如 "FFB" 等同於 "F"，MP 消耗也視同只有 "F"
    # "R": 代表攻擊範圍，每一個 R 會讓你該次攻擊的範圍 + 1 格，並額外消耗 10 的 MP
    # 如果沒有 "R" 代表不進行攻擊，則 "A" 也等同於沒有用
    # 移動距離的上限為 6 格
    # 攻擊距離的上限為 6 格
    # 你的技能可以同時有攻擊跟移動的效果，你的人物總是會先移動再攻擊，請善用這個特性

    # 每個 "R" 消耗 mp
    R_mp = 10
    # 每個 "A" 消耗 mp
    A_mp = 20/3
    # 每額外移動一格消耗 mp
    M_mp = 10

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

    # 每個 "R" 消耗 mp
    R_mp = 10
    # 每個 "A" 消耗 mp
    A_mp = 20/3
    # 每額外移動一格消耗 mp
    M_mp = 10

    action = 0
    if(my_mp <= 80):
        action = 0
    else:
        if(abs(enemy_pos - my_pos) < 4):
            if(my_pos <= 3 or my_pos >= 13):
                action = "FFFFFF"
            else:
                action = "B" * ( 5 - abs(enemy_pos - my_pos)) + "RRRRR"
        elif(abs(enemy_pos - my_pos) <= 5 and my_mp <= 100):
            action = "R" * abs(enemy_pos - my_pos)
        elif(abs(enemy_pos - my_pos) <= 5):
            action = "R" * abs(enemy_pos - my_pos) + "AAAA"
        elif(abs(enemy_pos - my_pos) > 5):
            action = "F"
    if(my_avoid):
        action = 2
    if(my_power_shot):
        action = 1

    return action

def name():
    # 取個煞氣的名字吧，會顯示在角色上方
    name = "欸欸欸名字可以自己取欸"
    return name