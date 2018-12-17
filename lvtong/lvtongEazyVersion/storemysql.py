import pandas as pd
from sqlalchemy import create_engine
import readfile2df

car_info_raw = "./urf_all.txt"
ip = '192.168.17.45'
netconnect = create_engine('mysql+pymysql://root:940518@192.168.17.45:3306/lvtong')


# netconnect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
def readfile(file_uri=car_info_raw):
    lvtong_names = ['分公司', '出口收费站', '交易时间', '车型', '入口站', '入口时间', '轴数'
        , '重量', '金额', '收费类型（正常，违规，假冒）', '车牌号', '货物', '批注说明']
    lvtong = pd.read_csv(file_uri, sep='\t', encoding='utf-8', names=lvtong_names)
    return lvtong


# 存储原始记录到数据库
def orignalData2mysql():
    df_orignal = readfile()
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(df_orignal, 'car_info_raw', netconnect, schema='lvtong')


# 点击存储到数据库按钮存储用户输入信息
def userInputData2mysql(dfuser):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(dfuser, 'user_input_data', netconnect, schema='lvtong', if_exists='append')


# 通用存储函数，不append
def store2lvtong(df, graphName):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(df, graphName, netconnect, schema='lvtong')


# dataProcess挑出清洗好的用以关联规则挖掘的违法数据df和合法数据df
def dataPreProcess():
    df = readaAllFromMysql('car_info_original')
    df.fillna('无', inplace=True)
    df.drop(551291, inplace=True)
    df['交易时间'] = df["交易时间"].map(lambda x: x.split("/")[1])
    df['重量'] = df['重量'].map(lambda x: x / 100)
    df['金额'] = df['金额'].map(lambda x: str(int(x / 100) + 1) + '百')
    df['车辆归属地'] = df['车牌号'].map(
        lambda x: x[0] if x[0] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] else '数字车')
    # df['收费类型（正常，违规，假冒）'] = df['收费类型（正常，违规，假冒）'].map(lambda x: '违规收费' if x == '假冒绿通' else x)
    dflegal = df[df['收费类型（正常，违规，假冒）'] == '正常']
    dfillegal = df[df['收费类型（正常，违规，假冒）'] != '正常']
    dflegal = dflegal.ix[:, ['车型', '轴数', '重量', '金额', '出口收费站', '入口站', '交易时间', '货物', '车辆归属地']]
    dfillegal = dfillegal.ix[:, ['车型', '轴数', '重量', '金额', '出口收费站', '入口站', '交易时间', '货物', '车辆归属地']]
    return dflegal, dfillegal


# 存储用户画像到数据库
def userpicData2mysql():
    dfpic = dfuserpic()
    dfpic.drop(columns=['freq_outin', 'freq_goods'], inplace=True)
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(dfpic, 'car_info_userpic', netconnect, schema='lvtong')


# 存储映射表到数据库，更新模型时候可能要更新
def maplabeling2mysql(dfmap, graphname):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(dfmap, graphname, netconnect, schema='lvtong')


# 通用读取函数
def readaAllFromMysql(graphName):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    sql = 'select * from ' + graphName + ';'
    df = pd.read_sql_query(sql, netconnect)
    return df


# 违规因子检测功能模块根据输入车牌号查询车辆画像表
def querybycarid(caridin, graphName='car_info_userpic'):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    sql = "select caridrepeated,illegaltimes,appeartimes,travel_distance_avg,outin_freq1," \
          "outin_freq1_times,goods_freq1,goods_freq1_times from " + graphName + " where carid ='" + caridin + "';"
    df = pd.read_sql_query(sql, netconnect)
    return df


# 登录界面id 密码查询函数
def userloginQuery(employid):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    sql = 'select * from USER WHERE employid="%s"' % (employid)
    df = pd.read_sql_query(sql, netconnect)
    return df


# 手动插入用户表的函数
def insertUserInfo2Mysql(df):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    pd.io.sql.to_sql(df, 'user', netconnect, schema='lvtong')


# 统计表中数据总条数，统计近一年插入条数。
def queryUpdateRecords(graphName):
    connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
    sql1 = 'select count(1) from ' + graphName + ';'
    df = pd.read_sql_query(sql1, netconnect)
    return df


# if __name__ == '__main__':
#     # df = readaAllFromMysql('car_info_userpic')
#     # df = querybycarid('BA88868')
#     # print(df)
#     # 插入数据挖掘表及数据
#     # dflegal,dfillegal = dataPreProcess()
#     # print(dflegal.info())
#     # store2lvtong(dflegal,'car_leagal_4rulemining')
#     # store2lvtong(dfillegal,'car_illeagal_4rulemining')
#     # 插入用户信息
#     # time = QDateTime.currentDateTime()
#     # timeDisplay = time.toString('yyyy-MM-dd hh:mm:ss')
#     # columns = ['employid','password','usergroup']
#     # df1 = pd.DataFrame([['neunn','123','common'],['zs','zs','admin']],index=[0,1],columns=columns)
#     # print(df1)
#     # ##df2 = pd.DataFrame(np.array(['zs','zs','admin']).reshape(1,-1),columns=columns)
#     # insertUserInfo2Mysql(df1)
#     ##insertUserInfo2Mysql(df2)
#     # 测试loginquery
#     df = userloginQuery('neunn')
#     # print(len(df))


