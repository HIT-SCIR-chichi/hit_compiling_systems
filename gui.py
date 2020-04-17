#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMenuBar, QApplication, QMenu, QMainWindow, QAction, QFileDialog, QDialog, QLabel, \
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView, QTreeWidgetItem, QStyleFactory, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QBrush
from PyQt5.QtCore import QUrl, Qt
from lexical import Lexical
from syntax import Syntax
from ui import syntax_grammar, syntax_res
import sys
import os

width = 960  # 窗口宽度
height = 540  # 窗口高度
bar_height = 26  # 菜单栏和状态栏高度


class Editor(QWebEngineView):
    def __init__(self, par):
        super().__init__(par)
        self.text = ''  # 输入的文本
        self.editor_flag = []

        self.editor_index = os.getcwd() + '/help/index.html'
        self.load(QUrl.fromLocalFile(self.editor_index))

    def _callback(self, res):
        self.text = res

    def get_text(self, callback=_callback):
        self.page().runJavaScript("monaco.editor.getModels()[0].getValue()", callback)

    def set_text(self, data):
        import base64
        self.text = data
        data = base64.b64encode(data.encode()).decode()  # 编解码代码文件
        js_str = "monaco.editor.getModels()[0].setValue(Base64.decode('{}'))".format(data)
        self.page().runJavaScript(js_str)

    def change_language(self, lan):
        self.page().runJavaScript("monaco.editor.setModelLanguage(monaco.editor.getModels()[0],'{}')".format(lan))


