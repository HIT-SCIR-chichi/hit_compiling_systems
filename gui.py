#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMenuBar, QApplication, QMenu, QMainWindow, QAction, QFileDialog, QStatusBar
from PyQt5.QtGui import QIcon, QKeySequence
from lexical import Lexical
from editor import Editor
import sys
import os

width = 960  # 窗口宽度
height = 540  # 窗口高度
bar_height = 26  # 菜单栏和状态栏高度


class MainWindow(QMainWindow):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFixedSize(width, height)
        self.setWindowTitle('编译器@zjr')
        self.setWindowIcon(QIcon('./img/system.ico'))
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
        print(res)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Editor(None))
    window.show()
    sys.exit(app.exec_())
