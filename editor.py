from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os


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
