from PyQt5.QtWidgets import QMenuBar, QApplication, QMenu, QMainWindow, QAction, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import QUrl
import os
import sys

width = 960  # 窗口宽度
height = 540  # 窗口高度


class Editor(QWebEngineView):
    def __init__(self, par):
        super().__init__(par)
        self.editor_flag = []
        self.text = None  # 输入的文本

        self.editor_index = os.getcwd() + '/index.html'
        self.load(QUrl.fromLocalFile(self.editor_index))

    def __callback(self, res):
        self.text = res

    def get_value(self):
        self.page().runJavaScript("monaco.editor.getModels()[0].getValue()", self.__callback)
        return self.text

    def set_value(self, data):
        # import base64
        # data = base64.b64encode(data.encode())
        # data = data.decode()
        js_str = 'monaco.editor.getModels()[0].setValue(' + data + ')'
        print(js_str)
        self.page().runJavaScript(js_str)

    def change_language(self, lan):
        self.page().runJavaScript("monaco.editor.setModelLanguage(monaco.editor.getModels()[0],'{}')".format(lan))


class MainWindow(QMainWindow):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFixedSize(width, height)
        self.setWindowTitle('编译器')
        self.setWindowIcon(QIcon('./img/system.ico'))
        self.setCentralWidget(editor)

        self.menu_bar = QMenuBar(self)  # 菜单栏
        self.file_menu = QMenu('文件', self.menu_bar)
        self.open_file_action = QAction('打开文件', shortcut=QKeySequence.Open, triggered=self.open_file)
        self.lexical_menu = QMenu('词法分析', self.menu_bar)
        self.syntax_menu = QMenu('语法分析', self.menu_bar)
        self.semantic_menu = QMenu('语义分析', self.menu_bar)
        self.about_menu = QMenu('关于', self.menu_bar)
        self.init_menu_bar()

    def init_menu_bar(self):
        self.menu_bar.setGeometry(0, 0, width, 26)
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.lexical_menu)
        self.menu_bar.addMenu(self.syntax_menu)
        self.menu_bar.addMenu(self.semantic_menu)
        self.menu_bar.addMenu(self.about_menu)
        self.file_menu.addAction(self.open_file_action)

    def open_file(self):
        file_path = QFileDialog.getOpenFileName(self, '', os.getcwd() + '/input', 'C(*.c);;Txt(*.txt)')[0]
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                self.editor.set_value(text)


def main():
    app = QApplication(sys.argv)
    window = MainWindow(Editor(None))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
