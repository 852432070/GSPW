import onnxruntime as ort
import numpy as np
import threading
import time
from data_generator import tensor_queue
from sklearn.preprocessing import StandardScaler
import pickle
from PyQt5.QtCore import pyqtSignal, QObject


scaler = pickle.load(open('/home/shichang/imuServer/model/scaler.pkl', 'rb'))



class Classifier(QObject):
    signal_predict = pyqtSignal(int)
    def __init__(self, model_path):
        super().__init__()
        # 初始化ONNX运行时会话
        self.session = ort.InferenceSession(model_path)

    def predict(self, data):

        input_name = self.session.get_inputs()[0].name
        data = np.array(data, dtype=np.float32)

        # 进行预测
        outputs = self.session.run(None, {input_name: data})


        predictions = np.argmax(outputs[0], axis=1)

        self.signal_predict.emit(predictions[0])

        return predictions
    
def classification_thread(classifier):
    while True:
        # if not tensor_queue.empty():
        tensor = tensor_queue.get()
        tensor_shape = tensor.shape
        tensor = scaler.transform(tensor.astype(np.float32).reshape(-1,1)).reshape(tensor_shape[0], tensor_shape[1], tensor_shape[2], 1)
        # tensor = scaler.fit_transform(tensor.astype(np.float32).reshape(-1,1)).reshape(tensor_shape[0], tensor_shape[1], tensor_shape[2], 1)
        prediction = classifier.predict(tensor)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("\n")
        print(f"Time: {current_time}, Prediction: {prediction}\n")