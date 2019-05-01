import jieba
import re


def word_seg(doc_lst):
    result = []
    for doc in doc_lst:
        clean_text = re.sub('\s', '', doc)
        result.append([p for p in jieba.cut(clean_text)])
    return result


def count_term_freq(seg_word_lst):
    all_voc = list(set(seg_word_lst))
    result = [(voc, seg_word_lst.count(voc)) for voc in all_voc]
    result = sorted(result, key=lambda x: -x[1])
    return result


"""
在此放入你要新加入的功能，如文字雲
"""
