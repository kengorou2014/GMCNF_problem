from optimize import *
import csv
import data

result = []

fuel_pattern = {
    0: 'mgo',
    1: 'lng',
    2: 'hfo',
    3: 'lng,hfo',
    4: 'hfo,mgo',
    5: 'lng,mgo',
    6: 'lng,hfo,mgo',
}

def main(t,pattern):
    CO2_emission = 0
    lngship_total = 0
    hfoship_total = 0
    mgoship_total = 0
    data.set_t(t, pattern)
    prob, var_inflow, var_outflow = optimize("cost", size, t)
    opt_cost = pulp.value(prob.objective)

    for v in prob.variables():
        i = v.name.split('_')[1]
        j = v.name.split('_')[3]

        # 排出CO2量を計算
        if 'lng_out' in v.name:
            CO2_emission += v.varValue*CO2['lng']
        elif 'hfo_out' in v.name:
            CO2_emission += v.varValue*CO2['hfo']
        elif 'mgo_out' in v.name:
            CO2_emission += v.varValue*CO2['mgo']

        # 各船舶の[隻・km]を算出
        if ('lngship' in v.name)&('out' in v.name):
            lngship_total += v.varValue*distance.iloc[dict_rev[i],dict_rev[j]]
        elif ('scrbship' in v.name)&('out' in v.name):
            hfoship_total += v.varValue*distance.iloc[dict_rev[i],dict_rev[j]]
        elif ('ordship' in v.name)&('out' in v.name):
            mgoship_total += v.varValue*distance.iloc[dict_rev[i],dict_rev[j]]

    print("\n")
    print("Status:", pulp.LpStatus[prob.status])
    print("opt_cost: ", opt_cost, 'CO2_emission: ', CO2_emission, "\n")
    print('lngship_total_ton*km: ', lngship_total, '[隻・km]')
    print('hfoship_total_ton*km: ', hfoship_total, '[隻・km]')
    print('mgoship_total_ton*km: ', mgoship_total, '[隻・km]')
    print("\n")

    # 最適化の結果得られる各変数の値を表示する
    # for v in prob.variables():
        # if v.varValue != 0:
            # print(v.name, "=", v.varValue)

    return opt_cost, prob, CO2_emission

row = 0
co2_result = []


for i in range(1):
    cost, prob, co2 = main(1,i)
