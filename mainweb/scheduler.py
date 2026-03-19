from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .models import Cache_dir, Room_user, Rooms
from webpush import send_user_notification
import json, requests, time, threading

sended_10min = set()
sended_5min = set()

def send_push_to_user(user, payload):
    def _send():
        send_user_notification(user=user, payload=payload, ttl=1000)
    
    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


def check_database():
    global sended_10min, sended_5min
    rooms = Rooms.objects.all()
    for room in rooms:
        if room.start_time < time.time():
            # TODO: 알림 전송 기능
            print(f"[DELETED] {room.context}")
            room.delete()
        elif room.start_time - 300 < time.time():
            # TODO: 5분 전 알림 전송 기능
            if room.roomid not in sended_5min:
                room_users = Room_user.objects.filter(room=room)
                for user in room_users:
                    payload = {
                        'head': '카풀이 5분 남았습니다!',
                        'body': '약속 장소에서 대기해주세요!'
                    }
                    send_push_to_user(user=user.user, payload=payload)
                    # send_user_notification(user=user.user, payload=payload, ttl=300)
                    print(f"[5 min] {room.context}")
                sended_5min.add(room.roomid)
        elif room.start_time - 600 < time.time():
            # TODO: 10분 전 알림 전송 기능
            if room.roomid not in sended_10min:
                for user in room_users:
                    payload = {
                        'head': '카풀이 10분 남았습니다!',
                        'body': '약속 장소에서 대기해주세요!'
                    }
                    send_push_to_user(user=user.user, payload=payload)
                    print(f"[10 min] {room.context}")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_database, 'interval', seconds=5, id='check_database_id', replace_existing=True, misfire_grace_time=None)
    scheduler.start()