def food_tags(x):
    # 150种货物分成六类，无暂时归蔬菜类
    vegatables = ['豇豆', '大葱', '生菜', '洋葱', '茼蒿', '生姜', '甘薯', '萝卜', '西红柿', '茄子', '韭菜', '蒜苔', '黄瓜', '菜花', '冬瓜', '蘑菇',
                  '大白菜', '西兰花', '香菜', '四季豆', '芹菜', '豆芽', '大蒜', '马铃薯', '辣椒', '油菜', '菠菜', '山药', '空心菜', '红薯', '结球甘蓝',
                  '小青菜', '金针菇', '西葫芦', '蒜苗', '胡萝卜', '原菇', '扁豆', '莲藕', '青椒', '紫菜', '香葱', '南瓜', '莴笋', '鲜花生', '平菇',
                  '茴香',
                  '金针菜(黄花菜)', '四棱豆', '鲜玉米', '荚豆', '豌豆苗', '佛手瓜', '芋头', '芦笋', '苦瓜', '苋菜', '豌豆', '竹笋', '白薯', '芥蓝',
                  '丝瓜',
                  '菜薹', '水芹', '毛豆', '茭白', '芜菁', '滑菇', '香椿', '蔬菜混合', '木耳菜', '无']
    fruits = ['火龙果', '苹果', '梨', '桔', '橙', '草莓', '猕猴桃', '柿子', '香蕉', '柠檬', '葡萄', '柚', '西瓜', '樱桃', '提子', '山楂', '芒果',
              '伊丽莎白瓜', '桃', '菠萝', '榴莲', '哈密瓜', '枣', '龙眼', '石榴', '桑葚', '椰子', '香瓜', '李', '木瓜', '橄榄', '甜瓜', '柑', '枇杷',
              '杨梅', '杨桃', '番石榴', '荔枝', '华莱士瓜', '杏', '海棠', '水果混合', '无花果', '舌瓜']
    meats = ['鲜牛肉', '鲜羊肉', '鲜猪肉', '鲜鸡肉', '鲜家兔肉', '鲜鹅肉', '鲜鸭肉', '鲜驴肉', '鲜骡肉']
    secondary_product = ['鲜奶', '鸡蛋', '鸭蛋', '鹌鹑蛋', '鹅蛋']
    # 禽畜类
    livestocks = ['猪', '马', '羊', '鸡', '驴', '牛', '鸭', '蜜蜂(转地放蜂)', '鹅', '食用蛙类', '骡', '家兔']
    seafoods = ['虾类', '鱼类', '贝类', '蟹类', '海带', '海参', '海蜇', '海鲜混合']
    if x in vegatables:
        return '蔬菜运输'
    if x in fruits:
        return '水果运输'
    if x in meats:
        return '肉类运输'
    if x in secondary_product:
        return '农副产品运输'
    if x in livestocks:
        return '禽畜类运输'
    if x in seafoods:
        return '水产品运输'


