from math import factorial
from bisect import bisect_right
import time
import numpy as np

#Convertクラスで使用する要素を準備するクラス
class InitKey:
    states_sums = [0]
    for i in range(3):
        for j in range(3):
            states_sum = factorial(9)//(factorial(i)*factorial(j)*factorial(9-i-j))
            states_sums.append(states_sum + states_sums[-1])
    cases_sum = states_sums[-1]

    @staticmethod
    #番号(int)から状態(list)へ変換する
    def init_scene_to_states(scene: int) -> list:
        convert_ss = InitKey.states_sums
    
        index = bisect_right(convert_ss, scene)-1
        k, l = index%3, index//3
        large_part = convert_ss[index]
        small_part = scene - large_part

        rate = convert_ss[k+1]-convert_ss[k]
        allies_part, enemies_part = small_part%rate, small_part//rate
        allies_states, enemies_states = [0, 0], [0, 0]
        if k == 1:
            allies_states[1] = allies_part+1
        elif k == 2:
            n1 = int((17-(289-8*allies_part)**(1/2))//2)
            m1 = allies_part+1-n1*(15-n1)//2
            allies_states = [n1+1, m1+1]
        if l == 1:
            enemies_states[1] = enemies_part+1+k
        elif l == 2:
            n2 = int((17-2*k-((17-2*k)**2-8*enemies_part)**(1/2))//2)
            m2 = enemies_part+1-n2*(15-2*k-n2)//2
            enemies_states = [n2+1+k, m2+1+k]
        for x in range(2):
            for y in range(2):
                if enemies_states[x] <= allies_states[-y-1] and enemies_states[x] != 0: enemies_states[x] -= 1

        return allies_states+enemies_states

#局面と番号の相互変換クラス
class Convert:
    scene_dic = {}
    states_list = []
    for i in range(1423):
        states = InitKey.init_scene_to_states(i)
        left, right = states[:2], states[2:]
        for j in range(4):
            if j == 2: left.reverse()
            right.reverse()
            scene_dic[tuple(left+right)] = i
        states_list.append(states)

    @staticmethod
    #状態(list)から番号(int)へ変換する
    def states_to_scene(states: list) -> int:
        ret = 0
        for i in range(3):
            s = tuple(states[i*2:i*2+2]+states[i*2+6:i*2+8])
            ret += Convert.scene_dic[s]*InitKey.cases_sum**i
        return ret

    @staticmethod
    #番号(int)から状態(list)へ変換する
    def scene_to_states(scene: int) -> list:
        allies_parts, enemies_parts = [], []
        for _ in range(3):
            part = scene % InitKey.cases_sum
            allies_parts.extend(Convert.states_list[part][:2])
            enemies_parts.extend(Convert.states_list[part][2:])
            scene //= InitKey.cases_sum
        return allies_parts + enemies_parts

#終了局面かを判定する(戻り値: 終了局面→評価値, 終了局面でない→None)
judge_sets = [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {1, 4, 7}, {2, 5, 8}, {3, 6, 9}, {1, 5, 9}, {3, 5, 7}]
def judge_states_end(states):

    #隠れている駒を掃き出しつつ駒の位置を集合にまとめる
    player_set, enemy_set = set(), set()
    for i in reversed(range(3)):
        player_set |= set(states[i*2:i*2+2]) - enemy_set
        enemy_set |= set(states[i*2+6:i*2+8]) - player_set

    flag = False
    #judge_setsのパターンに合致していれば評価値を返す
    for judge in judge_sets:
        if judge <= player_set:
            return 0
        if judge <= enemy_set:
            flag = True
    else:
        if flag:
            return -1
        else:
            return None

#1手先としてありえる局面を列挙する
def list_next_scenes_states(states):
    states_reversed_buf = states[6:]+states[:6]
    states_buf = states[:]
    #それぞれの駒について、移動不可であればスキップする
    for i in range(6):
        if states[i] == states[i//2*2+(i+1)%2] == 0 and i%2 == 0: continue
        l_i = (i//2+1)*2
        ng_pos_set = set(states[l_i:6]) | set(states[l_i+6:12])
        if states[i] != 0:
            if states[i] in ng_pos_set: continue
            #駒を持ち上げた瞬間に敗北してしまう場合スキップする
            states_buf[i] = 0
            if judge_states_end(states_buf): 
                states_buf[i] = states[i]
                continue
            states_buf[i] = states[i]
        
        #移動可能な位置に移動させ、局面を排出していく
        ng_pos_set |= set(states[l_i-2:l_i]) | set(states[l_i+4:l_i+6])
        enable_pos_set = set(range(1, 10)) - ng_pos_set
        for j in enable_pos_set:
            states_reversed_buf[i+6] = j
            yield states_reversed_buf
        states_reversed_buf[i+6] = states[i]

#局面の状態を視覚的に出力する
sign_dic = {0: "▫", 1: "□", 2:"◇", 3: "▪", 4:"■", 5:"◆"}
def print_states(states):
    pos_list = [[] for _ in range(9)]
    for i in range(12):
        x = (5+i*6)%13
        if states[x] == 0: continue
        pos_list[states[x]-1].append(sign_dic[x//2])
    for j in range(3):
        print(" ".join("".join(pos_list[k]) + "-"*(3-len(pos_list[k])) for k in range(j*3, j*3+3)))

#終了局面か判定する
data_list = np.zeros(1423**3, dtype=np.int8)
is_final = np.zeros(1423**3, dtype=np.bool_)
start_time = time.time()
count = 0
for i in range(1423**3):
    if is_final[i]: continue
    states = Convert.scene_to_states(i)
    res = judge_states_end(states)
    if res != None:
        data_list[i] = res
        is_final[i] = True

        #探索状況の出力
        if count % 1000000 == 0:
            print(count, i)
            print("{:.1f}s".format(time.time()-start_time))
            print_states(states)
            print()
        count += 1
    else:
        for _ in list_next_scenes_states(states):
            break
        else:
            data_list[i] = -1
            is_final[i] = True

#本探索用ファイルの出力
np.save("data_list", data_list)
np.save("is_final", is_final)