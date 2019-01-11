import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import re
from scipy import sparse
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold

from sklearn.preprocessing import OneHotEncoder
import lightgbm as lgb

traindf_1227 = pd.read_csv('jinnan_round1_train_20181227.csv', encoding='gbk')
testAdf_1227 = pd.read_csv('jinnan_round1_testA_20181227.csv', encoding='gbk')

# 在控制台显示所有的列，而不是以省略号方式隐藏,设置一次即可生效
pd.set_option('display.max_columns', None)

# a2,a7,a8,b11空值率很高
# 首要问题是空值率这么高的这些列怎么处理
stats = []
for col in traindf_1227.columns:
    stats.append((col, traindf_1227[col].nunique(), traindf_1227[col].isnull().sum() * 100 / traindf_1227.shape[0],
                  traindf_1227[col].value_counts(normalize=True, dropna=False).values[0], traindf_1227[col].dtype))
stats_df = pd.DataFrame(stats, columns=['Feature', 'unique_values', 'percentage_of_missing_values', 'biggest_categroy',
                                        'type'])

stats_df.sort_values('percentage_of_missing_values', ascending=False)[:10]

stats_test = []
for col in testAdf_1227.columns:
    stats_test.append((col, testAdf_1227[col].nunique(), testAdf_1227[col].isnull().sum() * 100 / testAdf_1227.shape[0],
                       testAdf_1227[col].value_counts(normalize=True, dropna=False).values[0], testAdf_1227[col].dtype))
stats_test_df = pd.DataFrame(stats_test,
                             columns=['Feature', 'unique_values', 'percentage_of_missing_values', 'biggest_categroy',
                                      'type'])
stats_test_df.sort_values('percentage_of_missing_values', ascending=False)[:10]

# 如果特征只有一个类别，或某些特征中某一类的比例高于90%，将这列删除
for df in [traindf_1227, testAdf_1227]:
    df.drop(['B3', 'B13', 'A13', 'A18', 'A23'], axis=1, inplace=True)
good_cols = list(traindf_1227.columns)
for col in traindf_1227.columns:
    rate = traindf_1227[col].value_counts(normalize=True, dropna=False).values[0]
    if rate > 0.9:
        good_cols.remove(col)

# 发现预测结果 收率 整体在0.8以上，只有几个在这之下，因此可以删除这些离群点
traindf_1227 = traindf_1227[traindf_1227['收率'] > 0.8]

traindf_1227 = traindf_1227[good_cols]

testAdf_1227 = testAdf_1227[good_cols]

# a5，a7,a9,a11,a14,a16,a20,a24,a26,a28,b4,b5,b7,b9,b10,b11为时间特征或时间区间特征
# 其他为数据特征

# 对预测维度进行分析
target_col = '收率'
# 设定图纸大小,可跳过使用默认，只是保存时，图片的大小不一样
plt.figure(figsize=(8, 6))
# 画散点图
plt.scatter(range(traindf_1227.shape[0]), np.sort(traindf_1227[target_col].values))
plt.xlabel('index', fontsize=12)
plt.ylabel('yield', fontsize=12)
plt.show()
# 画柱状图
sns.distplot(traindf_1227[target_col].values, bins=50, kde=False, color='red')
plt.title('histogram of yield')
plt.xlabel('yield', fontsize=12)
plt.show()

# 数据预处理
# 1.去除缺失值大于90%的特征
# 2.去除类别唯一的特征
# 3.时间特征处理
# 4.进行label encoder
# 5.进行onehot编码

# 合并训练集和测试集
target = traindf_1227['收率']
del traindf_1227['收率']
data = pd.concat([traindf_1227, testAdf_1227], axis=0, ignore_index=True)
data = data.fillna(-1)


def timeTransform(t):
    try:
        t, m, s = t.splite(':')
    # 数据里有一些不是时分秒格式的数据，要对应的搞出来，我之前没有异常捕获，不够健壮
    except:
        if t == '1900/1/9 7:00':
            return 7 * 3600 / 3600
        elif t == '1900/1/1 2:30':
            return (2 * 3600 + 30 * 60) / 3600
        elif t == -1:
            return -1
        else:
            return 0

    try:
        # 把时间格式转换为一个浮点数
        tm = (int(t) * 3600 + int(m) * 60 + int(s)) / 3600
    except:
        return (30 * 60) / 3600

    return tm


