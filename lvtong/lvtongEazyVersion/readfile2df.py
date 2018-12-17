import pandas as pd
import numpy as np
file_all = "./urf_all.txt"



def readfile(file_uri=file_all):
    lvtong_names = ['分公司', '出口收费站', '交易时间', '车型', '入口站', '入口时间', '轴数'
        , '重量', '金额', '收费类型（正常，违规，假冒）', '车牌号', '货物', '批注说明']
    lvtong = pd.read_csv(file_uri, sep='\t', encoding='utf-8', names=lvtong_names)
    lvtong = lvtong.fillna('无')
    lvtong = lvtong.drop(lvtong.loc[lvtong['货物'] == '8:33'].index)
    lvtong = lvtong[lvtong['入口时间'].map(lambda x: x.split("/")[0] == "2018")]
    lvtong['车牌号'] = lvtong['车牌号'].map(lambda x: x.strip() if len(x.strip()) == 7 else np.NaN)
    lvtong = lvtong.dropna()
    #lvtong = lvtong.loc[lvtong['入口时间'] != '违规收费']
    return lvtong


def feature_reconstruct():
    df = readfile()


def readfile2legaldfandillegal():
    df =  readfile()
    legaldf_input = df.loc[df['收费类型（正常，违规，假冒）'] == '正常']

    # illegaldf_input.loc[illegaldf_input['入口时间']== '违规收费']
    illegaldf_input = df.loc[df['收费类型（正常，违规，假冒）'] != '正常']

    # illegaldf_input['收费类型（正常，违规，假冒）'].loc[df['收费类型（正常，违规，假冒）'] == '假冒绿通'] = '违规收费'
    # 妈的太费事了替换，Series有函数,虽然也不省多少事
    illegaldf_input['收费类型（正常，违规，假冒）'] = illegaldf_input['收费类型（正常，违规，假冒）'].replace('假冒绿通', '违规收费')

    legaldf = legaldf_input.ix[:, ['车牌号', '车型', '出口收费站', '入口站', '入口时间']]
    legaldf['入口时间'] = legaldf['入口时间'].map(lambda x: x.split('/')[1])

    illegaldf = illegaldf_input.ix[:, ['车牌号', '车型', '出口收费站', '入口站', '入口时间']]
    illegaldf['入口时间'] = illegaldf['入口时间'].map(lambda x: x.split('/')[1])

    return legaldf,illegaldf

def reconstructdf():
    df = readfile()
    carlist = df['车牌号'].unique()
    #注意如果只写到count，得到的是Series,建立新的df时会把Series的index带进去，如groupby车牌号那么得到的Series就是以
    #车牌号为index，有index就会自动对齐
    appearlist = df.groupby('车牌号')['入口站'].count()

    cartypelist = df.groupby('车牌号')['入口站'].count()

    appearinportlist =df.groupby(['车牌号','入口站'],as_index=False).count()

    cardf = pd.DataFrame({'出现次数':appearlist})






