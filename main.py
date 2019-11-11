from flask import Flask
from flask import request
from flask import jsonify
from utils import *
import sqlite3 as sql
import random
import requests
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/help', methods=['POST'])
def help():
    if request.method == 'POST':
        help_message = "訓練家您好，請輸入/create_player 以建立您的帳號"
        return jsonify(help_message)


@app.route('/create_player', methods=['POST'])
def create_player():
    if request.method == 'POST':
        con = sql.connect('record.db')
        cur = con.cursor()
        existed_user = set([p[0] for p in cur.execute("SELECT name from player").fetchall()])
        if request.form['user_name'] not in existed_user:
            user_dict = {'name':request.form['user_name'], 'lv':1}
            cur.execute(
                "INSERT or REPLACE into player ({}) VALUES ({})".format(
                    ','.join(user_dict.keys()), ','.join(['?'] * len(user_dict.keys()))),
                                tuple(user_dict.values())
            )
            con.commit()
            success_message = "創建成功 您可以開啟您的訓練之旅"
            return jsonify(success_message)
        else:
            message_dict = {'text': "這個訓練家已存在，請直接遊玩"}
            return jsonify(message_dict)


@app.route('/check_my_pokemon', methods=['POST'])
def check_my_pokemon():
    if request.method == 'POST':
        print(request.form)
        con = sql.connect('record.db')
        cur = con.cursor()
        users = [p for p in cur.execute("SELECT id,name from player").fetchall()]
        existed_user = set([p[1] for p in users])
        if request.form['user_name']in existed_user:
            user_id = [p[0] for p in users if p[1] == request.form['user_name']][0]
            own_pokemon = check_pokemon(cur, user_id)
            dict_lst = [dict(zip([c[0] for c in cur.description], p)) for p in own_pokemon]
            output_message = '===================='.join(['　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]) for pokemon_dict in dict_lst])
            return jsonify("您的神奇寶貝如下，他們的資訊是：{}".format(output_message))
        else:
            return jsonify("請先建立玩家喔！")


@app.route('/release', methods=['POST'])
def release_pokemon():
    if request.method == 'POST':
        print(request.form)
        con = sql.connect('record.db')
        cur = con.cursor()
        users = [p for p in cur.execute("SELECT id,name from player").fetchall()]
        existed_user = set([p[1] for p in users])
        if request.form['user_name']in existed_user:
            user_id = [p[0] for p in users if p[1] == request.form['user_name']][0]
            own_pokemons = check_pokemon(cur, user_id)
            if request.form['text'] in [str(p[0]) for p in own_pokemons]:
                choosed_pokemon = [p for p in own_pokemons if str(p[0]) == request.form['text']][0]
                delete_pokemon(con, cur, choosed_pokemon[0])
                return jsonify("你已經讓 {} 回到他的棲息地了！".format(choosed_pokemon[3]))
            else:
                return jsonify("你沒有這個id的寶可夢喔！")
        else:
            return jsonify("請先建立玩家喔！")

@app.route('/catch_first_pokemon', methods=['POST'])
def catch_first_pokemon():
    if request.method == 'POST':
        con = sql.connect('record.db')
        cur = con.cursor()
        users = [p for p in cur.execute("SELECT id,name from player").fetchall()]
        existed_user = set([p[1] for p in users])
        if request.form['user_name'] in existed_user:
            user_id = [p[0] for p in users if p[1] == request.form['user_name']][0]
            if cur.execute('SELECT player.name, own_pokemons.name from player, own_pokemons WHERE own_pokemons.owner_id == {}'.format(user_id)).fetchall():
                return jsonify('你已經有寶可夢囉！')
            else:
                pokemon = get_random_pokemon(cur)
                pokemon_dict = dict(zip([c[0] for c in cur.description], pokemon))
                rowDict = dict(zip([c[0] for c in cur.description], pokemon))
                catch_pokemon(con, cur, rowDict, user_id)
            return jsonify("你已經獲得你的第一隻寶可夢囉！\n他的資訊是：{}".format('　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()])))
        else:
            return jsonify("請先建立玩家喔！")


@app.route('/walk_around', methods=['POST'])
def walk_around():
    if request.method == 'POST':
        con = sql.connect('record.db')
        cur = con.cursor()
        users = [p for p in cur.execute("SELECT id,name from player").fetchall()]
        existed_user = set([p[1] for p in users])
        if request.form['user_name'] in existed_user:
            user_id = [p[0] for p in users if p[1] == request.form['user_name']][0]
            own_pokemons = check_pokemon(cur, user_id)
            if own_pokemons:
                now_event = get_event(cur, user_id)
                if not now_event:
                    max_hp = sorted(own_pokemons, key=lambda x:x[4], reverse=True)[0][4]
                    max_lv = sorted(own_pokemons, key=lambda x:x[10], reverse=True)[0][10]
                    from_num = max_lv - 5
                    end_num = max_lv + 5
                    from_num = from_num if from_num > 0 else 1
                    random_enemy = get_range_level_pokemon(cur, max_hp)
                    pokemon_dict = dict(zip([c[0] for c in cur.description], random_enemy))
                    pokemon_dict = count_pokemon_ability(pokemon_dict, random.randint(from_num,end_num))
                    response_dict = {'text':"你到處走動，遇到了這隻寶可夢！\n他的資訊是：{}　您要派出哪一隻神奇寶貝去對戰呢？ 請輸入神奇寶貝id".format(
                        '　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]))
                    , 'attachments':[{'image_url': pokemon_dict['picture']}]
                    }
                    write_event(con, cur, user_id, pokemon_dict, update=False)
                    return jsonify(response_dict)
                else:
                    event_dict = dict(zip([c[0] for c in cur.description], now_event))
                    if not now_event[1]:
                        # choose pokemon
                        if request.form['text'] in [str(p[0]) for p in own_pokemons]:
                            choosed_pokemon = [p for p in own_pokemons if str(p[0]) == request.form['text']][0]
                            event_dict['use_pokemon_id'] = int(request.form['text'])
                            event_dict['use_pokemon_hp'] = choosed_pokemon[4]
                            event_dict['origin_hp'] = event_dict['hp']
                            write_event(con, cur, user_id , event_dict, update=True)
                            return jsonify({"text":"您挑選的神奇寶貝是 {} ,等級是 {}　準備開始戰鬥！ 請選擇；攻擊（a）、特殊攻擊(s)、捕捉(c)、逃跑(r)".format(choosed_pokemon[3], choosed_pokemon[10]), 'attachments':[{'image_url': choosed_pokemon[2]}]})
                        else:
                            return jsonify("你沒有這個id的寶可夢喔！")
                    else:
                        # 進入回合制戰鬥
                        choosed_pokemon = [p for p in own_pokemons if p[0] == event_dict['use_pokemon_id']][0]
                        if request.form['text'] == 'r':
                            delete_event(con, cur, event_dict['id'])
                            return jsonify("您已成功逃脫！")
                        elif request.form['text'] == 'c':
                            if len(own_pokemons) < 6:
                                last_hp = event_dict['hp']
                                del event_dict['use_pokemon_id']
                                del event_dict['use_pokemon_hp']
                                event_dict['hp'] = event_dict['origin_hp']
                                del event_dict['origin_hp']
                                event_id = event_dict['id']
                                plus = int((event_dict['hp']/last_hp)/10 + 2)
                                print(plus)
                                random_pick = [True] * (3 + plus) + [False] * 2
                                random.seed(random.randint(0, 9999))
                                get = random_pick[random.randint(0, len(random_pick)-1)]
                                if get:
                                    catch_pokemon(con, cur, event_dict, user_id)
                                    delete_event(con, cur, event_id)
                                    return jsonify("您成功捕捉了！")
                                else:
                                    delete_event(con, cur, event_id)
                                    return jsonify("很可惜，被他跑了！")
                            else:
                                return jsonify("您已擁有六隻寶可夢，無法捕捉")
                        elif request.form['text'] == 'a':
                            event_id = event_dict['id']
                            strength = choosed_pokemon[5]
                            enemy_def = event_dict['def']
                            enemy_str = event_dict['str']
                            defense = choosed_pokemon[6]
                            enemy_damge = cause_damage(strength, enemy_def)
                            my_damage = cause_damage(enemy_str, defense)
                            event_dict['hp'] = event_dict['hp'] - enemy_damge
                            event_dict['use_pokemon_hp'] = event_dict['use_pokemon_hp'] - my_damage
                            write_event(con, cur, user_id, event_dict, True)
                            if event_dict['hp'] > 0 and event_dict['use_pokemon_hp'] > 0:
                                return jsonify("你的寶可夢:{} 用普通攻擊 對 對方 造成了 {} 點傷害，對方 {} 用普通攻擊 同時也對你造成了 {} 點傷害。"
                                               " 你的寶可夢{} 剩下 {} hp ；對方 {} 剩下 {} hp".format(choosed_pokemon[3], enemy_damge,
                                                                                          event_dict['name'], my_damage, choosed_pokemon[3],
                                                                                          event_dict['use_pokemon_hp'], event_dict['name'], event_dict['hp']))
                            elif event_dict['hp'] < 0 and event_dict['use_pokemon_hp'] > 0:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 打贏了 {}！！！".format(choosed_pokemon[3], event_dict['name']))
                            elif event_dict['hp'] > 0 and event_dict['use_pokemon_hp'] < 0:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 被 {} 打敗了，請多去訓練！！！".format(choosed_pokemon[3], event_dict['name']))
                            else:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 跟 {} 打成平手！！！".format(choosed_pokemon[3], event_dict['name']))
                        elif request.form['text'] == 's':
                            event_id = event_dict['id']
                            strength = choosed_pokemon[8]
                            enemy_def = event_dict['tf']
                            enemy_str = event_dict['tg']
                            defense = choosed_pokemon[9]
                            enemy_damge = cause_damage(strength, enemy_def)
                            my_damage = cause_damage(enemy_str, defense)
                            event_dict['hp'] = event_dict['hp'] - enemy_damge
                            event_dict['use_pokemon_hp'] = event_dict['use_pokemon_hp'] - my_damage
                            write_event(con, cur, user_id, event_dict, True)
                            if event_dict['hp'] > 0 and event_dict['use_pokemon_hp'] > 0:
                                return jsonify("你的寶可夢:{} 利用特殊攻擊 對 對方 造成了 {} 點傷害，對方 {} 用特殊攻擊 同時也對你造成了 {} 點傷害。"
                                               " 你的寶可夢{} 剩下 {} hp ；對方 {} 剩下 {} hp".format(choosed_pokemon[3], enemy_damge,
                                                                                          event_dict['name'], my_damage, choosed_pokemon[3],
                                                                                          event_dict['use_pokemon_hp'], event_dict['name'], event_dict['hp']))
                            elif event_dict['hp'] < 0 and event_dict['use_pokemon_hp'] > 0:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 打贏了 {}！！！".format(choosed_pokemon[3], event_dict['name']))
                            elif event_dict['hp'] > 0 and event_dict['use_pokemon_hp'] < 0:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 被 {} 打敗了，請多去訓練！！！".format(choosed_pokemon[3], event_dict['name']))
                            else:
                                delete_event(con, cur, event_id)
                                return jsonify("你的 {} 跟 {} 打成平手！！！".format(choosed_pokemon[3], event_dict['name']))
                        else:
                            return jsonify("開發中")
            else:
                return jsonify('請至少擁有一隻寶可夢，再來進行喔！（/catch_first_pokemon）')
        else:
            return jsonify("請先建立玩家喔！")


@app.route('/pick', methods=['POST'])
def pick():
    if request.method == 'POST':
        con = sql.connect('record.db')
        cur = con.cursor()
        url = "https://hooks.slack.com/services/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"
        pokemon = get_random_pokemon(cur)
        pokemon_dict = dict(zip([c[0] for c in cur.description], pokemon))
        message = {"text":"{},你抽到的寶可夢資訊是：{}".format(request.form['user_name'], '　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]))}
        req = requests.post(url, data=json.dumps(message))
        print(req)
        return "success"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3679)
