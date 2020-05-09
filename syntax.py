#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
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
        self.item_collection = []  # 文法的所有项目:[(idx, idy, a)]，其中idx指的是文法规则编号，idy指的是原点所在的位置,a为展望符
        self.table = {}  # LR(1)预测分析表
        self.tree = None  # 语法分析树

    def syntax_init(self, json_path='./help/syntax.json'):
        self.read_syntax(json_path)
        self.get_first()
        self.get_item_collection()
        self.get_table()
        self.tree = SyntaxNode(self.start_symbol)

    def read_syntax(self, json_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            js_dic = json.load(f)
            self.start_symbol = js_dic['start_symbol']
            self.empty_str = js_dic['empty_string']
            self.terminals = js_dic['terminals'].split()
            self.non_terminals = js_dic['non_terminals'].split()
            for non_terminal, values in js_dic['rules'].items():
                for value in values:
                    self.rules.append((non_terminal, value.split()))

    def get_first(self):
        """获得文法中所有符号的first集."""
        self.first = {terminal: [terminal] for terminal in self.terminals}  # 终结符的First集为自身
        for non_term in self.non_terminals:
            self.first[non_term] = []
        flag = True  # 迭代更新标志，用于判断是否仍需要一轮迭代
        while flag:
            flag = False
            for non_term, symbols in self.rules:  # 遍历每一个产生式
                if symbols == [self.empty_str]:
                    if self.empty_str not in self.first[non_term]:  # 存在未加入到First集中的空串，将其加入到First集合
                        self.first[non_term].append(self.empty_str)
                        flag = True
                    continue
                for symbol in symbols:  # 遍历非空产生式右部的每一个符号
                    for item in self.first[symbol]:  # 如果是空串，则说明需要处理下一个符号，同时不添加空串到First集中
                        if item != self.empty_str and item not in self.first[non_term]:
                            self.first[non_term].append(item)
                            flag = True
                    if self.empty_str in self.first[symbol]:  # 右部符号First集含有空串，分析下个符号或将空串加入
                        continue
                    else:  # 右部符号First集不含有空串，说明该产生式分析结束
                        break
                if self.empty_str in self.first[symbols[-1]] and self.empty_str not in self.first[non_term]:
                    self.first[non_term].append(self.empty_str)  # 若产生式最终可以推导出空串，则将空串加入到First集
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
                if self.empty_str not in self.first[symbol]:
                    break
            if self.empty_str in self.first[symbols[-1]] and self.empty_str not in res:
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

    def get_closure(self, item_lst: list) -> list:  # LR(1)文法项目集闭包
        res = item_lst.copy()
        for item in res:  # 遍历项目集中的每一个项目，（idx,idy,terminal）
            non_term, symbol_lst = self.rules[item[0]]  # non_term为非终结符，symbol_lst为右侧文法符号
            if item[1] < len(symbol_lst) and symbol_lst[item[1]] not in self.terminals:  # 点号在最后位置，为规约状态；点号后面为终结符
                symbol = symbol_lst[item[1]]  # 点号后的文法符号
                for idy, rule in enumerate(self.rules):
                    if rule[0] == symbol:  # 获得该文法符号的产生式
                        str_first = self.get_str_first(symbol_lst[item[1] + 1:] + [item[2]])
                        for first in str_first:
                            project = (idy, 0, first)  # 得到一个项目
                            if project not in res:
                                res.append(project)
        return res

    def goto(self, item_lst: list, symbol: str):  # LR(1)文法的GoTo函数
        res = []
        for item in item_lst:  # 遍历项目集中的每一项
            non_term, symbol_lst = self.rules[item[0]]  # non_term为非终结符，symbol_lst为右侧文法符号
            if item[1] != len(symbol_lst) and symbol == symbol_lst[item[1]]:
                res.append((item[0], item[1] + 1, item[2]))  # 将后继项目加入到goto集合中
        return self.get_closure(res)

    def get_item_collection(self):  # LR(1)文法的项集族
        self.item_collection.append(self.get_closure([(0, 0, '$')]))  # 加入初始的项目集闭包
        for idx, item_set in enumerate(self.item_collection):  # 遍历项集族中的每一个项目集
            self.table[idx] = {}
            for symbol in self.non_terminals + self.terminals:  # 对于每一个文法符号
                goto_set = self.goto(item_set, symbol)
                if goto_set:
                    if goto_set not in self.item_collection:
                        index = len(self.item_collection)
                        self.item_collection.append(goto_set)
                    else:
                        index = self.item_collection.index(goto_set)
                    self.table[idx][symbol] = index

    def get_table(self):
        goto_tbl = copy.deepcopy(self.table)
        for idx, item_set in enumerate(self.item_collection):  # 遍历每一个项目集
            for item in item_set:  # 遍历每一个项目
                non_term, symbol_lst = self.rules[item[0]]  # non_term为非终结符，symbol_lst为右侧文法符号
                # info = ('\t' + str(self.table[idx][item[2]])) if item[2] in self.table[idx] else ''
                info = ''
                if item[1] == len(symbol_lst) and non_term == self.start_symbol and item[2] == '$':
                    self.table[idx][item[2]] = 'acc'  # 成功接收
                elif symbol_lst[0] == self.empty_str:
                    self.table[idx][item[2]] = 'r ' + str(item[0]) + info
                elif item[1] == len(symbol_lst) and non_term != self.start_symbol:
                    self.table[idx][item[2]] = 'r ' + str(item[0]) + info  # 点号在最后一个符号后面，为规约符号
                elif symbol_lst[item[1]] in self.terminals:
                    self.table[idx][symbol_lst[item[1]]] = 's ' + str(goto_tbl[idx][symbol_lst[item[1]]]) + info

    def syntax_run(self, tokens: list, nums_attr: list):  # LR(1)文法运行语法分析
        def set_children():  # 由于自底向上分析只能获得父节点，因此需要再次处理，设置子节点
            for node in all_nodes:
                if node.parent is not None:
                    node.parent.add_child(node)

        sep, syntax_lst, states, tokens, nodes, all_nodes, syntax_err = ' ', [], [0], tokens + ['$'], ['$'], [], []
        nums_attr.append('$')
        while True:
            top_token, top_state, top_num_attr = tokens[0], states[0], nums_attr[0]
            if top_token not in self.table[top_state]:
                flag = True
                for idx, state in enumerate(states):  # 从符号栈自栈顶向下扫描，找到第一个可以跳转的符号以及对应的非终结符A的GOTO目标
                    for non_term in self.non_terminals:
                        if non_term in self.table[state]:
                            top_state = self.table[state][non_term]
                            for idy, token in enumerate(tokens):  # 忽略输入token，直到找到一个合法的可以跟在A后的token
                                if token in self.table[top_state]:
                                    symbols = [nodes[count].symbol for count in range(idx)]
                                    symbols.reverse()
                                    symbols.extend(tokens[:idy])
                                    syntax_err.append(
                                        (top_num_attr[0], top_token + ' : ' + str(top_state), '移入' + sep.join(
                                            tokens[:idy]) + '  规约' + non_term + ' -> ' + sep.join(symbols)))
                                    # 移入操作
                                    for item, num_attr in zip(tokens[:idy], nums_attr[:idy]):
                                        syntax_node = SyntaxNode(item, line_num=num_attr[0], attribute=num_attr[1])
                                        all_nodes.append(syntax_node)
                                        nodes.insert(0, syntax_node)
                                    syntax_lst.append((sep.join(list(map(str, states))), sep.join(tokens),
                                                       '错误恢复：移入' + sep.join(tokens[:idy])))
                                    # 规约操作
                                    parent_node = SyntaxNode(non_term)
                                    for syntax_node in nodes[:len(symbols)]:
                                        syntax_node.set_parent(parent_node)
                                    all_nodes.append(parent_node)
                                    syntax_lst.append((sep.join(list(map(str, states))), sep.join(tokens),
                                                       '错误恢复：规约：' + non_term + ' -> ' + sep.join(symbols)))

                                    # 删除栈顶符号，保留state, 并将goto(s, A)压入栈；忽略输入符号，保留token
                                    states, nodes = [top_state] + states[idx:], [parent_node] + nodes[len(symbols):]
                                    nums_attr, tokens, flag = nums_attr[idy:], tokens[idy:], False
                                    break
                        if not flag:  # 找到则跳出循环
                            break
                    if not flag:  # 找到则跳出循环
                        break
            else:
                op = self.table[top_state][top_token].split()
                if op[0] == 'acc':
                    syntax_lst.append((sep.join(list(map(str, states))), sep.join(tokens), '成功：' + self.start_symbol))
                    all_nodes.append(self.tree)
                    nodes[0].set_parent(self.tree)
                    set_children()
                    return syntax_lst, syntax_err
                elif op[0] == 's':  # 移入
                    syntax_lst.append((sep.join(list(map(str, states))), sep.join(tokens), '移入：' + top_token))
                    states.insert(0, int(op[1]))
                    syntax_node = SyntaxNode(top_token, line_num=top_num_attr[0], attribute=top_num_attr[1])
                    all_nodes.append(syntax_node)
                    nodes.insert(0, syntax_node)
                    tokens.pop(0)
                    nums_attr.pop(0)
                elif op[0] == 'r':  # 规约
                    non_term, symbols = self.rules[int(op[1])]
                    syntax_lst.append((sep.join(list(map(str, states))), sep.join(tokens),
                                       '规约：' + non_term + ' -> ' + sep.join(symbols)))
                    if symbols[0] == self.empty_str:  # 空产生式，特殊处理
                        null_node = SyntaxNode(self.empty_str)
                        all_nodes.append(null_node)
                        nodes.insert(0, null_node)
                    parent_node = SyntaxNode(non_term)
                    all_nodes.append(parent_node)
                    for syntax_node in nodes[:len(symbols)]:
                        syntax_node.set_parent(parent_node)
                    nodes = nodes[len(symbols):]
                    nodes.insert(0, parent_node)
                    states = states[len(symbols) if symbols[0] != self.empty_str else 0:]
                    states.insert(0, self.table[states[0]][non_term])

    def get_merged_table(self) -> dict:  # 合并同一个项目集中的相同项目的不同展望符
        merged_res = {idx: {(item[0], item[1]): [] for item in items} for idx, items in enumerate(self.item_collection)}
        for idx, items in enumerate(self.item_collection):
            for item in items:
                merged_res[idx][(item[0], item[1])].append(item[2])
        return merged_res


class SyntaxNode:

    def __init__(self, symbol, children=None, line_num=0, attribute=''):
        self.symbol = symbol  # 当前节点的文法符号
        self.children = [] if children is None else children  # 当前文法符号产生式的右部
        self.parent = None  # 当前符号的父节点
        self.line_num = line_num
        self.attribute = attribute  # 词法属性值

    def add_child(self, child):
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    def __str__(self):
        info = self.symbol
        if self.attribute and self.attribute != '_':
            info += ' :' + self.attribute
        if self.line_num:
            info += ' (' + str(self.line_num) + ')'
        return info
