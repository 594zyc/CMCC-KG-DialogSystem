import jieba
jieba.load_userdict('../data/_add_words.txt')
print(list(jieba.cut('有比这个流量更多的套餐吗')))