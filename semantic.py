#!/usr/bin/python
# -*- coding: utf-8 -*-
from syntax import Syntax
import json


class Semantic:
    def __init__(self):
        self.offset = 0  # 偏移量
        self.symbol = {}  # 符号表
        self.code = {}  # 三地址指令和四元式表示{0: (three_addr, quaternion), 1: (three_addr, quaternion)}

    def rule_5(self, id_val, e_val):  # S -> id=E，普通变量赋值
        item = self.lookup(id_val)
        if item is not None:
            three_addr = [id_val, '=', e_val]
            quaternion = ['=', e_val, '_', id_val]
            self.symbol[len(self.symbol)] = (three_addr, quaternion)
        else:
            print('错误：未经声明')

    def lookup(self, id_val):  # 查阅符号表
        return self.symbol[id_val] if id_val in self.symbol else None

    def semantic_run(self):  # 运行语义分析
        syntax = Syntax()
        syntax.syntax_init()


def main():
    semantic = Semantic()
    semantic.symbol['a'] = 1
    semantic.symbol['b'] = 2


if __name__ == '__main__':
    main()
