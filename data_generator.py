import threading
import socket
import queue  # 用于创建FIFO队列
import numpy as np
import time
import pandas as pd


# 定义一个FIFO队列，用于存储UDP数据包
fifo_queue = queue.Queue(maxsize=10)

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

time_up = False


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


# 定义UDP数据包接收函数
def receive_udp_data(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        print(f"Listening for UDP packets on {host}:{port}")
        while True:
            if time_up:
                return
            data, addr = s.recvfrom(1024) 
            fifo_queue.put(data, timeout=5)  # 将数据包放入FIFO队列

def convert_signed(data, high_byte, low_byte):
    # 获取16位数
    value = (get_databyte(data, high_byte) << 8) | get_databyte(data, low_byte)
    
    # 转换为有符号数
    if value & 0x8000:  # 检查最高位是否为1
        value = value - 0x10000  # 如果最高位为1，转为有符号数
    
    return float(value)
            

def store_data(activity_id=-1, user_id=-1, save_to_file=False, max_runtime_seconds= 9999):
    
    filename = f"dataset/{activity_id}_{user_id}_data.csv"
    start_time = time.time()
    data_list = []
    
    while True:
        try:
            current_time = time.time()
            elapsed_time = current_time - start_time

            if max_runtime_seconds is not None and elapsed_time > max_runtime_seconds:
                # 如果运行时间超过规定时间，退出循环
                print(f"\nMax runtime of {max_runtime_seconds} seconds reached.")
                time_up = True
                break
            data = fifo_queue.get(timeout=5)  # 从FIFO队列获取数据
            time_str = get_time(data)
            # ax = float((get_databyte(data, DATA_AXH) << 8) | get_databyte(data, DATA_AXL))/32768*16*9.8
            # ay = float((get_databyte(data, DATA_AYH) << 8) | get_databyte(data, DATA_AYL))/32768*16*9.8
            # az = float((get_databyte(data, DATA_AZH) << 8) | get_databyte(data, DATA_AZL))/32768*16*9.8
            # gx = float((get_databyte(data, DATA_GXH) << 8) | get_databyte(data, DATA_GXL))/32768*2000
            # gy = float((get_databyte(data, DATA_GYH) << 8) | get_databyte(data, DATA_GYL))/32768*2000
            # gz = float((get_databyte(data, DATA_GZH) << 8) | get_databyte(data, DATA_GZL))/32768*2000
            # hx = float((get_databyte(data, DATA_HXH) << 8) | get_databyte(data, DATA_HXL))*100/1024
            # hy = float((get_databyte(data, DATA_HYH) << 8) | get_databyte(data, DATA_HYL))*100/1024
            # hz = float((get_databyte(data, DATA_HZH) << 8) | get_databyte(data, DATA_HZL))*100/1024

            ax = convert_signed(data, DATA_AXH, DATA_AXL)
            ay = convert_signed(data, DATA_AYH, DATA_AYL)
            az = convert_signed(data, DATA_AZH, DATA_AZL)
            gx = convert_signed(data, DATA_GXH, DATA_GXL)
            gy = convert_signed(data, DATA_GYH, DATA_GYL)
            gz = convert_signed(data, DATA_GZH, DATA_GZL)
            hx = convert_signed(data, DATA_HXH, DATA_HXL)
            hy = convert_signed(data, DATA_HYH, DATA_HYL)
            hz = convert_signed(data, DATA_HZH, DATA_HZL)

            # 输出到终端
            print(f"{time_str}||{round(ax, 2)}:{round(ay, 2)}:{round(az, 2)}||{round(gx, 2)}:{round(gy, 2)}:{round(gz, 2)}||{round(hx, 2)}:{round(hy, 2)}:{round(hz, 2)}             \r", end="", flush=True)
            data_dict = {
            # "Time": [time_str],
            "Label": [activity_id],
            "AX": [round(ax, 2)],
            "AY": [round(ay, 2)],
            "AZ": [round(az, 2)],
            "GX": [round(gx, 2)],
            "GY": [round(gy, 2)],
            "GZ": [round(gz, 2)],
            "HX": [round(hx, 2)],
            "HY": [round(hy, 2)],
            "HZ": [round(hz, 2)]
            }
            data_df = pd.DataFrame(data_dict)
            data_list.append(data_df)
        except queue.Empty:
            pass  # 如果队列为空，继续等待新数据
        
    if save_to_file:
        print(f"{len(data_list)} packages")
        result_df = pd.concat(data_list, ignore_index=True)
        # 追加到文件，不写入列名
        result_df.to_csv(filename, mode='a', header=False, index=False)
        print("Dataset saved")
    return

if __name__ == "__main__":
    # 配置UDP监听主机和端口
    host = "0.0.0.0"  # 0.0.0.0 表示监听所有可用的网络接口
    port = 8524  

    # 创建线程并启动UDP数据包接收
    udp_thread = threading.Thread(target=receive_udp_data, args=(host, port))
    udp_thread.start()

    display_thread = threading.Thread(target=store_data)
    display_thread.start()

    while True:
        pass