import sqlite3 as sql
import math

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
    pokemon_dict['hp'] = int(pokemon_dict['hp'] * (math.sqrt(lv)*0.1 + 1))
    pokemon_dict['str'] = int(pokemon_dict['str'] * (math.sqrt(lv)*0.1 + 1))
    pokemon_dict['def'] = int(pokemon_dict['def'] * (math.sqrt(lv)*0.1 + 1))
    pokemon_dict['speed'] = int(pokemon_dict['speed'] * (math.sqrt(lv) * 0.1 + 1))
    pokemon_dict['tg'] = int(pokemon_dict['tg'] * (math.sqrt(lv) * 0.1 + 1))
    pokemon_dict['tf'] = int(pokemon_dict['tf'] * (math.sqrt(lv) * 0.1 + 1))
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


def cause_damage(str, defense):
    damage = str - defense
    damage = damage if damage > 0 else 1
    return damage