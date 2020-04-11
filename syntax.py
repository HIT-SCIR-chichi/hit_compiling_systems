#!/usr/bin/python
# -*- coding: utf-8 -*-
import json


class Syntax:

    def __init__(self):
        self.start_symbol = ''  # 文法开始符号
        self.empty_str = ''  # 文法中的空串表示
        self.terminals = []  # 终结符号集合
        self.non_terminals = []  # 非终结符集合
        self.rules = []  # 所有的文法规则
        self.first = {}  # 所有文法符号的First集合
        self.follow = {}  # 所有文法符号的Follow集合
        self.select = []  # 所有产生式的Select集合

    def read_syntax(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            js_dic = json.load(f)
            self.start_symbol = js_dic['start_symbol']
            self.empty_str = js_dic['empty_string']
            self.terminals = js_dic['terminals']
            self.non_terminals = js_dic['non_terminals']
            for key, values in js_dic['rules'].items():
                for value in values:
                    self.rules.append((key, value.split()))

    def get_first(self):
        """获得文法中所有符号的first集."""
        self.first = {terminal: [terminal] for terminal in self.terminals}  # 终结符的First集为自身
        for non_terminal in self.non_terminals:
            self.first[non_terminal] = []
        flag = True  # 迭代更新标志，用于判断是否仍需要一轮迭代
        while flag:
            flag = False
            for non_terminal, production in self.rules:  # 遍历每一个产生式
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

    def get_str_first(self, symbols: list) -> list:
        """获取文法符号串的First集.

        要求syntax对象已经执行过get_first()方法，如果参数symbols为空列表[]，返回值为空列表[].
        Args:
            symbols: 文法符号串.
        Returns:
            文法符号串symbols的First集
        """
        res = []
        if symbols:
            for symbol in symbols:
                res.extend(item for item in self.first[symbol] if item not in res and item != self.empty_str)
                if self.empty_str in self.first[symbol]:
                    continue
                else:
                    break
            if self.empty_str in self.first[symbol] and self.empty_str not in res:
                res.append(self.empty_str)
        return res

    def get_follow(self):
        """获得文法中所有非终结符的Follow集.

        要求syntax对象已经执行过get_first()方法.
        """
        self.follow = {non_terminal: [] for non_terminal in self.non_terminals}  # 初始化Follow集
        self.follow[self.start_symbol].append('$')  # 将$符号加入到文法开始符号的Follow集中
        flag = True  # 迭代更新标志，用于判断是否仍需要一轮迭代
        while flag:
            flag = False
            for non_terminal, production in self.rules:  # 遍历每一个产生式
                if production != [self.empty_str]:  # 空产生式不会更新Follow集
                    for idx, symbol in enumerate(production):
                        if symbol in self.non_terminals:  # 跳过终结符
                            str_first = self.get_str_first(production[idx + 1:])
                            for item in str_first:
                                if item != self.empty_str and item not in self.follow[symbol]:
                                    self.follow[symbol].append(item)  # 加入symbol后所有文法符号的First集中未出现的元素
                                    flag = True
                            if not str_first or self.empty_str in str_first:  # 后续文法符号可以产生空串或者无后续符号
                                for item in self.follow[non_terminal]:
                                    if item not in self.follow[symbol]:
                                        self.follow[symbol].append(item)
                                        flag = True

    def get_select(self):
        """获得文法中所有产生式的Select集.

        要求syntax对象已经执行过get_first()和get_follow()方法.
        """
        for idx, (non_terminal, production) in enumerate(self.rules):  # 遍历每一个产生式
            if production == [self.empty_str]:  # 空产生式的select集为左部的Follow集
                self.select.append(self.follow[non_terminal])
            else:
                str_first = self.get_str_first(production)  # 计算A->α中的α的First集
                if self.empty_str not in str_first:
                    self.select.append(str_first)
                else:  # First集中存在空串，则select集为(First(α)-{空串}) ∪ Follow(A)，这里采用set的union方法操作
                    self.select.append(
                        set(item for item in str_first if item != self.empty_str).union(self.follow[non_terminal]))


def main():
    syntax = Syntax()
    syntax.read_syntax('help/syntax.json')
    syntax.get_first()
    syntax.get_follow()
    syntax.get_select()


if __name__ == '__main__':
    main()
