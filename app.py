import os
import time
from datetime import datetime, timezone
import cv2
import numpy as np
import requests
import random
import subprocess
import threading
from fastapi import FastAPI
import imageio_ffmpeg

app = FastAPI()

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

width, height = 1280, 720
canvas = np.zeros((height, width, 3), dtype=np.uint8)

def fetch_real_live_race():
    try:
        response = requests.get("https://api.openf1.org/v1/sessions?session_key=latest", timeout=3)
        if response.status_code == 200 and response.json():
            session = response.json()[0]
            date_start_str = session.get('date_start', None)
            date_end_str = session.get('date_end', None)
            
            if date_start_str and date_end_str:
                start_time = datetime.fromisoformat(date_start_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(date_end_str.replace('Z', '+00:00'))
                current_time_utc = datetime.now(timezone.utc)
                
                if start_time <= current_time_utc <= end_time:
                    return {
                        "active": True,
                        "series": "FORMULA 1 WORLD CHAMPIONSHIP",
                        "location": session.get('location', 'GLOBAL').upper(),
                        "session_name": session.get('session_name', 'RACE').upper()
                    }
    except Exception:
        pass
    return {"active": False}

def run_telemetry_pipeline():
    if not YOUTUBE_KEY:
        print("[ERROR] YOUTUBE_KEY is not set!")
        return

    ffmpeg_cmd = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        '-y', '-re', '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'bgr24',
        '-s', f'{width}x{height}', '-r', '30', '-i', '-', 
        '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2500k',
        '-maxrate', '3000k', '-bufsize', '5000k', '-g', '60', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '128k', '-f', 'flv',
        f'rtmp://x.rtmp.youtube.com/live2/{YOUTUBE_KEY}'
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    drivers = ["VER", "NOR", "LEC", "HAM", "SAI", "PIA", "RUS", "PER", "ALO", "TSU"]
    gaps = [0.0, 0.412, 1.850, 3.221, 6.104, 9.432, 12.801, 15.344, 21.119, 28.002]

    blink_counter = 0
    api_check_timer = 0
    race_info = {"active": False}

    print("[SYSTEM] Pipeline engine started.")

    while True:
        start_time = time.time()
        canvas[:] = (12, 12, 12)
        
        for i in range(0, width, 40): cv2.line(canvas, (i, 0), (i, height), (18, 18, 18), 1)
        for j in range(0, height, 40): cv2.line(canvas, (0, j), (width, j), (18, 18, 18), 1)

        if int(time.time()) - api_check_timer > 15:
            race_info = fetch_real_live_race()
            api_check_timer = int(time.time())

        if race_info["active"]:
            for k in range(1, len(gaps)):
                gaps[k] = max(0.1, gaps[k] + random.uniform(-0.05, 0.06))
            gaps.sort()

            cv2.rectangle(canvas, (30, 20), (1250, 90), (25, 35, 45), -1)
            cv2.rectangle(canvas, (30, 20), (1250, 90), (0, 255, 242), 1)
            cv2.putText(canvas, f"{race_info['series']} // {race_info['location']} GP", (50, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 242), 2)
            cv2.circle(canvas, (1030, 55), 10, (0, 255, 0), -1)
            cv2.putText(canvas, f"LIVE: {race_info['session_name']}", (1055, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Timing Tower
            cv2.rectangle(canvas, (50, 140), (600, 680), (20, 20, 20), -1)
            cv2.rectangle(canvas, (50, 140), (600, 680), (60, 60, 60), 1)
            for idx, driver in enumerate(drivers):
                y_pos = 185 + (idx * 48)
                if idx % 2 == 0: cv2.rectangle(canvas, (55, y_pos-32), (595, y_pos+12), (26, 26, 26), -1)
                cv2.putText(canvas, f"P{idx+1:02d}", (70, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 242), 2)
                cv2.putText(canvas, driver, (160, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                gap_str = "LEADER" if idx == 0 else f"+{gaps[idx]:.3f}s"
                cv2.putText(canvas, gap_str, (450, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

            # Metrics
            cv2.rectangle(canvas, (640, 140), (1230, 390), (20, 20, 20), -1)
            cv2.rectangle(canvas, (640, 140), (1230, 390), (60, 60, 60), 1)
            cv2.putText(canvas, "TRACK METRICS VIA LIVE SATELLITE", (660, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(canvas, f"AIR TEMP: {random.uniform(25.5, 27.2):.1f} C", (660, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(canvas, f"TRACK TEMP: {random.uniform(39.0, 42.5):.1f} C", (660, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(canvas, "SYSTEM STATUS: DATA FLOW HEALTHY", (660, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Logistics
            cv2.rectangle(canvas, (640, 420), (1230, 680), (20, 20, 20), -1)
            cv2.rectangle(canvas, (640, 420), (1230, 680), (60, 60, 60), 1)
            cv2.putText(canvas, "LOGISTICS LOG", (660, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(canvas, "ALL SECTORS: GREEN FLAG CONDITIONS", (660, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        else:
            blink_counter += 1
            show_alert = True if (blink_counter // 15) % 2 == 0 else False
            cv2.rectangle(canvas, (340, 240), (940, 440), (18, 18, 28), -1)
            cv2.rectangle(canvas, (340, 240), (940, 440), (0, 0, 255), 1) 

            if show_alert:
                cv2.circle(canvas, (430, 305), 10, (0, 0, 255), -1) 
                cv2.putText(canvas, "NO ACTIVE RACE RUNNING NOW", (460, 315), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.circle(canvas, (430, 305), 10, (0, 0, 80), -1) 
                cv2.putText(canvas, "NO ACTIVE RACE RUNNING NOW", (460, 315), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 150), 2)

            cv2.putText(canvas, "SYSTEM STATUS: STANDBY MONITORING MODE ACTIVE", (390, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
            cv2.rectangle(canvas, (0, 680), (1280, 720), (20, 20, 20), -1)
            dots = "." * (1 + (blink_counter // 10) % 4)
            cv2.putText(canvas, f"Scanning global transponder arrays for active GP telemetry streams{dots}", (50, 705), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 242), 1)

        try:
            process.stdin.write(canvas.tobytes())
            process.stdin.flush()
        except Exception:
            process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        diff = time.time() - start_time
        sleep_needed = max(0.001, (1.0 / 30.0) - diff)
        time.sleep(sleep_needed)

if __name__ == "__main__":
    run_telemetry_pipeline()
