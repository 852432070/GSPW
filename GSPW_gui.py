from data_widget import *

import threading
import time

from data_generator import PRINT_TERMINAL, PRINT_GUI, SAVE_FILE, SEND_TENSOR, commu, DataGenerator, state_lock

from qt_material import apply_stylesheet



app = QApplication(sys.argv)
data_app = DataApp()
data_app.show()
generator = DataGenerator()

apply_stylesheet(app, theme='dark_teal.xml')

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

def data_log_end():
    data_app.confirm_button.setEnabled(True)

commu.signal_send_list.connect(data_app.update_data)
commu.signal_log_end.connect(data_log_end)
data_app.confirm_button.clicked.connect(comfirm_save_data)

host = "0.0.0.0"  
port = 8524  

generator.host = host
generator.port = port
generator.flag = PRINT_GUI

udp_thread = threading.Thread(target=generator.receive_udp_data)
udp_thread.start()

logging_thread = threading.Thread(target=generator.store_data)
logging_thread.start()
# udp_thread.join()
# logging_thread.join()

sys.exit(app.exec_())