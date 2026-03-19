from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cache_dir, Room_user, Rooms
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
import json, requests, time
from webpush import send_user_notification
from webpush.models import PushInformation, SubscriptionInfo
from django.contrib.auth import get_user_model

def send_push_to_user(user):
    payload = {
        "head": "알림 제목",
        "body": "이 유저에게만 가는 알림"
    }

    send_user_notification(
        user=user,
        payload=payload,
        ttl=1000
    )

PAGE_COUNT = 3
KAKAO_RESTAPI_KEY = "4979865108142105c0168166472d11c5"

def str2unixtime(string):
    dt = datetime.fromisoformat(string)
    return int(dt.timestamp())

def unixtime2str(unixtime):
    dt = datetime.fromtimestamp(unixtime)
    return dt.strftime("%m-%d %H:%M")

def predict_money(startX, startY, endX, endY):
    base_url = 'https://app.map.kakao.com/route/carset/mobility.json'
    params = {
        'origin': f'{startX},{startY}',
        'destination': f'{endX},{endY}',
    }
    try:
        response = requests.get(base_url, params=params)
        print(response.json()["results"][0]["summary"]["fare"]["taxi"])
        return response.json()["results"][0]["summary"]["fare"]["taxi"]
    except Exception as e:
        return False



def xy2address(x: str, y: str):
    cha = Cache_dir.objects.filter(x=x, y=y).first()
    print(cha)
    if cha and cha.context != '':
        return cha.context
    else:
        try:
            response = requests.get(
                f"https://dapi.kakao.com/v2/local/geo/coord2address?x={x}&y={y}", 
                headers = {"Authorization" : f"KakaoAK {KAKAO_RESTAPI_KEY}"}
            )
            print(response)
            if response.status_code != 200:
                return ""
            data = response.json()
            print(data)
            if data.get("documents", None):
                context = ""
                if data["documents"][0].get("road_address", None):
                    context = f"{data["documents"][0]["road_address"].get("address_name", "")} ({data["documents"][0]["road_address"].get("building_name", "")})"
                else:
                    context = data["documents"][0]["address"]["address_name"]
                chache = Cache_dir()
                chache.x = x
                chache.y = y
                chache.context = context
                chache.save()
                return context
            else:
                return ""
        except Exception as e:
            print(e)
            return e
        
@csrf_exempt
def save_webpush(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'no'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'status': 'no'}, status=405)
    
    data = json.loads(request.body)
    sub = data.get("subscription")
    
    endpoint = sub.get("endpoint")
    p256dh = sub["keys"]["p256dh"]
    auth = sub["keys"]["auth"]
    
    subscription, _ = SubscriptionInfo.objects.get_or_create(
        endpoint=endpoint,
        defaults={"p256dh": p256dh, "auth": auth, "browser": "chrome"}
    )
    
    PushInformation.objects.update_or_create(
        user=request.user,
        defaults={"subscription": subscription}
    )
    
    return JsonResponse({'status': 'ok'})


@login_required(login_url='/auth/login')
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def get_room_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'no'
        })
    if request.method == 'GET':
        try:
            start_txt = request.GET.get('start_txt', "")
            end_txt = request.GET.get('end_txt', "")
            page = int(request.GET.get('page', 1))
            if page < 1:
                return JsonResponse({
                    'status': 'no'
                })
            cont = Rooms.objects.annotate(
                user_count=Count('room_user')
            ).filter(
                start_txt__icontains=start_txt,
                end_txt__icontains=end_txt
            ).order_by('-roomid')
            
            cnt = 0
            start = (page-1) * PAGE_COUNT
            cont = list(cont.values())
            real_reuslt = []
            for c in cont:
                if c["max_people"] > c["user_count"]:
                    cnt += 1
                    real_reuslt.append(c)
            
            real_reuslt = real_reuslt[start:PAGE_COUNT+1]
            
            data = {
                'status': 'success',
                'counts': cnt,
                'content': real_reuslt
            }
        except Exception as e:
            print(e)
            data = {
                'status': 'no'
            }
    else:
        data = {
            'status': 'no'
        }
    return JsonResponse(data)