class MainWindow(QMainWindow):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFixedSize(width, height)
        self.setWindowTitle('编译器@zjr')
        self.setWindowIcon(QIcon('help/system.ico'))
        self.setCentralWidget(editor)

        self.file_path = None  # 打开的文件的目录

        self.menu_bar = QMenuBar(self)  # 菜单栏

        self.file_menu = QMenu('文件', self.menu_bar)
        self.open_file_action = QAction('打开', shortcut=QKeySequence.Open, triggered=self.open_file)
        self.save_file_action = QAction('保存', shortcut=QKeySequence.Save, triggered=self.save_file)
        self.save_as_action = QAction('另存为', shortcut='ctrl+shift+s', triggered=self.save_as_file)

        self.lexical_menu = QMenu('词法分析', self.menu_bar)
        self.lexical_run_action = QAction('运行', shortcut='ctrl+f1', triggered=self.lexical_run)
        self.dfa_action = QAction('DFA转换表', triggered=self.dfa)
        self.nfa_action = QAction('NFA转换表', triggered=self.nfa)

        self.syntax_menu = QMenu('语法分析', self.menu_bar)
        self.syntax_run_action = QAction('运行', shortcut='ctrl+f2', triggered=self.syntax_run)
        self.grammar_action = QAction('语法信息', triggered=self.grammar)

        self.semantic_menu = QMenu('语义分析', self.menu_bar)
        self.about_menu = QMenu('关于', self.menu_bar)
        self.more_action = QAction('待实现', triggered=self.more)
        self.init_menu_bar()

        self.lexical_window = None
        self.dfa_window = None
        self.nfa_window = None
        self.syntax_window = None
        self.grammar_window = None

    def init_menu_bar(self):
        self.menu_bar.setGeometry(0, 0, width, bar_height)
        for menu_bar in [self.file_menu, self.lexical_menu, self.syntax_menu, self.semantic_menu, self.about_menu]:
            self.menu_bar.addMenu(menu_bar)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_as_action)

        self.lexical_menu.addAction(self.lexical_run_action)
        self.lexical_menu.addAction(self.dfa_action)
        self.lexical_menu.addAction(self.nfa_action)

        self.syntax_menu.addAction(self.syntax_run_action)
        self.syntax_menu.addAction(self.grammar_action)

        self.semantic_menu.addAction(self.more_action)

        self.about_menu.addAction(self.more_action)

    def open_file(self):  # 打开文件
        self.file_path = QFileDialog.getOpenFileName(self, '', os.getcwd() + '/input', 'C(*.c);;Txt(*.txt)')[0]
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.editor.set_text(f.read())

    def __save_file_callback(self, res):
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(res)
        else:
            self.save_as_file()

    def __save_as_callback(self, res):
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(res)

    def save_file(self):  # 保存文件
        self.editor.get_text(self.__save_file_callback)

    def save_as_file(self):  # 文件另存为
        self.file_path = QFileDialog.getSaveFileName(self, '', os.getcwd() + '/input', 'C(*.c);;Txt(*.txt)')[0]
        self.editor.get_text(self.__save_as_callback)

    def __lexical_run_callback(self, res):
        lexical = Lexical()
        lexical.get_dfa('./help/dfa.json')
        res = lexical.lexical_run(str(res).replace('\r\n', '\n'))  # 词法分析的token序列，要将window换行符'\r\n'转换
        self.lexical_window = LexicalWindow(res)
        self.lexical_window.show()

    def lexical_run(self):  # 运行词法分析
        self.editor.get_text(self.__lexical_run_callback)

    def dfa(self):  # dfa转换表
        lexical = Lexical()
        lexical.get_dfa('./help/dfa.json')
        self.dfa_window = DFAWindow(lexical.get_dfa_table())
        self.dfa_window.show()

    def nfa(self):  # nfa转换表
        path = QFileDialog.getOpenFileName(self, '', os.getcwd() + '/help/nfa.json', 'Json(*.json)')[0]
        if path:
            lexical = Lexical()
            lexical.get_nfa(path)
            self.nfa_window = NFAWindow(lexical.nfa, lexical.nfa2dfa())
            self.nfa_window.show()

    def __syntax_run_callback(self, res):
        lexical = Lexical()
        lexical.get_dfa('./help/dfa.json')  # 读取DFA转换表
        lexical_res = lexical.lexical_run(str(res).replace('\r\n', '\n'))  # 得到词法分析的token序列
        tokens, line_nums = [], []
        if not lexical_res[0] and not lexical_res[1]:
            QMessageBox.warning(self, '输入无效', '请输入有效程序文本')
            return
        for idx in range(len(lexical_res[0])):  # item[1]为种别码,item[3]为行号
            item = lexical_res[0][idx]
            if 'comment' not in item[1]:
                tokens.append(item[1])
                line_nums.append(item[3])
        syntax = Syntax()
        syntax.syntax_init('./help/syntax.json')
        syntax_lst = syntax.syntax_run(tokens, line_nums)

        self.syntax_window = QDialog()
        ui = syntax_res.Ui_Dialog()
        ui.setupUi(self.syntax_window)
        self.syntax_window.setWindowIcon(QIcon('./help/system.ico'))
        self.syntax_window.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
        set_syntax_win(ui, syntax, syntax_lst)
        self.syntax_window.show()

    def syntax_run(self):  # 运行语法分析
        self.editor.get_text(self.__syntax_run_callback)

    def grammar(self):  # 展示语法分析中可以计算的集合和表
        syntax = Syntax()
        syntax.syntax_init('./help/syntax.json')

        self.grammar_window = QDialog()
        ui = syntax_grammar.Ui_dialog()
        ui.setupUi(self.grammar_window)
        set_grammar_tbl(ui, syntax)
        self.grammar_window.show()

    def more(self):  # 待实现
        pass


