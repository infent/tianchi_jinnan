from storemysql import *
from sklearn.svm import OneClassSVM
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from pymining import itemmining
from pymining import assocrules

def queryByCarid(carid):
    content = querybycarid(carid)
    if len(content) == 0:
        resultFromDB = ('历史违规次数:' + carid + '在数据库中未出现过')
    else:
        resultFromDB = ('有无套牌历史(1:有 0:无): ' + str(content['caridrepeated'].values[0])
                        + '\n' + '在省内高速行驶次数：' + str(content['appeartimes'].values[0])
                        + '\n' + '历史违规次数：' + str(content['illegaltimes'].values[0])
                        + '\n' + '平均行驶时长: ' + content['travel_distance_avg'].values[0]
                        + '\n' + '常用出入口： ' + content['outin_freq1'].values[0] + str(
            content['outin_freq1_times'].values[0]) + '次'
                        + '\n' + '常运输物品： ' + content['goods_freq1'].values[0] + str(
            content['goods_freq1_times'].values[0]) + '次'+'\n')
    return resultFromDB

#接入用户输入数据，并转换为整型
def convert2int(calculateParam):
    cartypeMapping = readaAllFromMysql('cartypeMaping')
    dfoutMapping = readaAllFromMysql('dfoutMapping')
    dfinMapping = readaAllFromMysql('dfinMapping')
    dfdateMapping = readaAllFromMysql('dfdateMapping')
    dfgoodsMapping = readaAllFromMysql('dfgoodsMapping')
    intParam = [0,0,0,0,0,0]
    intParam[0] = cartypeMapping[calculateParam[0]].values[0]
    if calculateParam[1]=='':
        intParam[1] = 0
    else:
        intParam[1] = dfoutMapping[calculateParam[1]].values[0]
    if calculateParam[2]=='':
        intParam[1] = 0
    else:
        intParam[2] = dfinMapping[calculateParam[2]].values[0]

    intParam[3] = dfdateMapping[calculateParam[3]].values[0]

    if calculateParam[4]=='':
        intParam[4] = 0
    else:
        intParam[4] = dfgoodsMapping[calculateParam[4]].values[0]
    if calculateParam[5]=='':
        intParam[5] = 5000
    else:
        intParam[5] = int(calculateParam[5])
    return intParam

#读取存储的训练好的模型进行概率预测
def rf_predict(calculateParam):
    model = joblib.load('model/rf.model')
    intParam = convert2int(calculateParam)
    #print('intparam='+intParam)
    temp = model.predict(np.array(intParam).reshape(1,6))
    temp2 = model.predict_proba(np.array(intParam).reshape(1,6))
    result = '*'*30+'\nSunShine模型预测:'+'\n属于合法车辆的概率为：'+str(temp2[0][0])+'\n属于非法车辆的概率为：'+str(temp2[0][1])
    return result
    #result = model.predict(df.values[0][:-1])
    #return result

#关联规则挖掘算法
def rule_mining(itemlist):
    dfillegal = readaAllFromMysql('car_illeagal_4rulemining')
    def not_empty(s):
        return s and s.strip()
    #list去空
    itemlistnotnull = list(filter(not_empty,itemlist))
    dfillegal = dfillegal.ix[:,itemlistnotnull]

    transactions_mining = []
    for i in dfillegal.values:
        transactions_mining.append(tuple(list(map(str, i))))

    # step1 找频繁项集
    relim_input = itemmining.get_relim_input(transactions_mining)
    freq_items = itemmining.relim(relim_input, min_support=100)

    # step2 找关联规则
    # 关联规则使用的数据结构 [(项集1，项集2，项集n，支持度，置信度)]
    # (frozenset({'大连收费分中心', '6', '计货1'}), frozenset({'违规收费'}), 1007, 0.998017839444995)
    rules = assocrules.mine_assoc_rules(freq_items, min_confidence=0.1)
    #按list中的tuple的第四项也就是置信度来排序
    rules = sorted(rules,key=lambda rule:-rule[3])
    return rules



