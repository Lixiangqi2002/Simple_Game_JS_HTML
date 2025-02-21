from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import numpy as np

app = Flask(__name__)
CORS(app)

used_offsets = set()  # 存储已经使用过的偏移值
current_offset = 1  # 递增模式的起始值
# model = joblib.load("mlp_level_predictor.pkl")

def get_sensor_data():
    """模拟传感器数据，这里要替换成真实的读取代码"""
    heart_rate = random.uniform(60, 100)  # 真实情况下这里要改成实际传感器数据
    skin_conductance = random.uniform(0.1, 1.0)
    eeg_signal = random.uniform(0.1, 0.5)
    stress_level = random.uniform(1, 10)
    return np.array([[heart_rate, skin_conductance, eeg_signal, stress_level]])

def get_sequential_offset():
    """获取递增的偏移值（一个一个加），并确保不重复"""
    global current_offset
    if current_offset > 23:
        current_offset = 1  # 重新从1开始
    offset = current_offset
    current_offset += 1
    return offset

def get_unique_random_offset():
    """生成一个1到23之间的不重复随机数"""
    global used_offsets
    available_numbers = set(range(1, 24)) - used_offsets  # 计算剩余可用数字

    if not available_numbers:
        used_offsets.clear()  # 如果所有数字都用完了，清空集合并重新开始
        available_numbers = set(range(1, 24))

    new_offset = random.choice(list(available_numbers))  # 选择一个新数字
    used_offsets.add(new_offset)  # 记录已经使用的数字
    return new_offset

@app.route('/predict_level_offset', methods=['GET'])
def predict_level_offset():
    try:
        mode = request.args.get('mode', 'random')  # 获取模式参数，默认是递增模式
        sensor_data = get_sensor_data()

        if mode == 'sequential':
            predicted_offset_rounded = get_sequential_offset()
        elif mode == 'random':
            predicted_offset_rounded = get_unique_random_offset()
        elif mode == 'model':
            # 这里可以替换成真实模型预测逻辑
            predicted_offset_rounded = random.randint(1, 23)  # 假设模型预测随机数
        else:
            return jsonify({"error": "Invalid mode. Use 'sequential', 'random', or 'model'."})

        print("=== Flask Debug ===")
        print("Mode:", mode)
        print("Sensor Data:", sensor_data)
        print("Predicted Level Offset:", predicted_offset_rounded)
        print("Used Offsets (if random mode):", used_offsets)
        print("===================")

        return jsonify({"next_level_offset": predicted_offset_rounded})
    except Exception as e:
        print("Error in predict_level_offset:", str(e))
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