class LexicalWindow(QDialog):
    def __init__(self, res):
        super().__init__()
        self.__res_table = QTableWidget(len(res[0]) if len(res[0]) > 0 else 1, 3, self)  # 词法分析表
        self.__err_table = QTableWidget(len(res[1]) if len(res[1]) > 0 else 1, 3, self)  # DFA转换表
        self.__res_label = QLabel('词法分析结果', self)
        self.__err_label = QLabel('错误信息表', self)

        self.__set_ui()
        self.__set_table(res)

    def __set_ui(self):
        self.setWindowTitle('词法分析')
        self.setWindowIcon(QIcon('./help/system.ico'))
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        for idx, label in enumerate([self.__res_label, self.__err_label]):
            label.setGeometry(idx * width / 2, 0, width / 2, bar_height * 2)
            label.setFont(QFont('roman times', 15))
            label.setAlignment(Qt.AlignCenter)

    def __set_table(self, res):
        self.__res_table.setGeometry(0, bar_height * 2, width / 2, height - bar_height * 2)
        self.__err_table.setGeometry(width / 2, bar_height * 2, width / 2, height - bar_height * 2)
        self.__res_table.setHorizontalHeaderLabels(['行号', '字符串', 'Token'])
        self.__err_table.setHorizontalHeaderLabels(['行号', '字符串', '错误'])
        for idx, table in enumerate((self.__res_table, self.__err_table)):
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.verticalHeader().setVisible(False)
            for idy in res[idx]:
                item = res[idx][idy]
                table.setItem(idy, 0, QTableWidgetItem(str(item[3])))
                table.setItem(idy, 1, QTableWidgetItem(item[0]))
                table.setItem(idy, 2, QTableWidgetItem('<' + str(item[1]) + ' , ' + item[2] + '>'))
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__err_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)


class DFAWindow(QDialog):
    def __init__(self, dfa_table):
        super().__init__()
        self.__dfa_table = QTableWidget(dfa_table[0], len(dfa_table[1]), self)  # DFA转换表
        self.__err_table = QTableWidget(len(dfa_table[4]), 2, self)  # 错误信息对照表

        self.__dfa_label = QLabel('DFA转换表', self)
        self.__err_label = QLabel('错误信息表', self)

        self.__set_ui()
        self.__set_dfa_table(dfa_table[0], dfa_table[1], dfa_table[2], dfa_table[3])
        self.__set_err_table(dfa_table[4])

    def __set_ui(self):
        self.setWindowTitle('DFA')
        self.setWindowIcon(QIcon('./help/system.ico'))
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        for idx, label in enumerate([self.__dfa_label, self.__err_label]):
            label.setGeometry(idx * width * 2 / 3, 0, width * (1 if idx else 2) / 3, bar_height * 2)
            label.setFont(QFont('roman times', 15))
            label.setAlignment(Qt.AlignCenter)

    def __set_dfa_table(self, state_num, all_chars, dfa, end_state):
        show_chars = []  # 将不可打印字符转换
        for char in all_chars:
            if char == '\n':
                show_chars.append('换行符')
            elif char == '\t ':
                show_chars.append('制表符空格')
            elif char == '\0':
                show_chars.append('结束符')
            else:
                show_chars.append(char)
        self.__dfa_table.setGeometry(0, bar_height * 2, width * 2 / 3, height - bar_height * 2)
        self.__dfa_table.setHorizontalHeaderLabels(show_chars)
        self.__dfa_table.setVerticalHeaderLabels([str(idx) for idx in range(0, state_num)])  # 注意str不可少
        self.__dfa_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__dfa_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for idx in range(0, state_num):
            if idx in end_state:
                self.__dfa_table.verticalHeaderItem(idx).setForeground(QColor(0, 0, 255))
            for idy, char in enumerate(all_chars):
                if idx in dfa and char in dfa[idx]:
                    item = QTableWidgetItem(str(dfa[idx][char]))
                    if dfa[idx][char] < 0:
                        item.setForeground(QBrush(QColor(255, 0, 0)))
                    self.__dfa_table.setItem(idx, idy, item)  # 注意item值转换为str

    def __set_err_table(self, err_info):
        self.__err_table.setGeometry(width * 2 / 3, bar_height * 2, width / 3, height - bar_height * 2)
        self.__err_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__err_table.verticalHeader().setVisible(False)
        self.__err_table.setHorizontalHeaderLabels(['错误号', '错误信息'])
        self.__err_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.__err_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for idx in range(0, len(err_info)):
            self.__err_table.setItem(idx, 0, QTableWidgetItem(str(-idx - 1)))
            self.__err_table.setItem(idx, 1, QTableWidgetItem(err_info[-idx - 1]))


