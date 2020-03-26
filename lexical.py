#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


class Lexical:

    def __init__(self):
        self.state_number = 0  # 状态数目
        self.start_state = 0  # 开始状态编号
        self.end_state = []  # 结束状态编号结合
        self.dfa = {}  # dfa转换表
        self.nfa = {}  # nfa转换表
        self.rules = {}  # 词法规则

    def get_dfa(self, dfa_path):  # 从文件中获取dfa
        with open(dfa_path, 'r', encoding='utf-8') as dfa_file:
            dic = json.loads(dfa_file.read())
            self.state_number = dic['state_number']
            self.start_state = dic['start_state']
            self.end_state = dic['end_state']
            for idx in range(0, self.state_number):
                self.dfa[idx] = dic[str(idx)]

    def get_nfa(self, nfa_path):  # 从文件中获取nfa
        with open(nfa_path, 'r', encoding='utf-8') as nfa_file:
            self.nfa = json.loads(nfa_file.read())

    def dfa2nfa(self):  # dfa转换为nfa转换表
        pass

    def nfa2dfa(self):  # nfa转换为dfa转换表
        pass

    def lexical_run(self, text):  # 基于DFA的词法分析
        state, idx_count, next_char = self.start_state, 0, text[0]  # 记录状态编号,字符长度,当前字符
        while idx_count < len(text):
            next_char = text[idx_count]
            idx_count += 1
            if next_char != ' ' and next_char != '\n':
                state = self.dfa[state][next_char]  # 根据状态表更新状态
        if state in self.end_state:
            print(True)
        else:
            print(False)


if __name__ == '__main__':
    lexical = Lexical()
    lexical.get_dfa('./input/dfa.json')
