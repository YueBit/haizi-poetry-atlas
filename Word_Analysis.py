import jieba.analyse
#需要做关键词分析的文本路径
path = f'/Users/chenyue/Desktop/Haizi_Poem_Explorer/HaiziPoems_PureText.txt'
file_in = open(path, 'r', encoding='UTF-8')
content = file_in.read()
try:
    #停用词表路径
    jieba.analyse.set_stop_words(f'/Users/chenyue/Desktop/Haizi_Poem_Explorer/stop.txt')
    tags = jieba.analyse.extract_tags(content, topK=100, withWeight=True)
    for v, n in tags:
        #算出来的权重是小数，乘以一万用于凑整
        print (v + '\t' + str(int(n * 10000)))

finally:
    file_in.close()