@csrf_exempt
def create_room_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'no'
        })
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            room = Rooms()
            room.creater = request.user
            start_xy = data["start"].split("/")
            room.start = data["start"]
            room.start_txt = xy2address(start_xy[0], start_xy[1])
            end_xy = data["end"].split("/")
            room.end = data["end"]
            room.end_txt = xy2address(end_xy[0], end_xy[1])
            if not 0 < len(data["context"]) <= 25:
                return JsonResponse({
                    'status': 'no',
                    'message': "1자 이상 25자 이하로 입력해 주세요."
                })
            room.context = data["context"]
            try:
                room.max_people = int(data["max_p"])
                if not 1 < room.max_people < 15:
                    return JsonResponse({
                        'status': 'no',
                        'message': "2명 이상 15명 이하로 입력해 주세요."
                    })
            except Exception as e:
                return JsonResponse({
                    'status': 'no',
                    'message': "올바른 형식으로 입력해주세요."
                })
            pred = predict_money(
                start_xy[0], 
                start_xy[1],
                end_xy[0],
                end_xy[1]
            )
            if not pred:
                return JsonResponse({
                    'status': 'no',
                    'message': "택시가 다닐 수 없는 길입니다."
                })
            room.predict_money = pred
            if str2unixtime(data["start_time"]) < time.time():
                return JsonResponse({
                    'status': 'no',
                    'message': "지금보다 이후로 입력하여 주세요."
                })
            room.start_time = str2unixtime(data["start_time"])
            
            roomuser = Room_user()
            roomuser.room = room
            roomuser.user = request.user
            
            room.save()
            try:
                roomuser.save()
            except Exception as e:
                print(e)
                roomuser.delete()
                data = {
                    'status': 'no'
                }
            else:
                data = {
                    'status': 'success',
                    'message': 'created'
                }
        except Exception as e:
            print(e)
            data = {
                'status': 'no'
            }
    else:
        data = {
            'status': 'no'
        }
    return JsonResponse(data)

@csrf_exempt
def participant_room_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'no'
        })
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # print(data)
            room_id = data.get('roomid')
            # print(room_id)
            is_roomuser = Room_user.objects.filter(user=request.user, room=room_id).exists()
            if is_roomuser:
                return JsonResponse({
                    'status': 'no',
                    "message": "이미 참여중입니다."
                })
            try:
                room = Rooms.objects.get(roomid=room_id)
            except Rooms.DoesNotExist:
                return JsonResponse({
                    'status': 'no', 
                    'message': 'room not exists'
                })
            max_people = getattr(room, 'max_people', 0) 

            current_cnt = Room_user.objects.filter(room_id=room_id).count()
            if max_people > 0 and current_cnt >= max_people:
                return JsonResponse({
                    'status': 'no',
                    'message': 'room is full'
                })
                
            Room_user.objects.create(user=request.user, room=room)
            return JsonResponse({
                'status': 'success',
                'message': 'participated'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'no'
            })
    else:
        return JsonResponse({
            'status': 'no'
        })

@csrf_exempt
def get_myroom_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'no'
        })
    if request.method == 'GET':
        try:
            room_fields = [f'room__{f.name}' for f in Rooms._meta.get_fields() if not f.is_relation]
            rooms_data = list(
                Room_user.objects.filter(user=request.user)
                .values('id', *room_fields)
                .annotate(user_count=Count('room__room_user'))
            )
            clean_data = []
            for entry in rooms_data:
                new_entry = {k.replace('room__', ''): v for k, v in entry.items()}
                clean_data.append(new_entry)

            return JsonResponse({
                'status': 'success',
                'rooms': clean_data
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'no'
            })
    else:
        return JsonResponse({
            'status': 'no'
        })
        
@csrf_exempt
def leave_room_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'no'
        })
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            room_id = data.get('roomid')
            room_user = Room_user.objects.filter(room=room_id)
            rmc = Room_user.objects.filter(room=room_id).count() - 1
            print(rmc)
            if not room_user.filter(user=request.user).exists():
                return JsonResponse({
                    'status': 'no',
                    'message': '참여하지 않은 방입니다.'
                })
            room_user.filter(user=request.user).delete()
            if rmc < 1:
                Rooms.objects.filter(roomid=room_id).delete()
            return JsonResponse({
                'status': 'success'
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                'status': 'no'
            })
    else:
        return JsonResponse({
            'status': 'no'
        })

@csrf_exempt
def swjs(request):
    jsfile = """self.addEventListener('push', function(event) {
    const data = event.data.json();

    self.registration.showNotification(data.head, {
        body: data.body,
        icon: data.icon,
    });
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data?.url || "/")
    );
});"""
    return HttpResponse(jsfile, content_type="application/javascript")

@login_required(login_url='/auth/login')
def mypage_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
 
        errors = {}
        User_ = get_user_model()
 
        if not name:
            errors['name'] = '이름을 입력해주세요.'
        if not username:
            errors['username'] = '아이디를 입력해주세요.'
        if User_.objects.exclude(pk=request.user.pk).filter(username=username).exists():
            errors['username'] = '이미 사용중인 아이디입니다.'
        if password1 or password2:
            if len(password1) < 8:
                errors['password1'] = '비밀번호는 8자 이상이어야 합니다.'
            elif password1 != password2:
                errors['password2'] = '비밀번호가 일치하지 않습니다.'
 
        if errors:
            return render(request, 'mypage.html', {'errors': errors, 'user': request.user})
 
        request.user.name = name
        request.user.username = username
        request.user.email = email
        if password1:
            request.user.set_password(password1)
        request.user.save()
        update_session_auth_hash(request, request.user)
 
        return render(request, 'mypage.html', {'success': True, 'user': request.user})
 
    return render(request, 'mypage.html')
