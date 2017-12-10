import math
import jieba.analyse
import pandas as pd

def extract_tags(content):
    jieba.analyse.set_idf_path('idf.douban.txt.big')
    tags = jieba.analyse.extract_tags(content, topK=20, withWeight=True)
    return tags

def merge_tags(tags1, tags2):
    dic_tags1 = {t[0]: t[1] for t in tags1}
    dic_tags2 = {t[0]: t[1] for t in tags2}
    merged_tags = set(list(dic_tags1.keys()) + list(dic_tags2.keys()))
    v1 = []
    v2 = []
    for key in merged_tags:
        if key in dic_tags1:
            v1.append(dic_tags1[key])
        else:
            v1.append(0)
        if key in dic_tags2:
            v2.append(dic_tags2[key])
        else:
            v2.append(0)
    return v1, v2

def sum_product_vect(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def sqrt_sum_product_vect(vector):
    return math.sqrt(sum_product_vect(vector, vector))

def semilarity(v1, v2):
    return sum_product_vect(v1, v2) / (sqrt_sum_product_vect(v1) * sqrt_sum_product_vect(v2) + 0.00000000001)  # 避免除0错误

if __name__== '__main__':
    names = ['title','time','content','url']
    df = pd.read_csv('cleandata.csv', sep=',', header=None, names=names, encoding='utf-8')
    count = [0] * len(df)
    for i in range(1, len(df)):
        content1 = df.iloc[i]['content']
        tags1 = extract_tags(content1 if not isinstance(content1, (float)) else df.iloc[i]['title'])
        for j in range(i + 1, len(df)):
            content2 = df.iloc[j]['content']
            tags2 = extract_tags(content2 if not isinstance(content2, (float)) else df.iloc[j]['title'])
            v1, v2 = merge_tags(tags1, tags2)
            s = semilarity(v1, v2)
            if s > 0.5:  # 自定义余弦相似度大于0.5即为相似帖子
                count[i] += 1
                count[j] += 1
    urls = []
    titles = []
    for k in range(1, len(count)):
        if count[k] > 3:
            print('{} has been filtered.'.format(df.iloc[k]['url']))
            continue
        else:
            urls.append(df.iloc[k]['url'])
            titles.append(df.iloc[k]['title'])
    data = {'url': urls, 'title': titles}
    df_filtered = pd.DataFrame(data=data, columns=['url', 'title'])  # 按照指定顺序创建
    df_filtered.to_csv('no_intermediary_data.csv', sep=',', encoding='utf-8', index=False)