class NFAWindow(QDialog):
    def __init__(self, nfa, dfa):
        super().__init__()
        self.__nfa_table = QTableWidget(nfa['state_number'], len(nfa['char']) + 1, self)  # NFA转换表
        self.__dfa_table = QTableWidget(len(dfa['states']), len(dfa['char']), self)  # DFA转换表
        self.__info_table = QTableWidget(len(dfa['states']), 2, self)  # 变换前后状态信息对照表

        self.__nfa_label = QLabel('NFA转换表', self)
        self.__dfa_label = QLabel('DFA转换表', self)
        self.__info_label = QLabel('状态信息表', self)

        self.__set_ui()
        self.__set_nfa_table(nfa['state_number'], nfa['end_state'], nfa['char'], nfa['nfa_table'])
        self.__set_dfa_table(dfa['states'], dfa['end_states'], dfa['char'], dfa['dfa_table'])
        self.__set_info_table(dfa['states'], dfa['end_states'])

    def __set_ui(self):
        self.setWindowTitle('NFA->DFA')
        self.setWindowIcon(QIcon('./help/system.ico'))
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        for idx, label in enumerate([self.__nfa_label, self.__dfa_label, self.__info_label]):
            label.setGeometry(idx * width / 3, 0, width / 3, bar_height * 2)
            label.setFont(QFont('roman times', 15))
            label.setAlignment(Qt.AlignCenter)

    def __set_nfa_table(self, state_num, end_state, chars, table):
        self.__nfa_table.setGeometry(0, bar_height * 2, width / 3, height - bar_height * 2)
        self.__nfa_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__nfa_table.setVerticalHeaderLabels([str(idx) for idx in range(0, state_num)])

        show_chars = [char for char in chars]
        show_chars.append('空串')
        self.__nfa_table.setHorizontalHeaderLabels(show_chars)
        for x in range(0, state_num):
            if x in end_state:
                self.__nfa_table.verticalHeaderItem(x).setForeground(QBrush(QColor(0, 0, 255)))
            for y, char in enumerate(chars + ['\0']):
                if x in table and char in table[x]:
                    self.__nfa_table.setItem(x, y, QTableWidgetItem(' '.join('%s' % d for d in table[x][char])))

    def __set_dfa_table(self, states, end_states, chars, table):
        self.__dfa_table.setGeometry(width / 3, bar_height * 2, width / 3, height - bar_height * 2)
        self.__dfa_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__dfa_table.setVerticalHeaderLabels([str(idx) for idx in range(0, len(states))])
        self.__dfa_table.setHorizontalHeaderLabels(chars)
        for x in range(0, len(states)):
            if x in end_states:
                self.__dfa_table.verticalHeaderItem(x).setForeground(QBrush(QColor(0, 0, 255)))
            for y, char in enumerate(chars):
                if x in table and char in table[x]:
                    self.__dfa_table.setItem(x, y, QTableWidgetItem(str(table[x][char])))

    def __set_info_table(self, states, end_states):
        self.__info_table.setGeometry(width * 2 / 3, bar_height * 2, width / 3, height - bar_height * 2)
        self.__info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__info_table.verticalHeader().setVisible(False)
        self.__info_table.setHorizontalHeaderLabels(['现DFA状态', '原NFA状态'])
        self.__info_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for idx in range(len(states)):
            self.__info_table.setItem(idx, 0, QTableWidgetItem(str(idx)))
            if idx in end_states:
                self.__info_table.item(idx, 0).setForeground(QBrush(QColor(0, 0, 255)))
            self.__info_table.setItem(idx, 1, QTableWidgetItem(' '.join('%s' % d for d in states[idx])))


