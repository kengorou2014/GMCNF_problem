import pulp
import numpy as np
import copy
from data import *

def optimize(title, size, time):
    t = time
    prob = pulp.LpProblem("%s" % (title), pulp.LpMinimize)
    var_inflow = [[{} for i in range(size)] for j in range(size)]
    var_outflow = [[{} for i in range(size)] for j in range(size)]

    ############### 変数を定義 ################
    # 三次元配列に変数を格納
    for i in range(size):
        for j in range(size):
            var_inflow[j][i] = {
                'lng': pulp.LpVariable("%s(%s)_%s_to_%s_lng_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model']),
                'hfo': pulp.LpVariable("%s(%s)_%s_to_%s_hfo_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model']),
                'mgo': pulp.LpVariable("%s(%s)_%s_to_%s_mgo_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model']),
                'car_ship_jp': {
                    'lngship': pulp.LpVariable("%s(%s)_%s_to_%s_lngship_car_jp_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                    'scrbship': pulp.LpVariable("%s(%s)_%s_to_%s_scrbship_car_jp_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                    'ordship': pulp.LpVariable("%s(%s)_%s_to_%s_ordship_car_jp_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                },
                'car_ship_am': {
                    'lngship': pulp.LpVariable("%s(%s)_%s_to_%s_lngship_car_am_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                    'scrbship': pulp.LpVariable("%s(%s)_%s_to_%s_scrbship_car_am_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                    'ordship': pulp.LpVariable("%s(%s)_%s_to_%s_ordship_car_am_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'], cat = pulp.LpInteger),
                },
                'car_jp': pulp.LpVariable("%s(%s)_%s_to_%s_car_jp_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'],cat = pulp.LpInteger),
                'car_am': pulp.LpVariable("%s(%s)_%s_to_%s_car_am_in" % (t, dict[i], dict[j], dict[i]), lowBound = 0, upBound = upbound[j][i]['model'],cat = pulp.LpInteger),
            }
            var_outflow[i][j] = {
                'lng': pulp.LpVariable("%s(%s)_%s_to_%s_lng_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model']),
                'hfo': pulp.LpVariable("%s(%s)_%s_to_%s_hfo_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model']),
                'mgo': pulp.LpVariable("%s(%s)_%s_to_%s_mgo_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model']),
                'car_ship_jp': {
                    'lngship': pulp.LpVariable("%s(%s)_%s_to_%s_lngship_car_jp_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                    'scrbship': pulp.LpVariable("%s(%s)_%s_to_%s_scrbship_car_jp_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                    'ordship': pulp.LpVariable("%s(%s)_%s_to_%s_ordship_car_jp_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                },
                'car_ship_am': {
                    'lngship': pulp.LpVariable("%s(%s)_%s_to_%s_lngship_car_am_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                    'scrbship': pulp.LpVariable("%s(%s)_%s_to_%s_scrbship_car_am_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                    'ordship': pulp.LpVariable("%s(%s)_%s_to_%s_ordship_car_am_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                },
                'car_jp': pulp.LpVariable("%s(%s)_%s_to_%s_car_jp_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
                'car_am': pulp.LpVariable("%s(%s)_%s_to_%s_car_am_out" % (t, dict[i], dict[i], dict[j]), lowBound = 0, upBound = upbound[i][j]['model'], cat = pulp.LpInteger),
            }
    ################ 目的関数を定義 ###################
    objFn = []
    # 船、スクラバの建造コストを初期コストとして代入
    cost_initial = 0

    objFn.append(cost_initial)
    for i in range(size):
        for j in range(size):
            for ship in 'lngship', 'scrbship', 'ordship':
                objFn.append(var_outflow[i][j]['car_ship_jp'][ship]*cost_out[i][j][ship])
                objFn.append(var_outflow[i][j]['car_ship_am'][ship]*cost_out[i][j][ship])

    prob += pulp.lpSum(objFn), "%s" % (title)
    ################# 制約を付与 ###################
    for i in range(size):
        for c in 'lng', 'hfo', 'mgo', 'car_jp', 'car_am':
            #　ノード i におけるflow balance
            # matrixA
            prob += pulp.lpSum(var_outflow[i][j][c] for j in range(size)) - pulp.lpSum(var_inflow[j][i][c] for j in range(size)) <= b[i][c], "Flow balance of %s at node %s" % (c, dict[i])

        # 船に関してはb=0
        for c in 'car_ship_jp','car_ship_am':
            for ship in ['lngship','scrbship','ordship']:
                # matrixA
                prob += pulp.lpSum(var_outflow[i][j][c][ship] for j in range(size)) - pulp.lpSum(var_inflow[j][i][c][ship] for j in range(size)) <= b[i][c][ship], "Flow balance of %s%s at node %s" % (c, ship, dict[i])

        for j in range(size):
            # 燃料と船の関係
            # matrixC
            prob += fuel_consume_volume[i][j]['lngship']*pulp.lpSum(var_outflow[i][j][shiptype]['lngship'] for shiptype in ['car_ship_jp', 'car_ship_am']) - var_outflow[i][j]['lng'] <= 0, "lng must be loaded on lngship at edge(%s,%s)" % (dict[i], dict[j])
            prob += fuel_consume_volume[i][j]['scrbship']*pulp.lpSum(var_outflow[i][j][shiptype]['scrbship'] for shiptype in ['car_ship_jp', 'car_ship_am']) - var_outflow[i][j]['hfo'] <= 0, "hfo must be loaded on lngship at edge(%s,%s)" % (dict[i], dict[j])
            prob += fuel_consume_volume[i][j]['ordship']*pulp.lpSum(var_outflow[i][j][shiptype]['ordship'] for shiptype in ['car_ship_jp', 'car_ship_am']) - var_outflow[i][j]['mgo'] <= 0, "mgo must be loaded on lngship at edge(%s,%s)" % (dict[i], dict[j])

            prob += -p['lngship']*pulp.lpSum(var_outflow[i][j][shiptype]['lngship'] for shiptype in ['car_ship_jp', 'car_ship_am']) + var_outflow[i][j]['lng'] <= 0, "lngship has a tank capacity at edge(%s,%s)" % (dict[i], dict[j])
            prob += -p['scrbship']*pulp.lpSum(var_outflow[i][j][shiptype]['scrbship'] for shiptype in ['car_ship_jp', 'car_ship_am']) + var_outflow[i][j]['hfo'] <= 0, "scrbship has a tank capacity at edge(%s,%s)" % (dict[i], dict[j])
            prob += -p['ordship']*pulp.lpSum(var_outflow[i][j][shiptype]['ordship'] for shiptype in ['car_ship_jp', 'car_ship_am']) + var_outflow[i][j]['mgo'] <= 0, "ordship has a tank capacity at edge(%s,%s)" % (dict[i], dict[j])

            # matrixC
            prob += var_outflow[i][j]['car_jp'] - pulp.lpSum(capacity*var_outflow[i][j]['car_ship_jp'][shiptype] for shiptype in ['lngship', 'scrbship', 'ordship']) <= 0, "%s must be loaded on %s at edge(%s,%s)" % ('car_jp', 'carship', dict[i], dict[j])
            prob += var_outflow[i][j]['car_am'] - pulp.lpSum(capacity*var_outflow[i][j]['car_ship_am'][shiptype] for shiptype in ['lngship', 'scrbship', 'ordship']) <= 0, "%s must be loaded on %s at edge(%s,%s)" % ('car_am', 'carship', dict[i], dict[j])

            # 船は燃料を消費して運航する
            # matrixB
            prob += var_inflow[i][j]['lng'] == var_outflow[i][j]['lng'] - pulp.lpSum(fuel_consume_volume[i][j]['lngship']*var_outflow[i][j][shiptype]['lngship'] for shiptype in ['car_ship_jp', 'car_ship_am']),"lng is consumed by all_lngship at edge(%s,%s)" % (dict[i], dict[j])
            prob += var_inflow[i][j]['hfo'] == var_outflow[i][j]['hfo'] - pulp.lpSum(fuel_consume_volume[i][j]['scrbship']*var_outflow[i][j][shiptype]['scrbship'] for shiptype in ['car_ship_jp', 'car_ship_am']),"hfo is consumed by all_scrbship at edge(%s,%s)" % (dict[i], dict[j])
            prob += var_inflow[i][j]['mgo'] == var_outflow[i][j]['mgo'] - pulp.lpSum(fuel_consume_volume[i][j]['ordship']*var_outflow[i][j][shiptype]['ordship'] for shiptype in ['car_ship_jp', 'car_ship_am']),"mgo is consumed by all_ordship at edge(%s,%s)" % (dict[i], dict[j])

            # フローの保存則
            # matrixB
            for c in 'car_jp', 'car_am':
                prob += var_outflow[i][j][c] == var_inflow[i][j][c], "Consistency of %s at edge (%s,%s)" % (c, dict[i], dict[j])
            for c in 'car_ship_jp', 'car_ship_am':
                for ship in var_outflow[i][j][c].keys():
                    prob += var_outflow[i][j][c][ship] == var_inflow[i][j][c][ship], "Consistency of %s,%s at edge (%s,%s)" % (c, ship, dict[i], dict[j])

    ################ optimizeしてprobを返す ###################
    prob.solve()
    return prob, var_inflow, var_outflow
