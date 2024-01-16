import threading
import socket
import queue  # 用于创建FIFO队列
import numpy as np
import time
import pandas as pd
import threading


from PyQt5.QtCore import pyqtSignal, QObject
from data_widget import DataApp
class Communicate(QObject):
    signal_send_list = pyqtSignal(list)
commu = Communicate()


# 定义一个FIFO队列，用于存储UDP数据包
fifo_queue = queue.Queue(maxsize=10)
tensor_queue = queue.Queue(maxsize=10)
state_lock = threading.Lock()

TIME_YEAR = 13
TIME_MON = 14
TIME_DAY = 15
TIME_HOUR = 16
TIME_MIN = 17
TIME_SEC = 18
TIME_MSL = 19
TIME_MSH = 20
DATA_AXL = 21
DATA_AXH = 22
DATA_AYL = 23
DATA_AYH = 24
DATA_AZL = 25
DATA_AZH = 26
DATA_GXL = 27
DATA_GXH = 28
DATA_GYL = 29
DATA_GYH = 30
DATA_GZL = 31
DATA_GZH = 32
DATA_HXL = 33
DATA_HXH = 34
DATA_HYL = 35
DATA_HYH = 36
DATA_HZL = 37
DATA_HZH = 38

PRINT_TERMINAL = 0b1
PRINT_GUI = 0b10
SAVE_FILE = 0b100
SEND_TENSOR = 0b1000



window_size =171

def get_databyte(data, shift):
    return data[shift-1]

def get_time(data):
    year = get_databyte(data, TIME_YEAR)
    month = get_databyte(data, TIME_MON)
    day = get_databyte(data, TIME_DAY)
    hour = get_databyte(data, TIME_HOUR)
    min = get_databyte(data, TIME_MIN)
    sec = get_databyte(data, TIME_SEC)
    ms = (get_databyte(data, TIME_MSH) << 8) | get_databyte(data, TIME_MSL)
    return f"{year}-{month}-{day}||{hour}:{min}:{sec}:{ms}"

def convert_signed(data, high_byte, low_byte):
    # 获取16位数
    value = (get_databyte(data, high_byte) << 8) | get_databyte(data, low_byte)
    
    # 转换为有符号数
    if value & 0x8000:  # 检查最高位是否为1
        value = value - 0x10000  # 如果最高位为1，转为有符号数
    
    return value

class DataGenerator:
    def __init__(self, activity_id=-1, user_id=-1, flag=PRINT_TERMINAL, max_runtime_seconds=None, host="0.0.0.0" , port=8524, window_size=171):
        self.activity_id = activity_id
        self.user_id = user_id
        self.flag = flag
        self.max_runtime_seconds = max_runtime_seconds
        self.host = host
        self.port = port
        self.window_size = window_size
        self.start_time = time.time()
        # self.time_up = False


    # 定义UDP数据包接收函数
    def receive_udp_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.host, self.port))
            print(f"Listening for UDP packets on {self.host}:{self.port}")
            while True:
                # if self.time_up:
                #     return
                data, addr = s.recvfrom(1024) 
                fifo_queue.put(data, timeout=5)  # 将数据包放入FIFO队列
    def store_data(self): 
        
        
        data_list = []
        tensor_data = []
        while True:
            with state_lock:
                try:
                    current_time = time.time()
                    elapsed_time = current_time - self.start_time

                    if self.max_runtime_seconds is not None and elapsed_time > self.max_runtime_seconds:
                        # 如果运行时间超过规定时间，退出循环
                        print(f"\nMax runtime of {self.max_runtime_seconds} seconds reached.")
                        if self.flag & SAVE_FILE:
                            filename = f"dataset/{self.activity_id}_{self.user_id}_data.csv"
                            self.flag &= ~SAVE_FILE     
                            print(f"{len(data_list)} packages")
                            result_df = pd.concat(data_list, ignore_index=True)
                            # 追加到文件，不写入列名
                            result_df.to_csv(filename, mode='a', header=False, index=False)
                            print("Dataset saved")
                            data_list.clear()
                            self.max_runtime_seconds = None
                        # self.time_up = True
                        # break
                    data = fifo_queue.get(timeout=5)  # 从FIFO队列获取数据
                    time_str = get_time(data)

                    ax = convert_signed(data, DATA_AXH, DATA_AXL)
                    ay = convert_signed(data, DATA_AYH, DATA_AYL)
                    az = convert_signed(data, DATA_AZH, DATA_AZL)
                    gx = convert_signed(data, DATA_GXH, DATA_GXL)
                    gy = convert_signed(data, DATA_GYH, DATA_GYL)
                    gz = convert_signed(data, DATA_GZH, DATA_GZL)
                    hx = convert_signed(data, DATA_HXH, DATA_HXL)
                    hy = convert_signed(data, DATA_HYH, DATA_HYL)
                    hz = convert_signed(data, DATA_HZH, DATA_HZL)

                    sample_data = [round(ax, 2),round(ay, 2), round(az, 2), round(gx, 2), round(gy, 2), round(gz, 2), round(hx, 2), round(hy, 2), round(hz, 2)]

                    if self.flag & PRINT_TERMINAL: # 输出到终端
                        print(f"{time_str}||{sample_data[0]}:{sample_data[1]}:{sample_data[2]}||{sample_data[3]}:{sample_data[4]}:{sample_data[5]}||{sample_data[6]}:{sample_data[7]}:{sample_data[8]}             \r", end="", flush=True)
                    
                    if self.flag & PRINT_GUI:
                        commu.signal_send_list.emit(sample_data)
                        
                    if self.flag & SAVE_FILE: # 保存到文件
                        data_dict = {
                        # "Time": [time_str],
                        "Label": [self.activity_id],
                        "AX": [sample_data[0]],
                        "AY": [sample_data[1]],
                        "AZ": [sample_data[2]],
                        "GX": [sample_data[3]],
                        "GY": [sample_data[4]],
                        "GZ": [sample_data[5]],
                        "HX": [sample_data[6]],
                        "HY": [sample_data[7]],
                        "HZ": [sample_data[8]]
                        }
                        data_df = pd.DataFrame(data_dict)
                        data_list.append(data_df)
                    if self.flag & SEND_TENSOR: # 以张量形式发送给神经网络
                        tensor_row = [ax, ay, az, gx, gy, gz, hx, hy, hz]
                        tensor_data.append(tensor_row)

                        if len(tensor_data) == window_size:  # 检查是否达到所需长度
                            tensor_array = np.array(tensor_data).reshape(1, window_size, 9, 1)
                            tensor_queue.put(tensor_array)
                            tensor_data = []  # 重置列表以存储新的数据
                except queue.Empty:
                    pass  # 如果队列为空，继续等待新数据
                

            



if __name__ == "__main__":
    # 配置UDP监听主机和端口
    # host = "0.0.0.0"  # 0.0.0.0 表示监听所有可用的网络接口
    # port = 8524  
    generator = DataGenerator()
    # 创建线程并启动UDP数据包接收
    udp_thread = threading.Thread(target=generator.receive_udp_data)
    udp_thread.start()

    display_thread = threading.Thread(target=generator.store_data)
    display_thread.start()

    while True:
        pass