def set_grammar_tbl(ui: syntax_grammar.Ui_dialog, syntax: Syntax):
    ui.grammar_table.setRowCount(len(syntax.rules))  # 设置文法展示表和Select集的表
    ui.grammar_table.setVerticalHeaderLabels([str(idx) for idx in range(len(syntax.rules))])
    for idx, rule in enumerate(syntax.rules):
        ui.grammar_table.setItem(idx, 0, QTableWidgetItem(rule[0] + '->' + ' '.join(rule[1])))  # 产生式

    ui.lst_table.setRowCount(len(syntax.non_terminals))  # 设置First集和Follow集的展示表
    for idx, non_term in enumerate(syntax.non_terminals):
        ui.lst_table.setItem(idx, 0, QTableWidgetItem(non_term))
        ui.lst_table.setItem(idx, 1, QTableWidgetItem(' '.join(syntax.first[non_term])))
        ui.lst_table.setItem(idx, 2, QTableWidgetItem(' '.join(syntax.follow[non_term])))

    symbols = syntax.terminals + syntax.non_terminals
    symbols.remove(syntax.start_symbol)
    ui.table.setColumnCount(len(symbols))  # 设置分析表
    ui.table.setHorizontalHeaderLabels(symbols)
    ui.table.setRowCount(len(syntax.table))
    ui.table.setVerticalHeaderLabels(map(str, range(len(syntax.table))))
    for idx, state in enumerate(syntax.table):
        for idy, symbol in enumerate(symbols):
            if symbol in syntax.table[state]:
                item = QTableWidgetItem(str(syntax.table[state][symbol]))
                if syntax.table[state][symbol] == 'acc':
                    item.setForeground(QBrush(QColor(0, 0, 255)))
                ui.table.setItem(idx, idy, item)

    count, item_num, merged_res = 0, 0, syntax.get_merged_table()  # item_nums用于项目总数目
    for idx in range(len(merged_res)):
        item_num += len(merged_res[idx])
    ui.item_tbl.setRowCount(item_num)
    ui.item_tbl.setVerticalHeaderLabels(map(str, range(item_num)))
    for idx in range(len(merged_res)):
        item_collection = merged_res[idx]
        for idy, ((production, dot_pos), look_ahead) in enumerate(item_collection.items()):
            non_term, symbols = syntax.rules[production]
            copy_symbols = symbols.copy()
            copy_symbols.insert(dot_pos, '·')  # 项目
            ui.item_tbl.setItem(count, 0, QTableWidgetItem(str(idx)))
            ui.item_tbl.setItem(count, 1, QTableWidgetItem(non_term + ' -> ' + ' '.join(copy_symbols)))
            ui.item_tbl.setItem(count, 2, QTableWidgetItem(' '.join(look_ahead)))
            count += 1

    for table in [ui.grammar_table, ui.item_tbl, ui.lst_table, ui.table]:
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


def set_syntax_win(ui: syntax_res.Ui_Dialog, syntax: Syntax, syntax_lst: list):
    ui.syntax_table.setRowCount(len(syntax_lst))  # 设置语法分析过程表
    ui.syntax_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    for idx, value in enumerate(syntax_lst):
        for idy in range(3):
            item = QTableWidgetItem(value[idy])
            item.setTextAlignment(Qt.AlignRight if idy != 2 else Qt.AlignCenter)
            ui.syntax_table.setItem(idx, idy, item)

    tree_stack, item_stack = [syntax.tree], [QTreeWidgetItem(ui.syntax_tree)]
    while tree_stack:
        tree_node, item_node = tree_stack.pop(0), item_stack.pop(0)
        item_node.setText(0, tree_node.__str__())
        tree_stack = tree_node.children + tree_stack
        item_stack = [QTreeWidgetItem(item_node) for child in tree_node.children] + item_stack
    ui.syntax_tree.expandAll()
    ui.syntax_tree.setStyle(QStyleFactory.create("windows"))  # 显示树上的虚线
    ui.syntax_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Editor(None))
    window.show()

    sys.exit(app.exec_())
