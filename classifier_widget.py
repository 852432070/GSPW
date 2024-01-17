import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QLineEdit, QApplication, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ClassifierApp(QWidget):
    signal_confirm = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.initUI()
        

    def initUI(self):
        # 主布局
        layout = QVBoxLayout()

        # 设置行为类别数的选择界面
        self.category_selector = QSpinBox(self)
        self.category_selector.setMinimum(1)
        self.confirm_button = QPushButton('确认', self)
        self.confirm_button.clicked.connect(self.generate_bars)
        self.stop_button = QPushButton('停止', self)
        self.stop_button.setEnabled(False)


        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel('行为类别数:'))
        selector_layout.addWidget(self.category_selector)
        selector_layout.addWidget(self.confirm_button)
        selector_layout.addWidget(self.stop_button)

        layout.addLayout(selector_layout)

        # 柱状图布局
        self.bars_layout = QVBoxLayout()
        layout.addLayout(self.bars_layout)

        self.setLayout(layout)

    def generate_bars(self):
        # 清除旧的柱体
        for i in reversed(range(self.bars_layout.count())): 
            widget_to_remove = self.bars_layout.itemAt(i)
            self.bars_layout.removeItem(widget_to_remove)

        # 创建新的柱体
        for i in range(self.category_selector.value()):
            bar_layout = QHBoxLayout()
            label_edit = QLineEdit(f'类别 {i+1}')
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)  # 示例最大值
            bar_layout.addWidget(label_edit)
            bar_layout.addWidget(progress_bar)
            self.bars_layout.addLayout(bar_layout)
        
        self.signal_confirm.emit()

    def update_category(self, index):
        # 更新分类结果
        for i in range(self.bars_layout.count()):
            bar_layout = self.bars_layout.itemAt(i)
            label_edit = bar_layout.itemAt(0).widget()
            progress_bar = bar_layout.itemAt(1).widget()

            if i == index:
                progress_bar.setValue(progress_bar.value() + 1)  # 假设每次增加1
                progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
                label_edit.setFont(QFont('Arial', 15, QFont.Bold))
            else:
                progress_bar.setStyleSheet("")
                label_edit.setFont(QFont())

# 运行程序
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClassifierApp()
    ex.show()
    sys.exit(app.exec_())