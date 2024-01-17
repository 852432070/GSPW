import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator



class DataApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize data labels
        self.data_labels = [QLabel('0') for _ in range(9)]

        # Layouts
        main_layout = QVBoxLayout()
        data_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Data display module
        data_layout.addWidget(QLabel('数据追踪'))
        for i in range(3):
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(['ACC', 'GYRO', 'MAG'][i]))
            for j in range(3):
                row_layout.addWidget(self.data_labels[i * 3 + j])
            data_layout.addLayout(row_layout)

        # User input module
        self.user_input = QLineEdit()
        self.activity_input = QLineEdit()
        self.duration_input = QLineEdit()
        positive_int_validator = QIntValidator(1, 999999)
        self.user_input.setValidator(positive_int_validator)
        self.activity_input.setValidator(positive_int_validator)
        self.duration_input.setValidator(positive_int_validator)
        self.confirm_button = QPushButton('确认')
        input_layout.addWidget(QLabel('用户:'))
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(QLabel('行为种类:'))
        input_layout.addWidget(self.activity_input)
        input_layout.addWidget(QLabel('采集时间:'))
        input_layout.addWidget(self.duration_input)
        input_layout.addWidget(self.confirm_button)

        # Add modules to main layout
        main_layout.addLayout(data_layout)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('实时数据展示')

    def update_data(self, new_data):
        # Update labels with new data
        if len(new_data) == 9:
            for i, label in enumerate(self.data_labels):
                label.setText(str(new_data[i]))

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = DataApp()
#     window.show()

#     # Example of updating data
#     def generate_and_update_data():
#         new_data = [random.randint(0, 100) for _ in range(9)]
#         window.update_data(new_data)

#     # Assuming this function is called externally to update data
#     generate_and_update_data()

#     sys.exit(app.exec_())