#在初次数据处理时生成映射表，并将其存好，需要更新时传入777参数更新映射表数据库
def dataPreprocess(rewritelabelmapping=0):
    df = readaAllFromMysql('car_info_original')
    df.fillna('无', inplace=True)
    df.drop(551291, inplace=True)
    df = df[df["入口时间"].map(lambda x: x.split("/")[0] == "2018")]
    df = df.ix[:, ['车牌号', '车型', '出口收费站', '入口站', '交易时间','货物','重量', '收费类型（正常，违规，假冒）']]
    # df[df['收费类型（正常，违规，假冒）']!='正常']['收费类型（正常，违规，假冒）']='违规收费'
    df['收费类型（正常，违规，假冒）'] = df['收费类型（正常，违规，假冒）'].map(lambda x: '违规收费' if x == '假冒绿通' else x)
    df['交易时间'] = df['交易时间'].map(lambda x: x.split(' ')[0])
    df['交易时间'] = df['交易时间'].map(lambda x: x.split('/')[1]+'/'+x.split('/')[2])
    if rewritelabelmapping==777:
        labelMappings = all2int(df)
        # 转置是为了方便列名读取
        dfcartype = pd.DataFrame.from_dict(labelMappings[0],orient='index').T
        maplabeling2mysql(dfcartype,'cartypeMaping')
        dfout = pd.DataFrame.from_dict(labelMappings[1],orient='index').T
        maplabeling2mysql(dfout,'dfoutMapping')
        dfin = pd.DataFrame.from_dict(labelMappings[2],orient='index').T
        maplabeling2mysql(dfin,'dfinMapping')
        dfdate = pd.DataFrame.from_dict(labelMappings[3], orient='index').T
        maplabeling2mysql(dfdate,'dfdateMapping')
        dfgoods = pd.DataFrame.from_dict(labelMappings[4],orient='index').T
        maplabeling2mysql(dfgoods,'dfgoodsMapping')

    return df







# 获得单列映射表
def categories2int(dataframe, label):
    label_mapping = {la: index for index, la in enumerate(np.unique(dataframe[label]))}
    dataframe[label] = dataframe[label].map(label_mapping)
    return label_mapping

# 获得整体映射表
def all2int(dataframe):
    label_mapping_cartype = categories2int(dataframe, '车型')
    label_mapping_outport = categories2int(dataframe, '出口收费站')
    label_mapping_inport = categories2int(dataframe, '入口站')
    label_mapping_dealtime = categories2int(dataframe, '交易时间')
    label_mapping_goods = categories2int(dataframe, '货物')
    #0合法1违规
    label_mapping_goal = categories2int(dataframe, '收费类型（正常，违规，假冒）')
    label_mappings = [label_mapping_cartype, label_mapping_outport, label_mapping_inport, label_mapping_dealtime,
                      label_mapping_goods, label_mapping_goal]
    return label_mappings


# 定义整型转回标签函数，单列
def int2categories(dataframe, label, label_mapping):
    inverse_lable_mapping = {v: k for k, v in label_mapping.items()}
    dataframe[label] = dataframe[label].map(inverse_lable_mapping)

#定义一条数据转成整型
def transformInput():
    pass
# 定义一条数据转回标签类
#label_mappings = all2int()
labels = ['车型', '出口收费站', '入口站', '交易时间', '货物','收费类型（正常，违规，假冒）']

'''
for i,j in zip(labels,label_mappings):
     int2categories(pre_data,i,j)
'''

'''
   precision    recall  f1-score   support
           0       0.97      0.99      0.98    270582
           1       0.61      0.27      0.37     12043
   micro avg       0.96      0.96      0.96    282625
   macro avg       0.79      0.63      0.68    282625
weighted avg       0.95      0.96      0.95    282625
加入重量维度后对违法车1类的精确度识别变高了变成0.7了，但是recall没有变化
'''
def buildModelAndSave_rf():
    df = dataPreprocess()
    df['重量'] = df['重量'].map(lambda x:x/100)
    X_train, X_test, y_train, y_test = train_test_split(df.loc[:, ['车型', '出口收费站', '入口站', '交易时间', '货物','重量']],
                                                        df['收费类型（正常，违规，假冒）'])

    clf = RandomForestClassifier(random_state=42)
    rf = clf.fit(X_train,y_train)
    #保存模型
    joblib.dump(rf,'model/rf.model')
    #读取模型
    model = joblib.load('model/rf.model')

    predict = model.predict(X_test)


    print(classification_report(y_test,predict))
    #return model

'''
违章判定属于违章类  不违章判定不属于违章类

433                804594
12084              811624
'''
def buildModelAndSave_OneClassSVM():
    df = dataPreprocess()
    dflegal = df[df['收费类型（正常，违规，假冒）']==0]
    dfillegal = df[df['收费类型（正常，违规，假冒）']==1]


    dfillegaltrain,dfillegaltest,a,b = train_test_split(dfillegal.loc[:, ['车型', '出口收费站', '入口站', '交易时间', '货物']],
                         dfillegal['收费类型（正常，违规，假冒）'])
    dflegaltrain, dflegaltest, c, d = train_test_split(dflegal.loc[:, ['车型', '出口收费站', '入口站', '交易时间', '货物']],
                                                           dflegal['收费类型（正常，违规，假冒）'])
    #default nu=0.5 gamma=0.1
    clf = OneClassSVM(nu=0.1)
    clf.fit(dfillegaltrain)


    result1 = clf.predict(dfillegaltest)


    result2 = clf.predict(dflegaltrain)

    print(result1[result1==1].size,result2[result2==-1].size)


#
# if __name__ == '__main__':
#     buildModelAndSave_rf()

