import math
import config


def get_random_pokemon(cur):
    pokemon = cur.execute('SELECT * FROM pokemons ORDER BY RANDOM() LIMIT 1;').fetchone()
    return pokemon


def get_range_level_pokemon(cur, ability_num):
    pokemon = cur.execute("SELECT * FROM pokemons WHERE hp < {} ORDER BY RANDOM() LIMIT 1 ".format(ability_num)).fetchone()
    return pokemon


def catch_pokemon(con, cur, pokemon_dict, user_id):
    del pokemon_dict['id']
    pokemon_dict['owner_id'] = user_id
    cur.execute(
        "INSERT or REPLACE into own_pokemons ({}) VALUES ({})".format(
            ','.join(pokemon_dict.keys()), ','.join(['?'] * len(pokemon_dict.keys()))),
        tuple(pokemon_dict.values())
    )
    con.commit()


def check_pokemon(cur, user_id):
    result = cur.execute(
        'SELECT * from own_pokemons WHERE owner_id == {}'.format(
            user_id)).fetchall()
    return result


def count_pokemon_ability(pokemon_dict, lv):
    pokemon_dict['hp'] = int(pokemon_dict['hp'] * (math.sqrt(lv)*0.15 + 1))
    pokemon_dict['str'] = int(pokemon_dict['str'] * (math.sqrt(lv)*0.15 + 1))
    pokemon_dict['def'] = int(pokemon_dict['def'] * (math.sqrt(lv)*0.15 + 1))
    pokemon_dict['speed'] = int(pokemon_dict['speed'] * (math.sqrt(lv) * 0.15 + 1))
    pokemon_dict['tg'] = int(pokemon_dict['tg'] * (math.sqrt(lv) * 0.15 + 1))
    pokemon_dict['tf'] = int(pokemon_dict['tf'] * (math.sqrt(lv) * 0.15 + 1))
    pokemon_dict['lv'] = lv
    return pokemon_dict


def get_event(cur, user_id):
    events = cur.execute(
        "SELECT * FROM event WHERE owner_id == {}".format(user_id)).fetchone()
    return events


def write_event(con, cur, user_id, pokemon_dict, update):
    if not update:
        del pokemon_dict['id']
        pokemon_dict['owner_id'] = user_id
        pokemon_dict['use_pokemon_id'] = ''
        cur.execute(
            "INSERT or REPLACE into event ({}) VALUES ({})".format(
                ','.join(pokemon_dict.keys()), ','.join(['?'] * len(pokemon_dict.keys()))),
            tuple(pokemon_dict.values())
        )
        con.commit()
    else:
        cur.execute(
            "INSERT or REPLACE into event ({}) VALUES ({})".format(
                ','.join(pokemon_dict.keys()), ','.join(['?'] * len(pokemon_dict.keys()))),
            tuple(pokemon_dict.values())
        )
        con.commit()


def delete_event(con, cur, event_id):
    cur.execute(
        "DELETE  FROM event WHERE id == {}".format(event_id))
    con.commit()


def delete_pokemon(con,cur, pokemon_id):
    cur.execute(
        "DELETE  FROM own_pokemons WHERE id == {}".format(pokemon_id))
    con.commit()


def cause_damage(strength, defense):
    damage = strength - defense
    damage = damage if damage > 0 else 1
    return damage


def level_up_ablity(pokemon_dict, origin_lv, lv):
    all_abil = sum([pokemon_dict['hp'], pokemon_dict['str'], pokemon_dict['def'],
                    pokemon_dict['speed'], pokemon_dict['tg'], pokemon_dict['tf']])
    high_balance = 2 if lv < 50 else (1/math.loglp(lv))
    minus_lv = lv - origin_lv
    pokemon_dict['hp'] = pokemon_dict['hp'] + (int((pokemon_dict['hp']/all_abil) * 10 * high_balance) * minus_lv)
    pokemon_dict['str'] = pokemon_dict['str'] + (int((pokemon_dict['str']/all_abil) * 10 * high_balance) * minus_lv)
    pokemon_dict['def'] = pokemon_dict['def'] + (int((pokemon_dict['def']/all_abil) * 10 * high_balance) * minus_lv)
    pokemon_dict['speed'] = pokemon_dict['speed'] + (int((pokemon_dict['speed']/all_abil) * 10 * high_balance) * minus_lv)
    pokemon_dict['tg'] = pokemon_dict['tg'] + (int((pokemon_dict['tg']/all_abil) * 10 * high_balance) * minus_lv)
    pokemon_dict['tf'] = pokemon_dict['tf'] + (int((pokemon_dict['tf']/all_abil) * 10 * high_balance) * minus_lv)
    return pokemon_dict


