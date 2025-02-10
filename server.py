from flask import Flask, jsonify
from flask_cors import CORS 
import random
import numpy as np
app = Flask(__name__)
CORS(app)
# model = joblib.load("mlp_level_predictor.pkl")

def get_sensor_data():
    """模拟传感器数据，这里要替换成真实的读取代码"""
    heart_rate = random.uniform(60, 100)  # 真实情况下这里要改成实际传感器数据
    skin_conductance = random.uniform(0.1, 1.0)
    eeg_signal = random.uniform(0.1, 0.5)
    stress_level = random.uniform(1, 10)
    return np.array([[heart_rate, skin_conductance, eeg_signal, stress_level]])

@app.route('/predict_level_offset', methods=['GET'])
def predict_level_offset():
    try:
        sensor_data = get_sensor_data()
        predicted_offset = random.uniform(1, 2)  # 这里要替换成真实的预测模型
        # predicted_offset_rounded = int(round(predicted_offset))
        predicted_offset_rounded = 1
        print("=== Flask Debug ===")
        print("Sensor Data:", sensor_data)
        print("Predicted Level Offset:", predicted_offset_rounded)
        print("===================")

        return jsonify({"next_level_offset": predicted_offset_rounded})
    except Exception as e:
        print("Error in predict_level_offset:", str(e))
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
