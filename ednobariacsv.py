import os
import csv
import cv2
import pygame
import time
from flask import Flask, Response
from buildhat import Motor, DistanceSensor
from picamera2 import Picamera2
import threading
import numpy as np
from datetime import datetime

# Flaskの初期化
app = Flask(__name__)

# Pygameの初期化
try:
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        raise ValueError("ジョイスティックが検出されませんでした。接続を確認してください。")
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Pygameとジョイスティックの初期化に成功しました。")
except Exception as e:
    print(f"Pygame初期化エラー: {e}")
    pygame.quit()
    raise SystemExit("Pygameの初期化に失敗しました。終了します。")

# Build HATモーターとセンサーの初期化
motor1 = Motor('A')
motor2 = Motor('B')
sensor = DistanceSensor('C')

# Picamera2の初期化
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# グローバル変数
joy_values = {"joy_ly": 0, "joy_ry": 0, "btn_maru": 0, "btn_sankaku": 0}
distance_value = -1  # センサーが無効な場合の初期値
h = 0.7  # バリア距離（m）
left_speed = 0
right_speed = 0
csv_logging_active = False  # CSV記録を管理するフラグ

# CSVファイルのパスをタイムスタンプ付きで設定
def get_csv_file_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.expanduser("~/Desktop")  # 保存先をデスクトップに設定
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"controller_log_{timestamp}.csv")

# CSVファイルの初期化
def initialize_csv(csv_file_path):
    """CSVファイルにヘッダーを記入する"""
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Joy_LY", "Joy_RY", "Left_Speed", "Right_Speed", "Distance"])

# データをCSVに記録する関数
def log_to_csv(csv_file_path):
    """定期的にデータをCSVに記録"""
    global joy_values, left_speed, right_speed, distance_value, csv_logging_active
    while True:
        if csv_logging_active:  # フラグが有効な場合のみ記録
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(csv_file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        timestamp,
                        joy_values["joy_ly"],
                        joy_values["joy_ry"],
                        left_speed,
                        right_speed,
                        f"{distance_value:.2f}"
                    ])
            except Exception as e:
                print(f"Error writing to CSV: {e}")
        time.sleep(0.1)


# ジョイスティックイベントの取得
def update_joystick():
    global joy_values, csv_logging_active
    prev_sankaku_state = False  # 前回の△ボタンの状態を記録
    while True:
        for event in pygame.event.get():
            if event.type in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
                joy_values["joy_ly"] = -int(joystick.get_axis(1) * 100)
                joy_values["joy_ry"] = -int(joystick.get_axis(4) * 100)
                joy_values["btn_maru"] = joystick.get_button(0)
                current_sankaku_state = joystick.get_button(2)  # △ボタンの状態

                # △ボタンの状態が変化したときにフラグを切り替える
                if current_sankaku_state and not prev_sankaku_state:
                    csv_logging_active = not csv_logging_active  # フラグを反転
                    print(f"CSV記録 {'開始' if csv_logging_active else '停止'}")

                prev_sankaku_state = current_sankaku_state  # 状態を更新
        time.sleep(0.1)

# 距離センサーの更新
def update_distance():
    global distance_value
    while True:
        try:
            distance_value = sensor.get_distance() * 0.001
        except Exception as e:
            print(f"Error reading distance sensor: {e}")
            distance_value = -1
        time.sleep(0.1)

# モーター制御
def control_motors():
    global joy_values, distance_value, left_speed, right_speed
    while True:
        left_speed = joy_values["joy_ly"]
        right_speed = joy_values["joy_ry"]
        motor1.start(right_speed)
        motor2.start(left_speed)

        if joy_values["btn_maru"]:
            motor1.stop()
            motor2.stop()

        time.sleep(0.1)

# Flaskのビデオストリーミング
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            try:
                frame = picam2.capture_array()
                frame[:, :, 0] = cv2.addWeighted(frame[:, :, 0], 0.6, 0, 0, 0)
                frame[:, :, 2] = cv2.addWeighted(frame[:, :, 2], 1.2, 0, 0, 0)
                # オーバーレイテキストを3段に分割
                overlay_text_1 = f"UL: {joy_values['joy_ly']} | UR: {joy_values['joy_ry']}"
                overlay_text_2 = f"SL: {left_speed} | SR: {right_speed}"
                overlay_text_3 = f"D: {distance_value:.2f} m"
              # 1段目のテキストを描画
                cv2.putText(frame, overlay_text_1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
              # 2段目のテキストを描画
                cv2.putText(frame, overlay_text_2, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
              # 3段目のテキストを描画
                cv2.putText(frame, overlay_text_3, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception as e:
                print(f"Error during video feed: {e}")
                continue

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return Response('<html><body><img src="/video_feed"></body></html>')

# プログラムの実行
if __name__ == "__main__":
    csv_file_path = get_csv_file_path()
    initialize_csv(csv_file_path)

    threads = [
        threading.Thread(target=update_joystick, daemon=True),
        threading.Thread(target=update_distance, daemon=True),
        threading.Thread(target=control_motors, daemon=True),
        threading.Thread(target=log_to_csv, args=(csv_file_path,), daemon=True),
    ]

    for thread in threads:
        thread.start()

    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        motor1.stop()
        motor2.stop()
        picam2.stop()
        pygame.quit()
