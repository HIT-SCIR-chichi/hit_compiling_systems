#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMenuBar, QApplication, QMenu, QMainWindow, QAction, QFileDialog, QDialog, QLabel, \
    QTableWidget, QAbstractItemView, QTableWidgetItem, QHeaderView
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtCore import QUrl, Qt
from lexical import Lexical
import sys
import os

width = 960  # 窗口宽度
height = 540  # 窗口高度
bar_height = 26  # 菜单栏和状态栏高度


# todo 添加nfa与dfa转换
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
        self.open_file_action = QAction('打开文件', shortcut=QKeySequence.Open, triggered=self.open_file)
        self.save_file_action = QAction('保存文件', shortcut=QKeySequence.Save, triggered=self.save_file)
        self.save_as_action = QAction('另存为', shortcut='ctrl+shift+s', triggered=self.save_as_file)

        self.lexical_menu = QMenu('词法分析', self.menu_bar)
        self.lexical_run_action = QAction('运行词法分析', shortcut='ctrl+f1', triggered=self.lexical_run)
        self.lexical_rules_action = QAction('词法规则', triggered=self.lexical_rules)
        self.dfa_action = QAction('DFA转换表', triggered=self.dfa)
        self.nfa_action = QAction('NFA转换表', triggered=self.nfa)

        self.more_action = QAction('待实现', triggered=self.more)
        self.syntax_menu = QMenu('语法分析', self.menu_bar)

        self.semantic_menu = QMenu('语义分析', self.menu_bar)
        self.about_menu = QMenu('关于', self.menu_bar)
        self.init_menu_bar()

        self.lexical_window = None

    def init_menu_bar(self):
        self.menu_bar.setGeometry(0, 0, width, bar_height)

        self.menu_bar.addMenu(self.file_menu)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_as_action)

        self.menu_bar.addMenu(self.lexical_menu)
        self.lexical_menu.addAction(self.lexical_run_action)
        self.lexical_menu.addAction(self.lexical_rules_action)
        self.lexical_menu.addAction(self.dfa_action)
        self.lexical_menu.addAction(self.nfa_action)

        self.menu_bar.addMenu(self.syntax_menu)
        self.syntax_menu.addAction(self.more_action)

        self.menu_bar.addMenu(self.semantic_menu)
        self.semantic_menu.addAction(self.more_action)

        self.menu_bar.addMenu(self.about_menu)
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
        lexical.get_dfa('./input/dfa.json')
        dfa_table = lexical.get_dfa_table()
        lexical_res = lexical.lexical_run(res)  # 词法分析的token序列
        self.lexical_window = LexicalWindow(lexical_res, dfa_table)
        self.lexical_window.show()

    def lexical_run(self):  # 运行词法分析
        self.editor.get_text(self.__lexical_run_callback)

    def lexical_rules(self):  # 词法规则
        pass

    def dfa(self):  # dfa转换表
        pass

    def nfa(self):  # nfa转换表
        pass

    def more(self):  # 待实现
        pass


class LexicalWindow(QDialog):
    def __init__(self, lexical_res, dfa_table):
        super().__init__()
        self.__res_table = QTableWidget(len(lexical_res) if len(lexical_res) > 0 else 1, 4, self)  # 词法分析表
        self.__dfa_table = QTableWidget(dfa_table[0], len(dfa_table[1]), self)  # DFA转换表
        self.__result_label = QLabel('词法分析结果', self)
        self.__dfa_label = QLabel('DFA转换表', self)

        self.__set_ui()
        self.__set_res_table(lexical_res)
        self.__set_dfa_table(dfa_table)

    def __set_ui(self):
        self.setWindowTitle('词法分析')
        self.setWindowIcon(QIcon('./help/system.ico'))
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        self.__result_label.setGeometry(0, 0, width / 2, bar_height * 2)
        self.__result_label.setFont(QFont('roman times', 15))
        self.__result_label.setAlignment(Qt.AlignCenter)

        self.__dfa_label.setGeometry(width / 2, 0, width / 2, bar_height * 2)
        self.__dfa_label.setFont(QFont('roman times', 15))
        self.__dfa_label.setAlignment(Qt.AlignCenter)

    def __set_res_table(self, lexical_res):
        self.__res_table.setGeometry(0, bar_height * 2, width / 2, height - bar_height * 2)
        self.__res_table.setHorizontalHeaderLabels(['行号', '字符串', 'Token序列', '类型'])
        self.__res_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__res_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for idx in lexical_res:
            self.__res_table.setItem(idx, 0, QTableWidgetItem('0'))  # 行号
            self.__res_table.setItem(idx, 1, QTableWidgetItem(lexical_res[idx][1]))  # 字符串
            self.__res_table.setItem(idx, 2, QTableWidgetItem(
                '<' + lexical_res[idx][0] + ' ,' + lexical_res[idx][1] + '>'))
            self.__res_table.setItem(idx, 3, QTableWidgetItem(lexical_res[idx][0]))  # token类型

    def __set_dfa_table(self, dfa_table):
        state_num, all_char, dfa = dfa_table
        all_char = ['换行符' if char == '\n' else char for char in all_char]
        self.__dfa_table.setGeometry(width / 2, bar_height * 2, width / 2, height - bar_height * 2)
        self.__dfa_table.setHorizontalHeaderLabels(all_char)
        self.__dfa_table.setVerticalHeaderLabels([str(idx) for idx in range(0, state_num)])  # 注意str不可少
        self.__dfa_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.__dfa_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for idx in range(0, state_num):
            for idy, char in enumerate(all_char):
                if idx in dfa and char in dfa[idx]:
                    self.__dfa_table.setItem(idx, idy, QTableWidgetItem(str(dfa[idx][char])))  # 注意item值转换为str


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Editor(None))
    window.show()

    sys.exit(app.exec_())
