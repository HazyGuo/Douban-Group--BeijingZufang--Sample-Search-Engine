import jieba
import pandas as pd
from collections import defaultdict
from bloomfilter import BloomFilter

class SearchEngine:
    def __init__(self):
        self.filter = BloomFilter(10000)
        self.terms = defaultdict(set)
        self.urls = []
        self.generate_engine()

    def generate_engine(self):
        names = ['url', 'title']
        df = pd.read_csv('no_intermediary_data.csv', sep=',', encoding='utf-8', header=None, names=names)
        for i in range(1, len(df)):
            urlid = len(self.urls)
            self.urls.append(df.iloc[i]['url'])
            for term in jieba.cut_for_search(df.iloc[i]['title']):
                self.filter.add_value(term)
                self.terms[term].add(urlid)

    def search(self, term):
        if not self.filter.might_contain(term):
            return
        if term not in self.terms:
            return
        for uid in sorted(self.terms[term]):
            yield self.urls[uid]

    def search_all(self, terms=[]):
        result = set(range(len(self.urls)))
        for term in terms:
            if not self.filter.might_contain(term) or term not in self.terms:
                return
            result = result.intersection(self.terms[term])
        for uid in sorted(result):
            yield self.urls[uid]

    def search_any(self, terms):
        result = set()
        for term in terms:
            if not self.filter.might_contain(term) or term not in self.terms:
                continue
            result = result.union(self.terms[term])
        for uid in sorted(result):
            yield self.urls[uid]

if __name__ == '__main__':
    searcher = SearchEngine()
    for url in searcher.search('西二旗'):
       print(url)
    print('-'*20)
    for url in searcher.search_all(['西二旗', '地铁']):
        print(url)
    print('-' * 20)
    for url in searcher.search_any(['西二旗', '地铁']):
        print(url)