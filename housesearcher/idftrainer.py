import pandas as pd
import jieba
import math

def train(contents):
    all_dict = {}

    for content in contents:
        cut_line = jieba.cut(content, cut_all=False)
        for term in set(cut_line):
            num = all_dict.get(term, 0)
            all_dict[term] = num + 1

    for term in all_dict:
        w = term.strip()
        if w:
            p = '%.10f' % (math.log10(len(contents) / (all_dict[term] + 1)))
            yield w, p

if __name__ == '__main__':
    name=['title','time','content','url']
    lines = []
    r = pd.read_csv('douban.csv', encoding='utf-8', header=None, names=name, sep=',')
    r.dropna(inplace=True)
    for w, p in train(r['content'][1:]):
        lines.append('{} {}\n'.format(w, p).encode('utf-8'))
    with open('idf.douban.txt.big', 'wb') as idf:
        idf.writelines(lines)