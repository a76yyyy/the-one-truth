from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json

from django.utils.timezone import now
import sys
import json

print(sys.path)

from . import models

# Create your views here.

def index(request):
    return HttpResponse('Hello, world!')


def test(request):
    msg = {"func": 'test'}
    return JsonResponse(msg)


def register_handler(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        print(username)
        password = req['password']
        group_id = req['group_id']   # TODO: changed
        email = req['email']
        user = models.User.objects.filter(name=username)
        now_time = now()

        user_id, i = 0, 0
        new_user = models.User.objects.filter(_id=i).first()
        while new_user:
            i += 1
            new_user = models.User.objects.filter(_id=i).first()
        user_id = i
        
        if not user:
            models.User.objects.create(_id=user_id, name=username, password=password, email=email,
                                       group_id=group_id, register_date=now_time, friend_num=0,
                                       last_login_time=now_time)
        else:
            error = 'Username has been registered.'
        if error is None:
            response['error_num'] = 0
            data = {
                'name': username,
                'groupid': group_id,
                'reg_time': now_time,
                "last_login_time": 0,
            }
            response['data'] = data
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def login_handler(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        password = req['password']
        user = models.User.objects.filter(name=username).first()
        if not user:
            error = 'No such user.'
        else:
            psw = user.password
            if password != psw:
                error = 'Wrong password.'
        if error is None:
            response['error_num'] = 0
            data = {
                "username": username,
                "groupid": user.group_id,
                "last_login_time": user.last_login_time,
            }
            user.last_login_time = now()
            user.save()
            response['data'] = data
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def get_friend_list_request(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        user = models.User.objects.filter(name=username).first()
        friend_list = user.get_friend_list()
        friend_name_list = [friend.name for friend in friend_list]
        data = {
            'friend_list': friend_name_list,
        }
        response['data'] = data
    return JsonResponse(response)


def add_friend_request(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        user = models.User.objects.filter(name=username).first()
        user_to_be_add_name = req['name']
        user_to_be_add = models.User.objects.filter(name=user_to_be_add_name).first()
        if not user_to_be_add:
            error = 'No such user'
        else:
            user.friend_list.add(user_to_be_add)
            user_to_be_add.friend_list.add(user)
            user.friend_num += 1
            user_to_be_add.friend_num += 1
            user.save()
            user_to_be_add.save()
        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def delete_friend_request(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        user = models.User.objects.filter(name=username).first()
        user_to_be_delete_name = req['name']
        user_to_be_delete = models.User.objects.filter(name=user_to_be_delete_name).first()
        if not user_to_be_delete:
            error = 'No such user'
        else:
            user.friend_list.remove(user_to_be_delete)
            user_to_be_delete.friend_list.remove(user)
            user.friend_num -= 1
            user_to_be_delete.friend_num -= 1
            user.save()
            user_to_be_delete.save()
        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def init_room(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        num_person = req['num_person']

        if num_person < 3:
            error = 'at least 3 persons in a room'
        else:        
            room_id = 0
            room = models.Room.objects.filter(room_id=room_id).first()
            while room:
                room_id += 1
                room = models.Room.objects.filter(room_id=room_id).first()        
            room = models.Room.objects.create(room_id=room_id, size=num_person, stage=0, script=None)

        if error is None:
            script = models.Script.objects.filter(player_num=num_person)
            script_title = [sc.title for sc in script]
            response['error_code'] = 0
            data = {
                "room_id": room_id,
                "script_to_select": script_title
            }
            response['data'] = data
        else:
            response['error_code'] = 1
            response['msg'] = error
        return JsonResponse(response)


def upsend_script(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        title = req['title']
        player_num = req['player_num']
        truth = req['truth']
        description = req['description']

        role_info = req['role_list']
        clue_info = req['clue_list']

        if len(role_info) < 4:
            error = 'at least 4 roles in a script'
        elif player_num < 3:
            error = 'at least 3 players in a script'
        else:        
            ##=== update script ===##
            sc_id = 0
            script = models.Script.objects.filter(script_id=sc_id).first()
            while script:
                sc_id += 1
                script = models.Script.objects.filter(script_id=sc_id).first()
            script = models.Script.objects.create(script_id=sc_id, title=title, truth=truth, description=description,
                                                  player_num=player_num, add_time=now(), murder_id=None)

            ##=== update role ===##        
            rl_id = 0
            for rl_info in role_info:
                role = models.Role.objects.filter(role_id=rl_id).first()
                while role:
                    rl_id += 1
                    role = models.Role.objects.filter(role_id=rl_id).first()
                role = models.Role.objects.create(role_id=rl_id, role_name=rl_info['name'], script=script, 
                                                is_murder=rl_info['is_murder'], task=rl_info['task'], 
                                                background=rl_info['background'], timeline=rl_info['timeline'],
                                                role_description=rl_info['role_description'])
                if rl_info['is_murder']:
                    script.murder_id = rl_id
                    script.save()
                rl_id += 1

            ##=== update clue ===##        
            cl_id = 0
            for cl_info in clue_info:
                clue = models.Clue.objects.filter(clue_id=cl_id).first()
                while clue:
                    cl_id += 1
                    clue = models.Clue.objects.filter(clue_id=cl_id).first()
                clue = models.Clue.objects.create(clue_id=cl_id, script=script, text=cl_info['text'],
                                                clue_description=cl_info['clue_description'])
                cl_id += 1

        if error is None:
            sc = models.Script.objects.filter(script_id=sc_id).first()
            data = {
                "script_tittle": sc.title,
                "player_num": sc.player_num,
                "truth": sc.truth,
                "description": sc.description,
                "murder": sc.murder_id
            }
            response['data'] = data
        return JsonResponse(response)


def enter_room(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        room_id = req['room_id']
        is_master = req['is_master']    ## TODO: add this request
        user = models.User.objects.filter(name=username).first()
        room = models.Room.objects.filter(room_id=room_id).first()

        if not user:
            error = 'no such user'
        elif not room:
            error = 'no such room'
        else:
            player_list = models.Player.objects.filter(room_id=room_id)
            if len(player_list) == room.size:
                error = 'no seats left in this room'
            else:
                player = models.Player.objects.filter(user_id=user._id).first()
                if not player:
                    player_id = 0
                    player = models.Player.objects.filter(player_id=player_id).first()
                    while player:
                        player_id += 1
                        player = models.Player.objects.filter(player_id=player_id).first()
                    player = models.Player.objects.create(player_id=player_id, user_id=user._id, 
                                                        room_id=room_id, role=None,
                                                        is_master=is_master)
                else:
                    error = username + ' has already entered a room, please exit first'

            player_list = models.Player.objects.filter(room_id=room_id)        
            player_name_list = [player.user.name for player in player_list]

            start = False
            if room.stage == 1:
                start = True

        if error is None:
            response['error_code'] = 0
            data = {
                "player_list": player_name_list,
                "start": start
            }
            response['data'] = data
        else:
            response['error_code'] = 1
            response['msg'] = error
        return JsonResponse(response)


def exit_room(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        username = req['username']
        room_id = req['room_id']
        is_master = req['is_master']    ## TODO: add this request

        user = models.User.objects.get(name=username)
        if not user:
            error = 'user ' + username + ' does not exist'
        elif not room:
            error = 'no such room'
        else:
            this_player = models.Player.objects.get(room_id=room_id, user_id=user._id)
            player_list = models.Player.objects.filter(room_id=room_id)
        
            if not this_player:
                error = username + ' is not in this room'
            elif is_master and len(player_list) > 1:
                if 'next_master_name' not in req:
                    error = 'there exists other player(s) in this room, please select one to be master'
                else:
                    next_master_name = req['next_master_name']
                    next_user = models.User.objects.get(name=next_master_name)
                    if not next_user:
                        error = 'user ' + next_master_name + ' does not exist' 
                    else:
                        next_player = models.Player.objects.get(room_id=room_id, user_id=next_user._id)
                        if not next_player:
                            error = next_master_name + ' is not in this room'
        
        if not error:
            if len(player_list) == 1:
                this_player.delete()
                room = models.Room.objects.get(room_id=room_id)
                room.delete()
                player_list = []
            else:
                this_player.delete()
                if is_master:
                    next_player.is_master = 1
                    next_player.save()
                player_list = models.Player.objects.filter(room_id=room_id)
                room.stage, room.script = 0, None
            response['error_code'] = 0
            data = {
                "player_list_name": [player.user.name for player in player_list],
                "start": start
            }
            response['data'] = data
        else:
            response['error_code'] = 1
            response['msg'] = error


def room_owner_choose_script(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        room_id = req['room_id']
        script_title = req['script_title']      # TODO: this changed
        room = models.Room.objects.filter(room_id=room_id).first()
        
        if not room:
            error = 'no such room'
        else:
            script = models.Script.objects.filter(title=script_title).first()
            if not script:
                error = 'no such script, please select again'
        if error is None:
            room.script = script
            room.save()
            response['error_code'] = 0
        else:
            response['error_code'] = 1
            response['msg'] = error
        return JsonResponse(response)


def start_game(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        room_id = req['room_id']
        script_title = req['script_title']
        script = models.Script.objects.filter(title=script_title).first()
        room = models.Room.objects.filter(room_id=room_id).first()
        role_list = models.Role.objects.filter(script_id=script.script_id)

        ##=== check the number of players ===##
        player_list = models.Player.objects.filter(room=room)
        if len(player_list) != script.player_num:
            error = 'not enough players here'

        truth = script.truth
        murder_role = models.Role.objects.filter(script=script, is_murder=1).first()

        role_id, role_name, background, timeline, task = [], [], [], [], []
        for role in role_list:
            role_id.append(role.role_id)
            role_name.append(role.role_name)
            background.append(role.background)
            timeline.append(role.timeline)
            task.append(role.task)
        clue_list = models.Clue.objects.filter(script=script)
        c_list, clue_id, clue_description = [], [], []
        for clue in clue_list:
            c_list.append(clue.text)
            clue_id.append(clue.clue_id)
            clue_description.append(clue.clue_description)

        if error is None:
            room.stage = 1
            room.script = script
            room.save()
            script_title = script.title
            data = {
                "script_title": script_title,
                "role_id": role_id,
                "role_list": role_name,
                "background": background,
                "timeline": timeline,
                "task": task,
                "truth": truth,
                "murder_id": murder_role.role_id,
                "clue_id": clue_id,
                "clue_list": c_list,
                "clue_description": clue_description
            }
            response['error_code'] = 0
            response['data']=data
        else:
            response['error_code'] = 1
            response['msg'] = error
        return JsonResponse(response)


def check_clue(request):
    if request.method == 'POST':
        response = {}
        error = None

        req = json.loads(request.body)
        room_id = req['room_id']        
        role_id = req['role_id']
        clue_id = req['clue_id']

        # check if clue id is correct
        find_clue = models.Clue.objects.filter(clue_id = clue_id)
        find_player = models.Player.objects.filter(room_id = room_id, role_id= role_id)
        print(not find_player )
        if not find_clue or not find_player:
            error = 'No such clue or no such player'
        else:
            find_player = find_player[0]
            find_clue = find_clue[0]
            models.PlayerClue(is_public = 0, player_id = find_player.player_id, clue_id = clue_id).save()

        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def refresh_clue(request):
    if request.method == 'POST':
        response = {}
        error = None

        req = json.loads(request.body)
        room_id = req['room_id']        

        # check if clue id is correct
        find_room = models.Room.objects.filter(room_id = room_id)
        if not find_room:
            error = 'No such room'
        else:
            script_id = models.Room.objects.filter(room_id = room_id)[0].script_id
            all_clue = models.Clue.objects.filter(script_id = script_id)
            data = []
            for i in range(len(all_clue)):
                #get player_clue
                clue_id = all_clue[i].clue_id
                player_clue = models.PlayerClue.objects.filter(clue_id = clue_id)
                # if no owner
                if not player_clue :
                    owner_role_id = None
                    is_open = False
                else:
                    player_clue = player_clue[0]
                    owner_role_id = player_clue.player_id
                    is_open = player_clue.is_public
                cur_data = {
                    "clue_id":all_clue[i].clue_id,
                    "owner_role_id":owner_role_id,
                    "open":is_open
                }
                data.append(cur_data)
            response['data'] = data
        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
    return JsonResponse(response)


def public_clue(request):
    if request.method == 'POST':
        response = {}
        error = None

        req = json.loads(request.body)
        room_id = req['room_id']        
        clue_id = req['clue_id']

        # check if clue id is correct
        find_clue = models.Clue.objects.filter(clue_id = clue_id)
        if not find_clue:
            error = 'No such clue'
        else:
            find_clue = find_clue[0]
            cur_player_clue = models.PlayerClue.objects.filter(clue_id = clue_id)[0]
            cur_player_clue.is_public = 1
            cur_player_clue.save()

        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
        return JsonResponse(response)


def send_msg(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        room_id = req['room_id']
        player_id = req['player_id']
        message = req['message']
        
        room = models.Room.objects.get(room_id=room_id)
        player = models.Player.objects.get(player_id=player_id)

        if not room:
            error = 'no such room'
        elif not player:
            error = 'no such player'
        else:
            dlg_id = 0
            dialogue = models.Dialogue.objects.get(dialogue_id=dlg_id)
            while dialogue:
                dlg_id += 1
                dialogue = models.Dialogue.objects.get(dialogue_id=dlg_id)
            dialogue = models.Dialogue.objects.create(dialogue_id=dlg_id, content=message, 
                                                      room=room, player=player)
        
        if error is None:
            response['error_num'] = 0
        else:
            response['error_num'] = 1
            response['msg'] = error
        return JsonResponse(response)


def synchronize(request):
    if request.method == 'POST':
        response = {}
        error = None
        req = json.loads(request.body)
        room_id = req['room_id']
        player_id = req['player_id']
        ready_tag = req['ready_tag']

        room = models.Room.objects.get(room_id=room_id)
        player = models.Player.objects.get(player_id=player_id, room_id=room_id)

        if not room:
            error = 'no such room'
        elif not player:
            error = 'no such player'
        else:
            assert player.ready_status == ready_tag - 1
            player.ready(ready_tag)
            player_list = models.Player.objects.filter(room_id=room_id)

            ready_list = [ply for ply in player_list if ply.ready_status >= ready_tag]
        
        if error is None:
            data = {
                'player_num': len(player_list),
                'ready_player_num': len(ready_list)
            }
            response['error_num'] = 0
            response['data'] = data
        else:
            response['error_num'] = 1
            response['msg'] = error
        return JsonResponse(response)

