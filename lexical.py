#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


# todo 除标识符外，一词一码
# todo 将char中的结束符'\\0'换为'\0'
# todo 运算符！遇到#等报错
# todo 单行注释遇到'\n'的情况
# todo 代码文本中遇到'\0'需要转义为'\\0'(类似情况同样需要考虑)
class Lexical:

    def __init__(self):
        self.state_number = 0  # 状态数目
        self.start_state = 0  # 开始状态编号
        self.char = []  # 状态转移表中的所有引起转移的符号终结符集合，包括'other',注意结束符'\0'在json文件中存储方式为'\\0'
        self.end_state = {}  # 结束状态编号及其对应的描述
        self.error_info = {}  # 错误代码及其处理信息
        self.key_word = []  # 关键字集合
        self.dfa = {}  # dfa转换表
        self.nfa = {}  # nfa转换表
        self.rules = {}  # 词法规则

    def get_dfa(self, dfa_path):  # 从文件中获取必要的dfa信息
        with open(dfa_path, 'r', encoding='utf-8') as dfa_file:
            dic = json.loads(dfa_file.read())
            self.state_number = dic['state_number']
            self.start_state = dic['start_state']
            self.char = [each if each != '\\0' else '\0' for each in dic['char']]  # 对json文件中的'\0'转义
            self.end_state = {int(idx): dic['end_state'][idx] for idx in dic['end_state']}
            self.error_info = dic['error_info']
            self.key_word = dic['key_word']
            self.dfa = {idx: {idy if idy != '\\0' else '\0': dic[str(idx)][idy] for idy in dic[str(idx)]}
                        for idx in range(0, self.state_number) if str(idx) in dic}  # 对json文件中的'\0'转义

    def get_nfa(self, nfa_path):  # 从文件中获取nfa
        with open(nfa_path, 'r', encoding='utf-8') as nfa_file:
            self.nfa = json.loads(nfa_file.read())

    def dfa2nfa(self):  # dfa转换为nfa转换表
        pass

    def nfa2dfa(self):  # nfa转换为dfa转换表
        pass

    def lexical_run(self, text):  # 基于DFA的词法分析，在text中加入了'\0'结束符
        res = {}  # 结果集合
        text += '\0'  # 加上结束符标志
        state, idx_count, next_char = self.start_state, 0, text[0]  # 记录状态编号,字符长度,当前字符
        end_state, end_str, last_str = -1, '', ''  # 分析过程中保存的上一个终结状态和对应的分析串，last_str保存字串
        while idx_count <= len(text):
            (end_state, end_str) = (state, last_str) if state in self.end_state else (end_state, end_str)
            if idx_count == len(text):
                if end_state != -1:
                    res[len(res)] = (self.end_state[end_state], end_str)
                break
            next_char = text[idx_count]
            last_str += next_char
            idx_count += 1
            flag = False
            if (next_char is ' ' or next_char is '\n' or next_char is '\t') and state == 0:
                last_str = ''
                continue
            if state in self.dfa:
                if next_char in str.join('', self.char):
                    for key in self.dfa[state]:
                        if next_char in key and key is not 'other':
                            state = self.dfa[state][key]  # 根据状态表更新状态
                            flag = True
                            break
                elif 'other' in self.dfa[state]:
                    state = self.dfa[state]['other']
                    flag = True
            if not flag:
                if end_state == -1:
                    idx_count += 1  # todo
                    print('ERROR')
                else:
                    if self.end_state[end_state] == '标识符关键字':
                        res[len(res)] = (end_str.upper(), '_') if end_str in self.key_word else ('标识符', end_str)
                    else:
                        res[len(res)] = (self.end_state[end_state], end_str)
                state, idx_count = 0, idx_count - 1  # 更新自动机状态与指针
                end_state, end_str, last_str = -1, '', ''  # 更新分析过程中保存的终结状态与对应字串,last_str表示累计的字串
        return res

    def get_dfa_table(self):
        return self.state_number, self.char, self.dfa


if __name__ == '__main__':
    lexical = Lexical()
    lexical.get_dfa('./input/dfa.json')
    with open('./input/right_test.c', 'r', encoding='utf-8') as f:
        print(lexical.lexical_run('  '))
        # print(lexical.lexical_run(f.read()))
