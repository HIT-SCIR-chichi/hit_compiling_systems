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
        self.text = ''  # 输入的文本

        self.editor_index = os.getcwd() + '/index.html'
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
        self.setWindowTitle('编译器')
        self.setWindowIcon(QIcon('./img/system.ico'))
        self.setCentralWidget(editor)

        self.file_path = None  # 打开的文件的目录

        self.menu_bar = QMenuBar(self)  # 菜单栏

        self.file_menu = QMenu('文件', self.menu_bar)
        self.open_file_action = QAction('打开文件', shortcut=QKeySequence.Open, triggered=self.open_file)
        self.save_file_action = QAction('保存文件', shortcut=QKeySequence.Save, triggered=self.save_file)
        self.save_as_action = QAction('另存为', shortcut='ctrl+shift+s', triggered=self.save_as_file)

        self.lexical_menu = QMenu('词法分析', self.menu_bar)
        self.syntax_menu = QMenu('语法分析', self.menu_bar)
        self.semantic_menu = QMenu('语义分析', self.menu_bar)
        self.about_menu = QMenu('关于', self.menu_bar)
        self.init_menu_bar()

    def init_menu_bar(self):
        self.menu_bar.setGeometry(0, 0, width, 26)

        self.menu_bar.addMenu(self.file_menu)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.save_file_action)
        self.file_menu.addAction(self.save_as_action)

        self.menu_bar.addMenu(self.lexical_menu)
        self.menu_bar.addMenu(self.syntax_menu)
        self.menu_bar.addMenu(self.semantic_menu)
        self.menu_bar.addMenu(self.about_menu)

    def open_file(self):  # 打开文件
        self.file_path = QFileDialog.getOpenFileName(self, '', os.getcwd() + '/input', 'C(*.c);;Txt(*.txt)')[0]
        if self.file_path:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                self.editor.set_text(text)

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
        print(self.file_path)
        self.editor.get_text(self.__save_as_callback)


def main():
    app = QApplication(sys.argv)
    window = MainWindow(Editor(None))
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
