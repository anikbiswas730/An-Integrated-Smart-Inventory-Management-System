import socket
import struct

def send_frame_over_tcp(frame, host='0.0.0.0', port=8000):
    """Send a single JPEG frame over TCP (used by video_stream.py)"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        _, jpg = cv2.imencode('.jpg', frame)
        data = jpg.tobytes()
        client.sendall(struct.pack('<L', len(data)) + data)
    finally:
        client.close()
