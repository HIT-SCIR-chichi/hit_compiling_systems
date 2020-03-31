#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


def get_line_num(text, idx) -> int:  # 获得text中idx位置的行号
    line_num = 1
    for idy, char in enumerate(text):
        if char == '\n':
            line_num += 1
        if idx == idy:
            return line_num
    return -1


class Lexical:

    def __init__(self):
        self.state_number = 0  # 状态数目
        self.start_state = 0  # 开始状态编号
        self.char = []  # 状态转移表中的所有引起转移的符号终结符集合，包括'other',注意结束符'\0'在json文件中存储方式为'\\0'
        self.token_with_info = []  # 除种别码外需要带有信息的状态
        self.end_state = {}  # 结束状态编号及其对应的描述
        self.end_state_less_info = {}  # 结束状态编号及其简略描述
        self.err_info = {}  # 错误代码及其处理信息
        self.key_word = []  # 关键字集合
        self.dfa = {}  # dfa转换表
        self.nfa = {}  # nfa转换表

    def get_dfa(self, dfa_path):  # 从文件中获取必要的dfa信息
        with open(dfa_path, 'r', encoding='utf-8') as dfa_file:
            dic = json.loads(dfa_file.read())
            self.state_number = dic['state_number']
            self.start_state = dic['start_state']
            self.char = [each if each != '\\0' else '\0' for each in dic['char']]  # 对json文件中的'\0'转义
            self.token_with_info = dic['token_with_info']
            self.end_state = {int(item[0]): item[1] for item in dic['end_state'].items()}
            self.end_state_less_info = {int(item[0]): item[1] for item in dic['end_state_less_info'].items()}
            self.err_info = {int(item[0]): item[1] for item in dic['error_info'].items()}
            self.key_word = dic['key_word']
            self.dfa = {idx: {idy if idy != '\\0' else '\0': dic[str(idx)][idy] for idy in dic[str(idx)]}
                        for idx in range(0, self.state_number) if str(idx) in dic}  # 对json文件中的'\0'转义

    def get_nfa(self, nfa_path):  # 从文件中获取nfa
        with open(nfa_path, 'r', encoding='utf-8') as nfa_file:
            dic = json.loads(nfa_file.read())
            self.nfa['state_number'] = dic['state_number']  # 状态数
            self.nfa['start_state'] = dic['start_state']  # 开始状态
            self.nfa['end_state'] = {int(item[0]): item[1] for item in dic['end_state'].items()}  # 终结状态集合
            self.nfa['null'] = '\0'  # 表示空串
            self.nfa['char'] = [char if char != '\\0' else '\0' for char in dic['char']]  # 字符集
            self.nfa['nfa_table'] = {int(idx): {char if char != '\\0' else '\0': dic['nfa_table'][idx][char] for char
                                                in dic['nfa_table'][idx]} for idx in dic['nfa_table']}

    def get_closure(self, states: list) -> list:  # 获得ε闭包，输入为状态集
        res, nfa_table = states.copy(), self.nfa['nfa_table']  # 求闭包的结果，进行浅层复制即可
        while len(states) != 0:
            top_state = states.pop()
            if self.nfa['null'] in nfa_table[top_state]:  # 存在空转移
                state_lst = nfa_table[top_state][self.nfa['null']]
                for state in state_lst:
                    if state not in res:
                        states.append(state)  # 入栈
                        res.append(state)  # 加入到闭包中
        return res

    def nfa2dfa(self):  # nfa转换为dfa转换表
        def get_unmarked_state(flags: list):
            for x, flag in enumerate(flags):
                if not flag:
                    return x

        def move(states, a):
            res_states = []
            for state in states:
                if state in self.nfa['nfa_table'] and a in self.nfa['nfa_table'][state]:
                    res_states.extend(self.nfa['nfa_table'][state][a])
            return res_states

        dfa_table, start_closure = {}, self.get_closure([self.nfa['start_state']])  # nfa的开始状态组成的闭包
        state_closure, state_flag = [start_closure], [False]  # 保存状态闭包,保存状态闭包的标志
        unmark_state_idx = get_unmarked_state(state_flag)
        while unmark_state_idx is not None:
            state_closure_unmark, state_flag[unmark_state_idx] = state_closure[unmark_state_idx], True  # 加上标记
            for char in self.nfa['char']:
                u = self.get_closure(move(state_closure_unmark, char))
                if len(u) > 0:
                    if u not in state_closure:
                        state_closure.append(u)
                        state_flag.append(False)
                    if unmark_state_idx not in dfa_table:
                        dfa_table[unmark_state_idx] = {}
                    dfa_table[unmark_state_idx][char] = state_closure.index(u)
            unmark_state_idx = get_unmarked_state(state_flag)
        end_states = [idx for state in self.nfa['end_state'] for idx, item in enumerate(state_closure) if state in item]
        return {'start_state': 0, 'states': state_closure, 'char': self.nfa['char'], 'end_states': end_states,
                'dfa_table': dfa_table}

    def lexical_run(self, text):  # 基于DFA的词法分析，在text中加入了'\0'结束符
        res, error, text = {}, {}, text + '\0'  # 结果集合，错误集合，text加上结束符标志
        state, idx, next_char = self.start_state, 0, text[0]  # 记录状态,字符长度,当前字符
        end_save, last_str = (-12, '', -1), ''  # 保存的上一个终结状态、对应串和索引，last_str保存字串
        while idx < len(text):
            if next_char == '\0':
                break
            end_save = (state, last_str, idx) if state in self.end_state else end_save  # 更新保存状态
            next_char = text[idx]
            last_str, idx = last_str + next_char if next_char != '\0' else last_str, idx + 1
            next_state = self.__get_next_state(state, next_char)  # 如果存在则获得下一个状态
            if next_state is not None:  # 更新状态
                state = next_state
            if next_state is None or state < 0:
                if state < 0:
                    line_num = get_line_num(text, idx - 1)
                    res[len(res)] = last_str, state, self.err_info[state], line_num  # 错误信息
                    error[len(error)] = last_str, state, self.err_info[state], line_num
                if end_save[0] != -12:
                    idx = end_save[2]  # 进行状态回退
                    line_num = get_line_num(text, idx - 1)
                    if end_save[0] in self.token_with_info:
                        res[len(res)] = end_save[1], self.end_state_less_info[end_save[0]], end_save[1], line_num
                    elif self.end_state[end_save[0]] == '标识符关键字' and end_save[1] not in self.key_word:
                        res[len(res)] = end_save[1], 'IDN', end_save[1], line_num
                    else:
                        res[len(res)] = end_save[1], end_save[1].upper(), '_', line_num
                state, end_save, last_str = 0, (-12, '', -1), ''
        return res, error

    def __get_next_state(self, state, char):
        if state in self.dfa:
            for item in self.dfa[state].items():
                if char in item[0] and item[0] != 'other':
                    return item[1]
            if char not in str.join('', self.char) and 'other' in self.dfa[state]:
                return self.dfa[state]['other']

    def get_dfa_table(self):
        return self.state_number, self.char, self.dfa, self.end_state, self.err_info


def main():
    lexical = Lexical()
    lexical.get_nfa('./input/nfa.json')
    lexical.nfa2dfa()
    lexical.get_dfa('./input/dfa.json')
    res = lexical.lexical_run(open('./input/wrong_test.c', 'r', encoding='utf-8').read())
    for key in res[1]:
        print(res[1][key])


if __name__ == '__main__':
    main()