# def check_evolve(con, cur, pokemon_info_dict):
#


def get_exp(con, cur, pokemon_info_dict, get_exp, exp_record, exp_dict):
    if not exp_record:
        exp = (30 * pokemon_info_dict['lv']) + get_exp
        poke_exp_dict = {'own_pokemon_id': pokemon_info_dict['id'], 'exp': exp}
        cur.execute(
            "INSERT or REPLACE into pokemon_exp ({}) VALUES ({})".format(
                ','.join(poke_exp_dict.keys()), ','.join(['?'] * len(poke_exp_dict.keys()))),
            tuple(poke_exp_dict.values())
        )
        con.commit()
        return None
    else:
        exp_dict['exp'] = exp_dict['exp'] + get_exp
        cur.execute(
            "INSERT or REPLACE into pokemon_exp ({}) VALUES ({})".format(
                ','.join(exp_dict.keys()), ','.join(['?'] * len(exp_dict.keys()))),
            tuple(exp_dict.values())
        )
        con.commit()
        if int(exp_dict['exp'] / 30) > pokemon_info_dict['lv']:
            pokemon_info_dict = level_up_ablity(pokemon_info_dict, pokemon_info_dict['lv'], int(exp_dict['exp'] / 30))
            pokemon_info_dict['lv'] = int(exp_dict['exp'] / 30)
            cur.execute(
                "INSERT or REPLACE into own_pokemons ({}) VALUES ({})".format(
                    ','.join(pokemon_info_dict.keys()), ','.join(['?'] * len(pokemon_info_dict.keys()))),
                tuple(pokemon_info_dict.values())
            )
            con.commit()
            return int(exp_dict['exp'] / 30)


# Message Area
def walk_around_message(pokemon_dict):
    message = "你到處走動，遇到了這隻寶可夢！\n他的資訊是：{}　\n您要派出哪一隻神奇寶貝去對戰呢？ 請輸入神奇寶貝id。(可以使用/check_my_pokemon查詢)".format(
        '\n'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()])
    )
    response_dict = {'text': message, 'attachments': [{'image_url': pokemon_dict['picture']}], "mrkdwn": 'true'}
    return response_dict


def no_account_notice():
    response_dict = {"text":"請先建立玩家喔！", "mrkdwn": 'true' }
    return response_dict


def no_pokemon_notice():
    response_dict = {"text": "請至少擁有一隻寶可夢，再來進行喔！（/catch_first_pokemon）", "mrkdwn": 'true'}
    return response_dict


def battle_message(result_type, my_pokemon_name, enemy_name):
    if result_type == 'even':
        message = "你的 *{}* 跟 *{}* 打成平手！！！".format(my_pokemon_name, enemy_name)
    elif result_type == 'beat':
        message = "你的 *{}* 被 *{}* 打敗了，請多去訓練！！！".format(my_pokemon_name, enemy_name)
    else:
        message = "Error"
    response_dict = {'text': message, "mrkdwn": 'true'}
    return response_dict


def battle_exp_message(lv_up, my_pokemon_name, enemy_name, exp_dict, lv=None):
    if lv_up:
        message = "你的 *{}* 打贏了 *{}*！！！ 獲得 *{}* 經驗值，恭喜你的*{}*升到 *{}* 等。 exp:{}/{}".format(
            my_pokemon_name, enemy_name, config.enemy_basic_exp, my_pokemon_name, lv_up, exp_dict['exp'], (lv_up+1) * 30
        )
    else:
        message = "你的 *{}* 打贏了 *{}*！！！ 獲得 *{}* 經驗值。 exp: {}/{}".format(
            my_pokemon_name, enemy_name, config.enemy_basic_exp, exp_dict['exp'], (lv+1) * 30
        )
    response_dict = {'text': message, "mrkdwn": 'true'}
    return response_dict


def catch_message(get):
    if get:
        message = "你投擲出了:pokeball: \n 恭喜您，您成功捕捉了！"
    else:
        message = "你投擲出了:pokeball: \n 很可惜，他從寶貝球中逃跑了"
    response_dict = {"text": message, "mrkdwn": 'true'}
    return response_dict
