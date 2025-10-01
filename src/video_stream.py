# src/video_stream.py
import cv2
import socket
import struct
import sys

def start_video_stream(host='0.0.0.0', port=8000, width=320, height=240, fps=15):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[INFO] Video stream listening on {host}:{port}")

    try:
        conn, addr = server_socket.accept()
        print(f"[INFO] Client connected: {addr}")
        connection = conn.makefile('wb')
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, jpg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            data = jpg.tobytes()
            connection.write(struct.pack('<L', len(data)))
            connection.write(data)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        server_socket.close()

if __name__ == "__main__":
    start_video_stream()
