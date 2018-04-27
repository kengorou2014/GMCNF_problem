import pandas as pd
import pulp
import numpy as np
import copy

##### 海上輸送網の読み込み ####
node = pd.read_csv('case_study/model/node.csv', index_col=0).fillna(0)

# 生産・消費のcsv[ton]
b_lng = pd.read_csv('case_study/model/b_lng.csv', index_col=0).fillna(0)
b_oil = pd.read_csv('case_study/model/b_oil.csv', index_col=0).fillna(0)
b_car_jp = pd.read_csv('case_study/model/b_car_jp.csv', index_col=0).fillna(0)
b_car_am = pd.read_csv('case_study/model/b_car_am.csv', index_col=0).fillna(0)

# upboundを全て統一のcsvで表現する
upbound_model = pd.read_csv('case_study/model/upbound_model.csv', index_col=0).fillna(0)

# ノード間の距離を定義する
distance = pd.read_csv('case_study/model/distance.csv', index_col=0).fillna(0)

size = len(node)
sample = [[{} for i in range(size)] for j in range(size)]
cost_out = copy.deepcopy(sample)
b = [{} for i in range(size)]
upbound = copy.deepcopy(sample)
fuel_consume_volume = copy.deepcopy(sample)

# 定数コストを辞書型で定義
# 単位は[million $]
# 卒論では未使用
cost = {
    'base_init': 0,
    'base_expansion': 0,
    'lng_car':0,
    'lng_container':0,
    'lng_bulk':0,
    'scrubber_car':0,
    'scrubber_container':0,
    'scrubber_bulk':0,
}

# [tCO2/ton]
# 卒論では未使用
CO2 = {
    'lng': 2.7,
    'hfo': 3,
    'mgo':2.71,
}

# 燃料価格
# [$/ton]
fuelcost = {
    'lng':10,
    'hfo':12,
    'mgo':20,
    'JP': {
        'lng': 345,
        'hfo': 335,
        'mgo': 500,
    },
    'ME': {
        'lng': 125,
        'hfo': 330,
        'mgo': 550,
    },
    'SE': {
        'lng': 140,
        'hfo': 330,
        'mgo': 440,
    },
    'AU': {
        'lng': 140,
        'hfo': 400,
        'mgo': 500,
    },
    'EU': {
        'lng': 300,
        'hfo': 310,
        'mgo': 430,
    },
    'AW': {
        'lng': 155,
        'hfo': 310,
        'mgo': 450,
    },
    'AE': {
        'lng': 155,
        'hfo': 350,
        'mgo': 490,
    },
}

# 船1隻1kmあたりに消費する燃料
# [ton/隻・km]
r = {
    'lng': 0.099,
    'hfo': 0.124,
    'mgo': 0.112,
}

# 船1咳が運べる貨物の量[ton/隻]
capacity = 10

# 船にはタンク容量がある[ton/隻]
p = {
    'lngship': 1500,
    'scrbship': 3000,
    'ordship': 3500,
}

# ネットワーク内で使用できる燃料の組み合わせ全7種類をバイナリで判断する
bin_decision = {
    0: {
        'lng': 0,
        'hfo': 0,
        'mgo': 1,
    },
    1: {
        'lng': 1,
        'hfo': 0,
        'mgo': 0,
    },
    2: {
        'lng': 0,
        'hfo': 1,
        'mgo': 0,
    },
    3: {
        'lng': 1,
        'hfo': 1,
        'mgo': 0,
    },
    4: {
        'lng': 0,
        'hfo': 1,
        'mgo': 1,
    },
    5: {
        'lng': 1,
        'hfo': 0,
        'mgo': 1,
    },
    6: {
        'lng': 1,
        'hfo': 1,
        'mgo': 1,
    },
}

# LNG供給基地が作られているかどうかの状態をバイナリで管理する
lng_base = {
    'JP': 1,
    'ME': 0,
    'SE': 1,
    'AU': 0,
    'EU': 1,
    'AW': 0,
    'AE': 0,
}

# 数字とセル名を結びつける
n = 0
dict = {}
dict_rev = {}
for i in node:
    dict[n] = i
    dict_rev[i] = n
    n += 1

dict_commods = {0: 'lng', 1: 'hfo', 2: 'mgo'}

# 時間断面でのモデルの各数値を読み込み
# 切断する時間断面tを定義
def set_t (param, pattern):
    t = param

    # 三次元配列に諸情報を格納
    for i in range(size):
        b[i] = {
            'lng': b_lng.iloc[i]*bin_decision[pattern]['lng']*lng_base[dict[i]],
            'hfo': b_oil.iloc[i]*bin_decision[pattern]['hfo'],
            'mgo': b_oil.iloc[i]*bin_decision[pattern]['mgo'],
            'car_jp': b_car_jp.iloc[i],
            'car_am': b_car_am.iloc[i],
            'car_ship_jp': {
                'lngship': 0,
                'scrbship': 0,
                'ordship': 0,
            },
            'car_ship_am': {
                'lngship': 0,
                'scrbship': 0,
                'ordship': 0,
            },
        }
        for j in range(size):
            upbound[i][j] = {
                'model': upbound_model.iloc[i,j],
            }
            cost_out[i][j] = {
                'lngship': fuelcost[dict[i]]['lng']*r['lng']*distance.iloc[i,j],
                'scrbship': fuelcost[dict[i]]['hfo']*r['hfo']*distance.iloc[i,j],
                'ordship': fuelcost[dict[i]]['mgo']*r['mgo']*distance.iloc[i,j],
            }
            fuel_consume_volume[i][j] = {
                'lngship': r['lng']*distance.iloc[i,j],
                'scrbship': r['hfo']*distance.iloc[i,j],
                'ordship':r['mgo']*distance.iloc[i,j],
            }
