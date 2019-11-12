from typing import Dict, Any, Union

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
        help_message = "====新手教學====\n  - 訓練家您好，新加入玩家可以先使用/create_player建立帳號，會自己抓取您的slack暱稱作為帳號。\n " \
                       "- 接著您可以使用/catch_first_pokemon獲得您的第一隻寶可夢 \n - 使用/check_my_pokemon可以查看目前手上寶可夢狀況" \
                       "\n - 使用/walk_around 可以進行遇怪，並且繼續使用/walk_around加上您要出戰的寶可夢id，並跟著提示的指令輸入相對應的動作代碼，即可完成捕捉或是打怪\n" \
                       "任何疑問歡迎提出！！祝您遊玩順利"
        return jsonify({"text": help_message, "mrkdwn": 'true'})


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
            output_message = '\n=============\n:pokeball:'.join(['\n'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]) for pokemon_dict in dict_lst])
            return jsonify({"text":"您的神奇寶貝如下，他們的資訊是：\n{}".format(output_message)
                            , "mrkdwn": 'true'
                            })
        else:
            return jsonify(no_account_notice())


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
            return jsonify(no_account_notice())


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
            return jsonify({'text':"你已經獲得你的第一隻寶可夢囉！\n他的資訊是：\n{}".format('　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]))
                    , 'attachments':[{'image_url': pokemon_dict['picture']}]
                    , "mrkdwn": 'true'})
        else:
            return jsonify(no_account_notice())


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
            own_pokemons_dict = [dict(zip([c[0] for c in cur.description], p)) if p else '' for p in own_pokemons]
            if own_pokemons:
                now_event = get_event(cur, user_id)
                if not now_event:
                    max_hp = sorted(own_pokemons, key=lambda x: x[4], reverse=True)[0][4]
                    max_lv = sorted(own_pokemons, key=lambda x: x[10], reverse=True)[0][10]
                    from_num = max_lv - 5
                    end_num = max_lv + 5
                    from_num = from_num if from_num > 0 else 1
                    random_enemy = get_range_level_pokemon(cur, max_hp)
                    pokemon_dict = dict(zip([c[0] for c in cur.description], random_enemy))
                    pokemon_dict = count_pokemon_ability(pokemon_dict, random.randint(from_num,end_num))
                    response_dict = walk_around_message(pokemon_dict)
                    write_event(con, cur, user_id, pokemon_dict, update=False)
                    return jsonify(response_dict)
                else:
                    event_dict: Dict[Union[str, Any], Union[int, Any]] = dict(
                        zip([c[0] for c in cur.description], now_event))
                    if not now_event[1]:
                        # choose pokemon
                        if request.form['text'] in [str(p[0]) for p in own_pokemons]:
                            choosed_pokemon = [p for p in own_pokemons if str(p[0]) == request.form['text']][0]
                            event_dict['use_pokemon_id'] = int(request.form['text'])
                            event_dict['use_pokemon_hp'] = choosed_pokemon[4]
                            event_dict['origin_hp'] = event_dict['hp']
                            write_event(con, cur, user_id, event_dict, update=True)
                            return jsonify({"text": "您挑選的神奇寶貝是 {} ,等級是 {}。\n 去吧！　:pokeball:　\n準備開始戰鬥！ \n 請選擇；\n攻擊（a）、特殊攻擊(s)、捕捉(c)、逃跑(r)".format(
                                choosed_pokemon[3], choosed_pokemon[10]), 'attachments': [{'image_url': choosed_pokemon[2]}], "mrkdwn": 'true'})
                        else:
                            return jsonify("你沒有這個id的寶可夢喔！")
                    else:
                        # 進入回合制戰鬥
                        choosed_pokemon = [p for p in own_pokemons if p[0] == event_dict['use_pokemon_id']][0]
                        choosed_pokemon_dict = [p for p in own_pokemons_dict if p['id'] == event_dict['use_pokemon_id']][0]
                        exp_record = cur.execute(
                            "SELECT * from pokemon_exp WHERE own_pokemon_id == {}".format(choosed_pokemon[0])).fetchone()
                        exp_dict = dict(zip([c[0] for c in cur.description], exp_record)) if exp_record else ''
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
                                    return jsonify(catch_message(get))
                                else:
                                    delete_event(con, cur, event_id)
                                    return jsonify(catch_message(get))
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
                                return jsonify({"text":"你的寶可夢 *{}* 用普通攻擊:punch: 對 對方 造成了 *{}* 點傷害\n對方 *{}* 用普通攻擊:punch: 同時也對你造成了 *{}* 點傷害。"
                                               "\n你的寶可夢 *{}* 剩下 *{}* hp \n對方 *{}* 剩下 *{}* hp".format(choosed_pokemon[3], enemy_damge,
                                                                                          event_dict['name'],
                                                                                          my_damage, choosed_pokemon[3],event_dict['use_pokemon_hp'], event_dict['name'], event_dict['hp']), "mrkdwn": 'true'})
                            elif event_dict['hp'] <= 0 and event_dict['use_pokemon_hp'] <= 0:
                                delete_event(con, cur, event_id)
                                return jsonify(battle_message("even", choosed_pokemon[3], event_dict['name']))
                            elif event_dict['hp'] <= 0:
                                delete_event(con, cur, event_id)
                                lv_up = get_exp(con, cur, choosed_pokemon_dict, 15, exp_record, exp_dict)
                                if lv_up:
                                    return jsonify(battle_exp_message(lv_up, choosed_pokemon[3], event_dict['name'], exp_dict))
                                else:
                                    if not exp_dict:
                                        exp_dict = {'exp': (choosed_pokemon[10]) * 30 + 15}
                                    return jsonify(battle_exp_message(lv_up, choosed_pokemon[3], event_dict['name'], exp_dict, choosed_pokemon[10]))
                            else:
                                delete_event(con, cur, event_id)
                                return jsonify(battle_message("beat", choosed_pokemon[3], event_dict['name']))
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
                                return jsonify({"text":"你的寶可夢 *{}* 利用特殊攻擊:boom: 對 對方 造成了 *{}* 點傷害。\n對方 *{}* 用特殊攻擊:boom: 同時也對你造成了 *{}* 點傷害。"
                                               "\n你的寶可夢 *{}* 剩下 *{}* hp \n對方 *{}* 剩下 *{}* hp".format(choosed_pokemon[3], enemy_damge,
                                                                                          event_dict['name'], my_damage, choosed_pokemon[3],
                                                                                          event_dict['use_pokemon_hp'], event_dict['name'], event_dict['hp']), "mrkdwn": 'true'})
                            elif event_dict['hp'] <= 0 and event_dict['use_pokemon_hp'] <= 0:
                                delete_event(con, cur, event_id)
                                return jsonify(battle_message("even", choosed_pokemon[3], event_dict['name']))
                            elif event_dict['hp'] <= 0:
                                delete_event(con, cur, event_id)
                                lv_up = get_exp(con, cur, choosed_pokemon_dict, 15, exp_record, exp_dict)
                                if lv_up:
                                    return jsonify(battle_exp_message(lv_up, choosed_pokemon[3], event_dict['name'], exp_dict))
                                else:
                                    if not exp_dict:
                                        exp_dict = {'exp': (choosed_pokemon[10]) * 30 + 15}
                                    return jsonify(battle_exp_message(lv_up, choosed_pokemon[3], event_dict['name'], exp_dict, choosed_pokemon[10]))
                            else:
                                delete_event(con, cur, event_id)
                                return jsonify(battle_message("beat", choosed_pokemon[3], event_dict['name']))
                        else:
                            return jsonify("沒有這個指令喔！")
            else:
                return jsonify(no_pokemon_notice())
        else:
            return jsonify(no_account_notice())

@app.route('/world_boss', methods=['POST'])
def world_boss():
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