def dfuserpic():
    df = readfile2df.readfile()
    df['carid'] = df['车牌号']
    df['cartype'] = df['车型']
    # 想要载重量，但是查不到，先用轴数代替
    df['axle'] = df['轴数']
    df['weight'] = df['重量']
    df['out-in'] = df['出口收费站'].map(lambda x: x[:-3] + '到') + df['入口站'].map(lambda x: x[:-3])

    df['goodskind'] = df['货物'].map(food_tags)
    df['month'] = df['交易时间'].map(lambda x: (x.split(' ')[0]).split('/')[1:])
    df['month'] = df['month'].map(lambda x: str(x[0]) + '前半月' if int(x[1]) < 15 else str(x[0]) + '后半月')

    # 构造时间间隔
    df['交易时间'] = pd.to_datetime(df['交易时间'])
    df['入口时间'] = pd.to_datetime(df['入口时间'])
    # df['interval'] = pd.to_numeric(df['交易时间'] - df['入口时间'])
    df['interval'] = (df['交易时间'] - df['入口时间'])
    import math
    df['interval'] = df['interval'].map(lambda x: str(math.ceil(x.seconds / 3600)) + '小时车程')
    df['legaltag'] = df['收费类型（正常，违规，假冒）'].map(lambda x: 0 if x == '正常' else 1)

    # 建立用户横表
    dfpic = pd.DataFrame(index=df['车牌号'].unique())
    dfpic['carid'] = df['车牌号'].unique()
    # 统计套牌车
    cartype = df.groupby(['车牌号', '车型'])['车型'].count().unstack(level=0)
    dfpic['caridrepeated'] = cartype.nunique()
    dfpic['caridrepeated'] = dfpic['caridrepeated'].map(lambda x: 0 if x == 1 else 1)

    dftemp1 = pd.DataFrame([cartype.index[cartype[i].notnull()].values[-1] for i in cartype], index=cartype.columns)
    dftemp1.columns = ['cartype']

    # 统计轴数
    caraxlenums = df.groupby(['车牌号', '轴数'])['轴数'].count().unstack(level=0)
    dftemp2 = pd.DataFrame([caraxlenums.index[caraxlenums[i].notnull()].values[-1] for i in caraxlenums],
                           index=caraxlenums.columns)
    dftemp2.columns = ['axle']

    # 统计违法次数
    # 没经过详细测试，结果在应用时发现数据库存的一部分数据有问题，尤其时违规次数和出现次数的算法，2018/12/5
    # 经过详细测试发现没有bug，是因为建立用户画像表的时候数据已经经过预处理了，只选取了2018年的数据，
    # 而辽GP0002违法的第57号数据发生在17年十二月，所以统计出现了14次，没有违法记录
    # df[df['carid']=='云K17051'] 可以看出原始数据中 出现了5次，违法次数为0次
    # dftemp3.loc['云K17051'] dftemp4.loc['云K17051'] 显示出现次数为5次，违法次数为0次
    # 查原始数据df_orignal = readfile()
    # df_orignal['收费类型（正常，违规，假冒）'][df_orignal['车牌号']=='辽GP0002'] 出现了15次，1次违法
    # 但是为什么对于违法车辆的统计就不对了呢 df[df['carid']=='辽GP0002'] 出现了14次 ,显示无违法，df的['legaltag']都不对吗
    # dftemp4.loc['辽GP0002']
    dftemp3 = df.groupby(['车牌号'])['legaltag'].sum()
    dftemp3.name = 'illegaltimes'
    # dfpic[dfpic['carid']=='黑RS3566']['cartype'] 应该是二型货，查询dfpic看看对不对
    # dfpic[dfpic['carid']=='EC85375']['cartype']  计货2
    # dfpic[dfpic['carid']=='黑RG0666']['caraxlenums'] 0轴1次，2轴13次

    # 统计上道次数
    dftemp4 = df.groupby(['车牌号'])['legaltag'].count()
    dftemp4.name = 'appeartimes'
    # 先合并一个基础dfpic
    dfpic = pd.concat([dfpic, dftemp1, dftemp2, dftemp3, dftemp4], axis=1)

    # 统计平均违法金额
    dfpic['illegal_account_avg'] = (df.ix[df['legaltag'] == 1]).groupby(['carid'])['金额'].mean()
    dfpic['illegal_account_avg'].fillna(0)
    # 统计正常平均缴费金额
    dfpic['legal_account_avg'] = (df.ix[df['legaltag'] == 0]).groupby(['carid'])['金额'].mean()

    # 统计平均行驶距离
    df['interval_int'] = df['interval'].map(lambda x: int(x[:1]))
    dfpic['travel_distance_avg'] = df.groupby('carid')['interval_int'].mean()
    dfpic['travel_distance_avg'] = dfpic['travel_distance_avg'].map(lambda x: str(int(round(x))) + '小时车程')

    # 统计常用出入口 outin_freq1，outin_freq2，outin_freq3
    freq_outin = df.groupby(['车牌号', 'out-in'])['out-in'].count()
    # 测试用例，carid第零行'辽G3098X'  freq.ix['辽G3098X']，返回series,再对每个series操作取出前三
    dfpic['freq_outin'] = dfpic['carid'].map(lambda x: freq_outin.ix[x])
    # dfpic['freq_outin'][0].index Index(['沟帮子到盘锦', '盘锦到沟帮子'], dtype='object', name='out-in') [3,79]
    dfpic['outin_freq1'] = dfpic['freq_outin'].map(lambda x: x.argmax())
    dfpic['outin_freq1_times'] = dfpic['freq_outin'].map(lambda x: x.max())

    # 统计常拉货物 goods_freq1,goods_freq2,goods_freq3
    freq_goods = df.groupby(['车牌号', 'goodskind'])['goodskind'].count()
    dfpic['freq_goods'] = dfpic['carid'].map(lambda x: freq_goods.ix[x])
    dfpic['goods_freq1'] = dfpic['freq_goods'].map(lambda x: x.argmax())
    dfpic['goods_freq1_times'] = dfpic['freq_goods'].map(lambda x: x.max())

    dfpic.index = range(len(dfpic))
    return dfpic
