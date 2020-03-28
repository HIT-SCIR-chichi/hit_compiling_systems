#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


class Lexical:

    def __init__(self):
        self.state_number = 0  # 状态数目
        self.start_state = 0  # 开始状态编号
        self.end_state = {}  # 结束状态编号及其对应的描述
        self.key_word = []  # 关键字集合
        self.char = ''  # 状态转移表中的所有终结符
        self.dfa = {}  # dfa转换表
        self.nfa = {}  # nfa转换表
        self.rules = {}  # 词法规则

    def get_dfa(self, dfa_path):  # 从文件中获取必要的dfa信息
        with open(dfa_path, 'r', encoding='utf-8') as dfa_file:
            dic = json.loads(dfa_file.read())
            self.state_number = dic['state_number']
            self.start_state = dic['start_state']
            self.end_state = {int(idx): dic['end_state'][idx] for idx in dic['end_state'].keys()}
            self.key_word = dic['key_word']
            self.char = dic['char']
            self.dfa = {idx: dic[str(idx)] for idx in range(0, self.state_number) if str(idx) in dic}

    def get_nfa(self, nfa_path):  # 从文件中获取nfa
        with open(nfa_path, 'r', encoding='utf-8') as nfa_file:
            self.nfa = json.loads(nfa_file.read())

    def dfa2nfa(self):  # dfa转换为nfa转换表
        pass

    def nfa2dfa(self):  # nfa转换为dfa转换表
        pass

    def lexical_run(self, text):  # 基于DFA的词法分析
        res = {}  # 结果集合
        state, idx_count, next_char = self.start_state, 0, text[0]  # 记录状态编号,字符长度,当前字符
        end_state, end_str, last_str = -1, '', ''  # 分析过程中保存的上一个终结状态和对应的分析串，last_str保存字串
        while idx_count < len(text):
            (end_state, end_str) = (state, last_str) if state in self.end_state else (end_state, end_str)
            next_char = text[idx_count]
            last_str += next_char
            idx_count += 1
            flag = False
            if (next_char is ' ' or next_char is '\n' or next_char is '\t') and state == 0:
                last_str = ''
                continue
            if state in self.dfa:
                if next_char in self.char:
                    for key in self.dfa[state]:
                        if next_char in key and key is not 'other':
                            state = self.dfa[state][key]  # 根据状态表更新状态
                            flag = True
                            break
                elif 'other' in self.dfa[state]:
                    state = self.dfa[state]['other']
                    flag = True
            if not flag:
                res[len(res)] = (self.end_state[end_state], end_str)  # 保存结果
                print(res[len(res) - 1])
                state, idx_count = 0, idx_count - 1  # 更新自动机状态与指针
                end_state, end_str, last_str = -1, '', ''  # 更新分析过程中保存的终结状态与对应字串,last_str表示累计的字串


if __name__ == '__main__':
    lexical = Lexical()
    lexical.get_dfa('./input/dfa.json')
    with open('./input/right_test.c', 'r', encoding='utf-8') as f:
        lexical.lexical_run(f.read())
