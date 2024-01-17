def print_logo():
    print(" ________  ________  ________  ___       __      ")
    print("|\   ____\|\   ____\|\   __  \|\  \     |\  \    ")
    print("\ \  \___|\ \  \___|\ \  \|\  \ \  \    \ \  \   ")
    print(" \ \  \  __\ \_____  \ \   ____\ \  \  __\ \  \  ")
    print("  \ \  \|\  \|____|\  \ \  \___|\ \  \|\__\_\  \ ")
    print("   \ \_______\____\_\  \ \__\    \ \____________\\")
    print("    \|_______|\_________\|__|     \|____________|")
    print("             \|_________|    ")
    print("========General Sensing Platform on Wrist========")

import argparse
from data_generator import PRINT_TERMINAL, PRINT_GUI, SAVE_FILE, SEND_TENSOR, DataGenerator
import threading
import classifier
from classifier import Classifier

parser = argparse.ArgumentParser()
parser.add_argument("--mode", metavar="M", type=int, help='choose a mode', required=True)
parser.add_argument("--activity_id", metavar="A", type=int, help='activity id', default=-1, required=False)
parser.add_argument("--user_id", metavar="U", type=int, help='user id', default=-1, required=False)
parser.add_argument("--duration", metavar="D", type=int, help='duration of the logging mode', default=9999, required=False)
args = parser.parse_args()

if __name__ == "__main__":
    # 配置UDP监听主机和端口
    print_logo()
    host = "0.0.0.0"  
    port = 8524  
    generator = DataGenerator()
    generator.host = host
    generator.port = port

    
    if args.mode == 0:  #模式0：建立udp连接，并将接收到的数据实时显示在终端
        generator.flag = PRINT_TERMINAL
        # 创建线程并启动UDP数据包接收
        udp_thread = threading.Thread(target=generator.receive_udp_data)
        udp_thread.start()

        logging_thread = threading.Thread(target=generator.store_data)
        logging_thread.start()
    elif args.mode == 1:   #模式1：建立udp链接，并将接收到的数据存入指定文件
        if args.activity_id >= 0 and args.user_id >= 0:
            generator.flag = PRINT_TERMINAL | SAVE_FILE
            generator.activity_id = args.activity_id
            generator.user_id = args.user_id
            generator.max_runtime_seconds = args.duration
            udp_thread = threading.Thread(target=generator.receive_udp_data)
            udp_thread.start()

            logging_thread = threading.Thread(target=generator.store_data)
            logging_thread.start()
        else:
            print("Please provide both activity_id and user_id.")
    elif args.mode == 2:    #模式2，建立udp连接，对接收到的数据进行预处理、再进行推理，最终得到预测结果
        generator.flag = PRINT_TERMINAL|SEND_TENSOR
        cf = Classifier("./model/model.onnx")

        udp_thread = threading.Thread(target=generator.receive_udp_data)
        udp_thread.start()
        logging_thread = threading.Thread(target=generator.store_data)
        logging_thread.start()
        classify_thread = threading.Thread(target=classifier.classification_thread, args=(cf,))
        classify_thread.start()



