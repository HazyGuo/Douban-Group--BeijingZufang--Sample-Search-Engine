import pandas as pd
#http://blog.csdn.net/zhili8866/article/details/68134481

name = ['title','time','content','url']
df = pd.read_csv('douban.csv', sep=',', header=None,names=name,encoding='utf-8')
df = df[1:]
df = df[df['time'] > '2017-12-01 00:00:00']
df.to_csv('cleandata.csv', sep=',', encoding='utf-8', index=False)