for f in ['A5', 'A7', 'A9', 'A11', 'A14', 'A16', 'A24', 'A26', 'B5', 'B7']:
    try:
        data[f] = data[f].apply(timeTransform)
    except:
        print(f, '已经删除')


# 进行时段类型数据的转化
def getDuration(se):
    try:
        # 返回结果符合以下条件：数字出现一次及以上，.出现一次及以下，数字出现零次及以上
        # re.findall(r'\d+\.?\d*','21:30-23:30')
        # ['21', '30', '23', '30']

        sh, sm, eh, em = re.findall(r'\d+\.?\d*', se)
    except:
        # 如果该位置原来为空值，返回0
        if se == -1:
            return 0

    try:
        # 如果start小时大于end小时，就取对应的补时，反之直接相减即可
        if int(sh) > int(eh):
            tm = (int(eh) * 3600 + int(em) * 60 - int(sm) * 60 - int(sh) * 3600) / 3600 + 24
        else:
            tm = (int(eh) * 3600 + int(em) * 60 - int(sm) * 60 - int(sh) * 3600) / 3600
    except:
        # 异常值捕获
        if se == '19:-20:05':
            return 1
        elif se == '15:00-1600':
            return 1

    return tm


for f in ['A20', 'A28', 'B4', 'B9', 'B10', 'B11']:
    # 以下两种写法时一样的
    # data[f] = data.apply(lambda df: getDuration(df[f]),axis=1)
    data[f] = data[f].apply(getDuration)

# 样本id直接被作为特征抽取出来了
data['样本id'] = data['样本id'].apply(lambda x: int(x.split('_')[1]))

# 取出其他特征名放入列表
categorical_columns = [f for f in data.columns if f not in ['样本id']]

# numerical_columns
# ['样本id']
numerical_columns = [f for f in data.columns if f not in categorical_columns]

# label encoder
for f in categorical_columns:
    # unique 求种类列表 如A1[300, 250, 200]
    # nunique 求种类总数 dict生成对应的映射表{200: 2, 250: 1, 300: 0}
    data[f] = data[f].map(dict(zip(data[f].unique(), range(0, data[f].nunique()))))

train = data[:traindf_1227.shape[0]]
test = data[traindf_1227.shape[0]:]

# 进行one-hot编码
X_train = train[numerical_columns].values
X_test = test[numerical_columns].values

enc = OneHotEncoder()
for f in categorical_columns:
    # 学习one_hot
    enc.fit(data[f].values.reshape(-1, 1))
    # 横向合并X_train和稀疏后的features, 并存储为csr格式
    X_train = sparse.hstack((X_train, enc.transform(train[f].values.reshape(-1, 1))), 'csr')
    X_test = sparse.hstack((X_test, enc.transform(test[f].values.reshape(-1, 1))), 'csr')

y_train = target.values

param = {'num_leaves': 30,
         'min_data_in_leaf': 30,
         'objective': 'regression',
         'max_depth': -1,
         'learning_rate': 0.01,
         "min_child_samples": 30,
         "boosting": "gbdt",
         "feature_fraction": 0.9,
         "bagging_freq": 1,
         "bagging_fraction": 0.9,
         "bagging_seed": 11,
         "metric": 'mse',
         "lambda_l1": 0.1,
         "verbosity": -1}

# 5折交叉验证
folds = KFold(n_splits=5, shuffle=True, random_state=42)
oof = np.zeros(len(train))
predictions = np.zeros(len(test))

for fold_, (trn_idx, val_idx) in enumerate(folds.split(X_train, y_train)):
    print('fold n {}'.format(fold_ + 1))
    trn_data = lgb.Dataset(X_train[trn_idx], y_train[trn_idx])
    val_data = lgb.Dataset(X_train[val_idx], y_train[val_idx])

    num_round = 10000
    clf = lgb.train(param, trn_data, num_round, valid_sets=[trn_data, val_data], verbose_eval=200,
                    early_stopping_rounds=100)
    oof[val_idx] = clf.predict(X_train[val_idx], num_iteration=clf.best_iteration)
    predictions += clf.predict(X_test, num_iteration=clf.best_iteration) / folds.n_splits

print('cv score: {:<8.5f}'.format(mean_squared_error(oof,target)))


# 提交结果
# 读入提供的提交格式
#注意header = None一定要写，不然会把第一行默认当作表头
sub_df = pd.read_csv('jinnan_round1_submit_20181227.csv',header=None)
sub_df[1] = predictions
sub_df.to_csv('subline_jinnan.csv',index=False,header=None)