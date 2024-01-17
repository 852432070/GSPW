from data_widget import *

import threading
import time

from data_generator import PRINT_TERMINAL, PRINT_GUI, SAVE_FILE, SEND_TENSOR, DataGenerator, state_lock
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from classifier_widget import ClassifierApp
import classifier
from classifier import Classifier

from qt_material import apply_stylesheet




app = QApplication(sys.argv)
data_app = DataApp()
generator = DataGenerator()
classifier_app = ClassifierApp()
cf = Classifier("./model/model.onnx")


apply_stylesheet(app, theme='dark_teal.xml')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tab = QTabWidget()
        self.setCentralWidget(self.tab)

        self.tab.addTab(data_app, "数据追踪与采集")

        self.tab.addTab(classifier_app, "人体行为识别")
        
        # 设置主窗口的标题
        self.setWindowTitle("腕上感知平台")

main_window = MainWindow()
main_window.show()

def comfirm_save_data():
    if not all(field.text().isdigit() and int(field.text()) > 0 for field in [data_app.duration_input, data_app.user_input, data_app.activity_input]):  
        print("Please check your input data")  
        return  
    with state_lock:
        generator.flag |= SAVE_FILE
        generator.max_runtime_seconds = int(data_app.duration_input.text())
        generator.user_id = int(data_app.user_input.text())
        generator.activity_id = int(data_app.activity_input.text())
        print(f"save data from user {generator.user_id} activity {generator.activity_id} for {generator.max_runtime_seconds} seconds")
        generator.start_time = time.time()
        data_app.duration_input.clear()
        data_app.user_input.clear()
        data_app.activity_input.clear()
        data_app.confirm_button.setEnabled(False)

def confirm_classify():
    if generator.flag & SAVE_FILE:
        print("In logging mode")
        return
    with state_lock:
        generator.flag |= SEND_TENSOR
        classifier_app.confirm_button.setEnabled(False)
        classifier_app.stop_button.setEnabled(True)

def stop_classify():
    with state_lock:
        generator.flag &= ~SEND_TENSOR
        classifier_app.confirm_button.setEnabled(True)
        classifier_app.stop_button.setEnabled(False)
    

def data_log_end():
    data_app.confirm_button.setEnabled(True)

generator.signal_send_list.connect(data_app.update_data)
generator.signal_log_end.connect(data_log_end)
data_app.confirm_button.clicked.connect(comfirm_save_data)
classifier_app.signal_confirm.connect(confirm_classify)
classifier_app.stop_button.clicked.connect(stop_classify)
cf.signal_predict.connect(classifier_app.update_category)




host = "0.0.0.0"  
port = 8524  

generator.host = host
generator.port = port
generator.flag = PRINT_GUI



udp_thread = threading.Thread(target=generator.receive_udp_data)
udp_thread.start()

logging_thread = threading.Thread(target=generator.store_data)
logging_thread.start()

classify_thread = threading.Thread(target=classifier.classification_thread, args=(cf,))
classify_thread.start()
# udp_thread.join()
# logging_thread.join()
sys.exit(app.exec_())
