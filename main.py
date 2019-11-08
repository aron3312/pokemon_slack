from flask import Flask
from flask import request
from flask import jsonify
from utils import catch_pokemon, get_random_pokemon, check_pokemon, get_range_level_pokemon, count_pokemon_ability
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
                max_hp = sorted(own_pokemons, key=lambda x:x[4], reverse=True)[0][4]
                max_lv = sorted(own_pokemons, key=lambda x:x[10], reverse=True)[0][10]
                from_num = max_lv - 5
                end_num = max_lv + 5
                from_num = from_num if from_num > 0 else 1
                random_enemy = get_range_level_pokemon(cur, max_hp)
                pokemon_dict = dict(zip([c[0] for c in cur.description], random_enemy))
                pokemon_dict = count_pokemon_ability(pokemon_dict, random.randint(from_num,end_num))
                response_dict = {'text':"你到處走動，遇到了這隻寶可夢！\n他的資訊是：{}".format(
                    '　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]))
                , 'attachments':[{'image_url': pokemon_dict['picture']}]
                }
                return jsonify(response_dict)
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
