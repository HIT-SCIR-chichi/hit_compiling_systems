#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


class Syntax:

    def __init__(self):
        self.start_symbol = ''  # 文法开始符号
        self.empty_str = ''  # 文法中的空串表示
        self.terminals = []  # 终结符号集合
        self.non_terminals = []  # 非终结符集合
        self.rules = {}  # 文法规则
        self.first = {}  # 所有文法符号的First集合
        self.follow = {}  # 所有文法符号的Follow集合

    def read_syntax(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            js_dic = json.load(f)
            self.start_symbol = js_dic['start_symbol']
            self.empty_str = js_dic['empty_string']
            self.terminals = js_dic['terminals']
            self.non_terminals = js_dic['non_terminals']
            self.rules = {symbol: [item.split() for item in value] for (symbol, value) in js_dic['rules'].items()}

    def get_first(self):
        """获得文法中所有符号的first集."""
        self.first = {terminal: [terminal] for terminal in self.terminals}  # 终结符的First集为自身
        for non_terminal in self.non_terminals:
            self.first[non_terminal] = []
        flag = True  # 迭代更新标志，用于判断是否仍需要一轮迭代
        while flag:
            flag = False
            for non_terminal in self.non_terminals:  # 对每一个非终结符求解First集合
                productions = self.rules[non_terminal]  # 产生式集合
                for production in productions:  # 遍历每一个产生式
                    if production == [self.empty_str]:
                        if self.empty_str not in self.first[non_terminal]:  # 存在未加入到First集中的空串，将其加入到First集合
                            self.first[non_terminal].append(self.empty_str)
                            flag = True
                        continue
                    for symbol in production:  # 遍历非空产生式右部的每一个符号
                        for item in self.first[symbol]:  # 如果是空串，则说明需要处理下一个符号，同时不添加空串到First集中
                            if item != self.empty_str and item not in self.first[non_terminal]:
                                self.first[non_terminal].append(item)
                                flag = True
                        if self.empty_str in self.first[symbol]:  # 右部符号First集含有空串，分析下个符号或将空串加入
                            continue
                        else:  # 右部符号First集不含有空串，说明该产生式分析结束
                            break
                    if self.empty_str in self.first[symbol] and self.empty_str not in self.first[non_terminal]:
                        self.first[non_terminal].append(self.empty_str)  # 若产生式最终可以推导出空串，则将空串加入到First集
                        flag = True


def main():
    syntax = Syntax()
    syntax.read_syntax('help/syntax.json')
    syntax.get_first()


if __name__ == '__main__':
    main()
