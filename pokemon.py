from pydoc import describe
from sqlite3 import Cursor
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
from threading import Timer
import random

load_dotenv()

TOKEN = os.getenv('token')

client = commands.Bot(command_prefix = "-")

global pokemon_data
pokemon_data = pd.read_csv('pokemon.csv')

@client.event
async def on_ready():
    print(f"{client.user} is online")

def database_initialize():

    global pokemon_info
    pokemon_info = pd.read_csv('pokemon.csv')

    conn = psycopg2.connect(
        database=os.getenv('db_name'), user=os.getenv('user'), password=os.getenv('password'), host=os.getenv('host'), port= os.getenv('port')
    )
    conn.autocommit = True
    cursor = conn.cursor()

    create_player = "CREATE TABLE IF NOT EXISTS PLAYER(ID SERIAL NOT NULL PRIMARY KEY, NAME varchar(100), LEVEL int NOT NULL, BADGE int NOT NULL, GENERATION int NOT NULL, BALL varchar(200), MONEY int NOT NULL, STONES varchar(20));"
    aa = cursor.execute(create_player)
    print("Database player created successfully!")

    create_player = "CREATE TABLE IF NOT EXISTS MY_POKEMON(ID SERIAL NOT NULL PRIMARY KEY, NAME varchar(100), POKEMON varchar(2000), POKEDEX varchar(1700));"
    cursor.execute(create_player)
    print("Database pokemon created successfully!")

    return conn, cursor

# completed
@client.command(brief = "start game", aliases=['p'])
async def pokemon(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()

    cursor.execute(f"SELECT * FROM player WHERE name = '{username}';")
    check_player_set = cursor.fetchone()
    if check_player_set:
        await message.send(f"Welcome back {username}")
    else:
        start_journey_embed = discord.Embed(title = "Starting Pokemon Journey", description = "Professor Oak: Welcome to the Pokemon World "+ str(message.author).split("#")[0]+". Now let us choose your starter Pokemon.")
        file = discord.File("image/prof.png", filename="prof.png")
        start_journey_embed.set_thumbnail(url="attachment://prof.png")
        await message.send(file=file, embed=start_journey_embed)

        embed_poke1 = discord.Embed(title = "Balbasaur", description = "Balbasaur is a Grass/Poison-type Pokémon.")
        embed_poke1.set_thumbnail(url = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/001.png")
        await message.send(embed=embed_poke1)

        embed_poke2 = discord.Embed(title = "Squirtle", description = "Squirtle is a Water-type Pokémon.")
        embed_poke2.set_thumbnail(url = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/007.png")
        await message.send(embed=embed_poke2)

        embed_poke3 = discord.Embed(title = "Charmander", description = "Charmander is a Fire-type Pokémon.")
        embed_poke3.set_thumbnail(url = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/004.png")
        await message.send(embed=embed_poke3)

        become_trainer = f"INSERT INTO PLAYER(name, level, badge, generation, ball, money, stones) VALUES ('{username}', 1, 0, 1, '5.0.0.0', 1000, '0-0-0-0');"
        cursor.execute(become_trainer)
        print(f"{username} is registered as trainer.")

        await message.send('Professor Oak: To choose your starter pokemon write "-select <pokemon name>". ')

# completed
@client.command(breif = "choose initial starter pokemon")    
async def select(message, pokename):
    global pokemon_data, gym_le
    
    gym_le = ""
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()    
    cursor.execute(f"SELECT * FROM MY_POKEMON WHERE name = '{username}';")
    check_pokemon_set = cursor.fetchone()
    if check_pokemon_set:
        await message.send("Sorry you can use select only at the begining of the journey.")
    else:
        pokename = pokename.lower()
        pokename = pokename.capitalize()

        if pokename == "Bulbasaur":
            pokenum = 1
        elif pokename == "Squirtle":
            pokenum = 7
        elif pokename == "Charmander":
            pokenum = 4

        
        starter_data = pokemon_data.loc[pokemon_data["Pokemon"]==pokename]
        starter_hp = starter_data["HP"].values[0]
        pokedict1  = f"{pokename},5,0,{starter_hp};"
        pokedex = f"{pokename};"
        starter_move = starter_data["Move 1"].values[0]
        embed_starter = discord.Embed(title = "Congratulations!", description = str(message.author).split("#")[0]+f"! You received {pokename}.")
        embed_starter.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
        embed_starter.add_field(name = "lvl", value="5")
        embed_starter.add_field(name = "Move", value=starter_move)
        await message.send(embed = embed_starter)

        first_pokemon_entry = f"INSERT INTO MY_POKEMON(name, pokemon, pokedex) VALUES ('{username}', '{pokedict1}', '{pokedex}');"
        cursor.execute(first_pokemon_entry)
        print("registered pokemon")

        start_journey_embed_1 = discord.Embed(title = "Professor Oak", description = "Here are some pokeballs and a pokedex for your journey. Good Luck !")
        file = discord.File("image/prof.png", filename="prof.png")
        start_journey_embed_1.set_thumbnail(url="attachment://prof.png")

        await message.send(file=file, embed=start_journey_embed_1)


# incomplete 
@client.command(breif = "search wild pokemon", aliases=['s'])
async def search(message, pokename):
    global wild_level, wild_hp, wild_poke, user_on, gym_le
    gym_le = ""
    
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")
    user_on = username

    wild_poke = pokename

    conn, cursor = database_initialize()
    query1 = f"SELECT * FROM PLAYER WHERE name = '{username}';"
    cursor.execute(query1)
    check_player_set = cursor.fetchone()
    if check_player_set:
        userdata_sql = sqlio.read_sql_query(query1,conn)
        pokename = pokename.lower()
        pokename = pokename.capitalize()
        personal_lvl = userdata_sql["level"].values[0]
        conn.autocommit = True
        pokerange = []
        poke_avoid = [3, 6, 9]
        if personal_lvl <= 10:
            for pr in range(10,22):
                pokerange.append(pr)
                wild_level = random.randrange(3, 5)
        elif personal_lvl <= 20 and personal_lvl > 10:
            for pr in range(22,62):
                pokerange.append(pr)
                wild_level = random.randrange(7, 10)
        elif personal_lvl <= 30 and personal_lvl > 20:
            for pr in range(1, 70):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(10, 15)
        elif personal_lvl <= 40 and personal_lvl > 30:
            for pr in range(1, 90):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(15, 25)
        elif personal_lvl <= 50 and personal_lvl > 40:
            for pr in range(1, 100):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(25, 30)
        elif personal_lvl <= 60 and personal_lvl > 50:
            for pr in range(1, 110):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(25, 35)
        elif personal_lvl <= 70 and personal_lvl > 60:
            for pr in range(1, 120):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(30, 35)
        elif personal_lvl <= 80 and personal_lvl > 70:
            for pr in range(1, 130):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(40, 45)
        elif personal_lvl <= 90 and personal_lvl > 80:
            for pr in range(1, 140):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(45, 50)
        elif personal_lvl > 90:
            for pr in range(1, 152):
                if pr in poke_avoid:
                    pass
                else:
                    pokerange.append(pr)
                    wild_level = random.randrange(70, 80)
            
        find_data = pokemon_data.loc[pokemon_data["Pokemon"]==pokename]
        pokenum = find_data["Nat"].values[0]
        wild_hp = int(int(find_data["HP"].values[0]) * (wild_level/5))
        if pokenum in pokerange:

            global catch_mode
            catch_mode = True

            wild = discord.Embed(title = pokename)
            wild.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
            wild.add_field(name = "lvl", value=wild_level)
            wild.add_field(name = "HP", value=wild_hp)
            await message.send(embed = wild)
        else:
            await message.send("Sorry No luck")

# complete 
@client.command(breif = "find random wild pokemon", aliases=['f'])
async def forest(message):
    global pokename_f, wild_poke, wild_level, wild_hp, user_on, gym_le

    wild_poke=""
    gym_le = ""

    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")
    user_on = username
    
    conn, cursor = database_initialize()
    query1 = f"SELECT * FROM PLAYER WHERE name = '{username}';"
    cursor.execute(query1)
    check_player_set = cursor.fetchone()
    if check_player_set:
        userdata_sql = sqlio.read_sql_query(query1,conn)
        personal_lvl = userdata_sql["level"].values[0]
        conn.autocommit = True
        if personal_lvl < 10:
            pokenum = random.randrange(10,22)
            wild_level = random.randrange(4, 5)
        elif personal_lvl < 20 and personal_lvl >= 10:
            pokenum = random.randrange(23,32)
            wild_level = random.randrange(7, 15)
        elif personal_lvl < 30 and personal_lvl >= 20:
            poke_range = [1, 4, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
            pokenum = random.choice(poke_range)
            wild_level = random.randrange(15, 18)
        elif personal_lvl < 40 and personal_lvl >= 30:
            pokenum = random.randrange(62, 90)
            wild_level = random.randrange(15, 25)
        elif personal_lvl < 50 and personal_lvl >= 40:
            pokenum = random.randrange(90, 110)
            wild_level = random.randrange(25, 35)
        elif personal_lvl < 60 and personal_lvl >= 50:
            pokenum = random.randrange(110, 120)
            wild_level = random.randrange(35, 45)
        elif personal_lvl < 70 and personal_lvl >= 60:
            pokenum = random.randrange(120, 130)
            wild_level = random.randrange(35, 45)
        elif personal_lvl < 80 and personal_lvl >= 70:
            pokenum = random.randrange(130, 140)
            wild_level = random.randrange(35, 45)
        elif personal_lvl < 90 and personal_lvl >= 80:
            pokenum = random.randrange(140, 145)
            wild_level = random.randrange(40, 50)
        elif personal_lvl >= 90:
            pokenum = random.randrange(145, 151)
            wild_level = random.randrange(70, 80)
             

        global catch_mode
        catch_mode = True

        pokedata = pokemon_data.loc[pokemon_data["Nat"] == pokenum]
        pokename_f = pokedata["Pokemon"].values[0]
        wild_hp = int(int(pokedata["HP"].values[0]) * (wild_level/5))
        wild = discord.Embed(title = pokename_f)
        wild_poke = pokename_f
        wild.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
        wild.add_field(name = "lvl", value=wild_level)
        wild.add_field(name = "HP", value= wild_hp)
        await message.send(embed = wild)


# incomplete
@client.command(breif = "choose pokemon to battle")
async def go(message, my_pokename):
    global wild_poke, poke_level, poke_hp, my_poke, mypokemove, user_on, mypokeevol

    mypokemove = []

    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    if user_on == username:
        conn, cursor = database_initialize()
        query1 = f"SELECT * FROM MY_POKEMON WHERE name = '{username}';"
        cursor.execute(query1)
        check_player_set = cursor.fetchone()
        if check_player_set:
            if wild_poke == "":
                pass
            else:
                global catch_mode, battle_mode
                battle_mode = True
                my_pokename = my_pokename.lower()
                my_pokename = my_pokename.capitalize()
                my_poke = my_pokename
                query1 = f"SELECT pokemon FROM MY_POKEMON WHERE name = '{username}';"
                userdata_sql = sqlio.read_sql_query(query1,conn)
                each_poke_data = userdata_sql.values[0][0].split(";")
                for pokes in each_poke_data:
                    if pokes.__contains__(my_pokename):
                        poke_data_user = pokes.split(",")
                        poke_level = int(poke_data_user[1])
                        poke_exp = poke_data_user[2]
                        poke_hp = int(poke_data_user[3])
                        if poke_hp > 0:
                            find_data = pokemon_data.loc[pokemon_data["Pokemon"]==my_pokename]
                            pokenum = find_data["Nat"].values[0]

                            mypokemove1 = find_data["Move 1"].values[0]
                            mypokemove2 = find_data["Move 2"].values[0]
                            mypokemove3 = find_data["Move 3"].values[0]
                            mypokemove4 = find_data["Move 4"].values[0]
                            mypokeevol = find_data["Evolution"].values[0]

                            if poke_level < 6:
                                mypokemove = [mypokemove1]
                            
                            if poke_level >= 6:
                                mypokemove = [mypokemove1, mypokemove2]
                            
                            if poke_level > 9:
                                mypokemove = [mypokemove1, mypokemove2, mypokemove3]
                            
                            if poke_level > 11:
                                mypokemove = [mypokemove1, mypokemove2, mypokemove3, mypokemove4]

                            embed_starter = discord.Embed(title = my_pokename)
                            embed_starter.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                            embed_starter.add_field(name = "lvl", value = poke_level)
                            embed_starter.add_field(name = "EXP", value = poke_exp)
                            embed_starter.add_field(name = "HP", value= poke_hp)
                            embed_starter.add_field(name = "Moves", value= mypokemove)
                            await message.send(embed = embed_starter)
                        else:
                            await message.send("Your Pokemon is in no condition for battle. -heal to recover")
    else:
        await message.send("You're not in this battle.")

# incomplete
@client.command(breif = "gym leaders list")
async def use(message, move1, move2=""):
    global my_poke, wild_poke, poke_hp, wild_hp, poke_level, pokemon_data, catch_mode, battle_mode, mypokemove, gym_le, mypokeevol
    move1 = move1.lower()
    move2 = move2.lower()
    move1 = move1.capitalize()
    move2 = move2.capitalize()

    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    if battle_mode:
        if my_poke != "":
            battle_info = pd.read_csv("moves.csv")
            weakness_info = pd.read_csv("type_weakness.csv")
            move = f"{move1} {move2}"
            move = move.strip()

            move_info = battle_info.loc[battle_info["Name"]== move]
            move_kind = move_info["Kind"].values[0]
            move_power = int(move_info["Power"].values[0])

            pokedata2 = pokemon_data.loc[pokemon_data["Pokemon"] == my_poke]
            pokenum2 = pokedata2["Nat"].values[0]
            pokeatk = int(pokedata2["Atk"].values[0])
            pokedef = int(pokedata2["Def"].values[0])

            pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == wild_poke]
            pokenum = pokedata["Nat"].values[0]
            wildatk = int(pokedata["Atk"].values[0])
            wilddef = int(pokedata["Def"].values[0])

            pokemove1 = pokedata["Move 1"].values[0]
            pokemove2 = pokedata["Move 2"].values[0]
            pokemove3 = pokedata["Move 3"].values[0]
            pokemove4 = pokedata["Move 4"].values[0]
            
            if wild_level < 5:
                pokemove = [pokemove1]
            
            if wild_level > 7:
                pokemove = [pokemove1, pokemove2]
            
            if wild_level > 9:
                pokemove = [pokemove1, pokemove2, pokemove3]
            
            if wild_level > 11:
                pokemove = [pokemove1, pokemove2, pokemove3, pokemove4]

            wild_move = random.choice(pokemove)

            move_info2 = battle_info.loc[battle_info["Name"]== wild_move]
            move_kind2 = move_info2["Kind"].values[0]
            move_power2 = int(move_info2["Power"].values[0])
            
            if move in mypokemove:
                wild_hp = int(int(wild_hp) - ((((2*int(poke_level))/5)+2)*move_power*(pokeatk/wilddef)/12))
                await message.send(f"{my_poke} used {move1} {move2}")
                
                if wild_hp < 1:
                    await message.send(f"{wild_poke} fainted.")
                    conn, cursor = database_initialize()
                    if gym_le == "":
                        query1 = f"SELECT pokemon, pokedex FROM MY_POKEMON WHERE name = '{username}';"
                        userdata_sql = sqlio.read_sql_query(query1,conn)
                        pokedex = userdata_sql["pokedex"].values[0]
                        pokeda = userdata_sql["pokemon"].values[0]
                        each_poke_data = pokeda.split(";")
                        pokedict1_add = ""
                        for pokes in each_poke_data:
                            if pokes.__contains__(my_poke):
                                poke_data_user = pokes.split(",")
                                if poke_data_user[0] == my_poke:
                                    poke_data_user[2] = round(int(int(poke_data_user[2])+((100/poke_level)*wild_level)))
                                    if poke_data_user[2]>=100:
                                        poke_data_user[1] = round(int(int(poke_data_user[1])+1))
                                        poke_data_user[2] = 0
                                if mypokeevol == "No Evolution":
                                    pass
                                elif mypokeevol == "Fire Stone":
                                    pass
                                elif mypokeevol == "Water Stone":
                                    pass
                                elif mypokeevol == "Thunder Stone":
                                    pass
                                else:
                                    mypokeevol = int(mypokeevol)
                                    if mypokeevol <= int(poke_data_user[1]):
                                        evolution_chart = pd.read_csv("evolution.csv")
                                        mypokeevolutione1 = evolution_chart.loc[evolution_chart["e1"]==my_poke]
                                        mypokeevolutione2 = evolution_chart.loc[evolution_chart["e2"]==my_poke]
                                        print(mypokeevolutione1)
                                        mypokeevolution_e1 = mypokeevolutione1["e1"].values[0]
                                        if mypokeevolution_e1 == my_poke:
                                            poke_data_user[0] = mypokeevolutione1["e2"].values[0]
                                            print(poke_data_user[0])
                                        else:
                                            mypokeevolution_e2 = mypokeevolutione2["e2"].values[0]
                                            if mypokeevolution_e2 == my_poke:
                                                poke_data_user[0] = mypokeevolutione2["e3"].values[0] 
                                        new_poke_evol = poke_data_user[0]
                                        new_poke_evol_data = pokemon_data.loc[pokemon_data["Pokemon"]==new_poke_evol]
                                        pokenum = new_poke_evol_data["Nat"].values[0]
                                        evolution = discord.Embed(title= f"Your {my_poke} evolved into {poke_data_user[0]}.")
                                        evolution.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                                        await message.send(embed=evolution)
                                        
                                if poke_hp < 0:
                                    poke_hp = 0
                                poke_data_user[3]=poke_hp 
                                pokedict1_add = pokedict1_add + f"{poke_data_user};"
                            else:
                                pokedict1_add = pokedict1_add + pokes+";"
                        pokedict1_add = pokedict1_add.replace("[","")
                        pokedict1_add = pokedict1_add.replace("]","")
                        pokedict1_add = pokedict1_add.replace("'","")
                        pokedict1_add = pokedict1_add.replace(" ","")
                        catch_mode = False
                        battle_mode = False
                        wild_poke = ''
                        
                        pokedict1_add = pokedict1_add.replace(";;",";")
                        pokedex_add = pokedex + f"{wild_poke};"
                        update_query = f"UPDATE MY_POKEMON SET pokemon = '{pokedict1_add}', pokedex = '{pokedex_add}' WHERE name = '{username}';"
                        cursor.execute(update_query)
                    else:
                        gym_name = gym_le.lower()
                        gym_le_em = discord.Embed(title = f'{gym_le}', description = "You're Good. Here take the badge.")
                        file = discord.File(f"image/{gym_name}.png", filename=f"{gym_name}.png")
                        gym_le_em.set_thumbnail(url=f"attachment://{gym_name}.png")
                        await message.send(file = file, embed = gym_le_em)
                        query09 = f"SELECT badge,money,level FROM PLAYER WHERE name = '{username}';"
                        userdata_sql = sqlio.read_sql_query(query09,conn)
                        money = int(userdata_sql["money"].values[0])
                        badge = int(userdata_sql["badge"].values[0])
                        print(badge)
                        personal_lvl = int(userdata_sql["level"].values[0])

                        update_mon_heal = money + 100
                        update_badge = badge + 1
                        update_personal_lvl = personal_lvl + 2

                        update_query2 = f"UPDATE PLAYER SET money = '{update_mon_heal}', level = {update_personal_lvl}, badge = {update_badge} WHERE name = '{username}';"
                        cursor.execute(update_query2)

                        gym_le = ""
                        wild_poke = ""
                        wild_hp = ""
                        battle_mode = False
                else:
                    wild = discord.Embed(title = wild_poke)
                    wild.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                    wild.add_field(name = "lvl", value=wild_level)
                    wild.add_field(name = "HP", value= wild_hp)
                    await message.send(embed = wild)

                    poke_hp = int(int(poke_hp) - ((((2*int(wild_level))/5)+2)*move_power2*(wildatk/pokedef)/12))
                    if gym_le == "":
                        await message.send(f"{wild_poke} used {wild_move}")
                    else:
                        gym_le_em = discord.Embed(title = f'{gym_le}', description = f"{wild_poke} use {wild_move}")
                        gym_name = gym_le.lower()
                        file = discord.File(f"image/{gym_name}.png", filename=f"{gym_name}.png")
                        gym_le_em.set_thumbnail(url=f"attachment://{gym_name}.png")
                        await message.send(file = file, embed = gym_le_em)

                if poke_hp < 1:
                    await message.send(f"{my_poke} fainted.")
                    if gym_le != "":
                        gym_le_em = discord.Embed(title = f'{gym_le}', description = "Such a waste of my time")
                        file = discord.File(f"image/{gym_name}.png", filename=f"{gym_name}.png")
                        gym_le_em.set_thumbnail(url=f"attachment://{gym_name}.png")
                        await message.send(file = file, embed = gym_le_em)
                        gym_le = ""
                        wild_poke = ""
                        wild_hp = ""
                        battle_mode = False
                        
                        query0 = f"SELECT pokemon FROM MY_POKEMON WHERE name = '{username}';"
                        userdata_sql = sqlio.read_sql_query(query0,conn)
                        pokedict1 = userdata_sql["pokemon"].values[0]
                        poke_list = pokedict1.split(";")
                        pokeupstr = ""
                        for pokemon_ in poke_list:
                            pokem = pokemon_.split(",")
                            if len(pokem)>1:
                                pname = pokem[0]
                                poke_level = int(pokem[1])
                                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == pname]
                                pokes_hp = int(int(pokedata["HP"].values[0]) * (poke_level/5))    
                                pokem[3] = pokes_hp
                                pokeupstr = pokeupstr + f"{pokem}"
                        pokeupstr = pokeupstr.replace("[","")
                        pokeupstr = pokeupstr.replace("]",";")
                        pokeupstr = pokeupstr.replace("'","")
                        pokeupstr = pokeupstr.replace(" ","")
                        query09 = f"SELECT money FROM PLAYER WHERE name = '{username}';"
                        userdata_sql = sqlio.read_sql_query(query09,conn)
                        money = int(userdata_sql["money"].values[0])

                        if money < 5:
                            await message.send("Not Enough Money")
                        else:
                            update_query = f"UPDATE MY_POKEMON SET pokemon = '{pokeupstr}' WHERE name = '{username}';"
                            cursor.execute(update_query)

                            update_mon_heal = money - 5

                            update_query2 = f"UPDATE PLAYER SET money = '{update_mon_heal}' WHERE name = '{username}';"
                            cursor.execute(update_query2)
                            pc = discord.Embed(title = "Pokemon Center", description = "Nurse Joy: All your pokemons are healed for $5. Thank You")
                            file = discord.File("image/nursejoy.png", filename="nursejoy.png")
                            pc.set_thumbnail(url="attachment://nursejoy.png")
                            await message.send(file=file, embed=pc)

                if wild_hp > 1 and poke_hp > 1:
                    mp = discord.Embed(title = my_poke)
                    mp.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum2)
                    mp.add_field(name = "lvl", value=poke_level)
                    mp.add_field(name = "HP", value= poke_hp)
                    mp.add_field(name = "Moves", value= mypokemove)
                    await message.send(embed = mp)
                
            else:
                await message.send("Invalid Pokemon Move")
        else:
            await message.send("No poekmon chosen yet.")


# complete
@client.command(breif = "pokeball", aliases = ["pb"])
async def pokeball(message):
    global wild_poke, poke_level, catch_mode, wild_hp, poke_hp, my_poke, pokemon_data, mypokeevol
    
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    query2 = f"SELECT * FROM PLAYER WHERE name = '{username}';"
    userdata_sql12 = sqlio.read_sql_query(query2,conn)
    personal_lvl = int(userdata_sql12["level"].values[0])
    all_pokeball = userdata_sql12["ball"].values[0]
    all_pokeball = all_pokeball.split(".")
    pokeball = int(all_pokeball[0])
    greatball = int(all_pokeball[1])
    ultraball = int(all_pokeball[2])
    masterball = int(all_pokeball[3])
    
    if pokeball>0:        
        if catch_mode:
            if wild_hp <= 20:
                query1 = f"SELECT pokemon, pokedex FROM MY_POKEMON WHERE name = '{username}';"
                userdata_sql = sqlio.read_sql_query(query1,conn)
                pokedex = userdata_sql["pokedex"].values[0]
                pokeda = userdata_sql["pokemon"].values[0]
                each_poke_data = pokeda.split(";")
                pokedict1_add = ""
                for pokes in each_poke_data:
                    if pokes.__contains__(my_poke):
                        poke_data_user = pokes.split(",")
                        if poke_data_user[0] == my_poke:
                            poke_data_user[2] = round(int(int(poke_data_user[2])+((100/poke_level)*wild_level)))
                            if poke_data_user[2]>=100:
                                poke_data_user[1] = round(int(int(poke_data_user[1])+1))
                                poke_data_user[2] = 0
                        if mypokeevol == "No Evolution":
                            pass
                        elif mypokeevol == "Fire Stone":
                            pass
                        elif mypokeevol == "Water Stone":
                            pass
                        elif mypokeevol == "Thunder Stone":
                            pass
                        else:
                            mypokeevol = int(mypokeevol)
                            if mypokeevol <= int(poke_data_user[1]):
                                evolution_chart = pd.read_csv("evolution.csv")
                                mypokeevolutione1 = evolution_chart.loc[evolution_chart["e1"]==my_poke]
                                mypokeevolutione2 = evolution_chart.loc[evolution_chart["e2"]==my_poke]
                                print(mypokeevolutione1)
                                mypokeevolution_e1 = mypokeevolutione1["e1"].values[0]
                                if mypokeevolution_e1 == my_poke:
                                    poke_data_user[0] = mypokeevolutione1["e2"].values[0]
                                    print(poke_data_user[0])
                                else:
                                    mypokeevolution_e2 = mypokeevolutione2["e2"].values[0]
                                    if mypokeevolution_e2 == my_poke:
                                        poke_data_user[0] = mypokeevolutione2["e3"].values[0] 
                                new_poke_evol = poke_data_user[0]
                                new_poke_evol_data = pokemon_data.loc[pokemon_data["Pokemon"]==new_poke_evol]
                                pokenum = new_poke_evol_data["Nat"].values[0]
                                evolution = discord.Embed(title= f"Your {my_poke} evolved into {poke_data_user[0]}.")
                                evolution.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                                await message.send(embed=evolution)
                                
                        if poke_hp < 0:
                            poke_hp = 0
                        poke_data_user[3]=poke_hp 
                        pokedict1_add = pokedict1_add + f"{poke_data_user};"
                    else:
                        pokedict1_add = pokedict1_add + pokes+";"
                pokedict1_add = pokedict1_add.replace("[","")
                pokedict1_add = pokedict1_add.replace("]","")
                pokedict1_add = pokedict1_add.replace("'","")
                pokedict1_add = pokedict1_add.replace(" ","")
                
                if pokeda.__contains__(wild_poke):
                    pass
                else:
                    print(pokedict1_add)
                    pokedict1_add = pokedict1_add.replace(";;",";")
                    pokedict1_add = pokedict1_add + f"{wild_poke},{wild_level},0,{wild_hp};"
                    print(pokedict1_add)
                if pokedex.__contains__(wild_poke):
                    pokedex_add = pokedex
                else:
                    pokedex_add = pokedex + f"{wild_poke};"
                    personal_lvl = personal_lvl + 1
                    update_level = f"UPDATE PLAYER SET level = '{personal_lvl}' WHERE name = '{username}';"
                    cursor.execute(update_level)
                update_query = f"UPDATE MY_POKEMON SET pokemon = '{pokedict1_add}', pokedex = '{pokedex_add}' WHERE name = '{username}';"
                cursor.execute(update_query)
                catch_mode = False
                caught = discord.Embed(title = f"Congratulations!", description = str(message.author).split("#")[0] + f" you caught {wild_poke}")
                caught.set_thumbnail(url="https://c.tenor.com/CpRW4WUGa3IAAAAi/pok%C3%A9ball-pok%C3%A9mon.gif")
                await message.send(embed = caught)

                pokeball = pokeball - 1
                all_pokeball = f"{pokeball}.{greatball}.{ultraball}.{masterball}"
                update_query2 = f"UPDATE PLAYER SET ball = '{all_pokeball}' WHERE name = '{username}';"
                cursor.execute(update_query2)
                print("updated pokeball")


            else:
                await message.send(f"Unlucky, {wild_poke} flew away.")
                catch_mode = False
                wild_poke = ""
                my_poke = ""
        else:
            await message.send(f"You cannot catch pokemon at this moment")
    else:
        await message.send("You Don't Have Pokeball")
    

@client.command(breif = "heal your pokemon for $5")
async def heal(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    query0 = f"SELECT pokemon FROM MY_POKEMON WHERE name = '{username}';"
    userdata_sql = sqlio.read_sql_query(query0,conn)
    pokedict1 = userdata_sql["pokemon"].values[0]
    poke_list = pokedict1.split(";")
    pokeupstr = ""
    for pokemon_ in poke_list:
        pokem = pokemon_.split(",")
        if len(pokem)>1:
            pname = pokem[0]
            poke_level = int(pokem[1])
            pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == pname]
            pokes_hp = int(int(pokedata["HP"].values[0]) * (poke_level/5))    
            pokem[3] = pokes_hp
            pokeupstr = pokeupstr + f"{pokem}"
    pokeupstr = pokeupstr.replace("[","")
    pokeupstr = pokeupstr.replace("]",";")
    pokeupstr = pokeupstr.replace("'","")
    pokeupstr = pokeupstr.replace(" ","")

    query09 = f"SELECT money FROM PLAYER WHERE name = '{username}';"
    userdata_sql = sqlio.read_sql_query(query09,conn)
    money = int(userdata_sql["money"].values[0])

    if money < 5:
        await message.send("Not Enough Money")
    else:
        update_query = f"UPDATE MY_POKEMON SET pokemon = '{pokeupstr}' WHERE name = '{username}';"
        cursor.execute(update_query)

        update_mon_heal = money - 5

        update_query2 = f"UPDATE PLAYER SET money = '{update_mon_heal}' WHERE name = '{username}';"
        cursor.execute(update_query2)
        pc = discord.Embed(title = "Pokemon Center", description = "Nurse Joy: All your pokemons are healed for $5. Thank You")
        file = discord.File("image/nursejoy.png", filename="nursejoy.png")
        pc.set_thumbnail(url="attachment://nursejoy.png")
        await message.send(file=file, embed=pc)
        
# completed
@client.command(breif = "gym leaders list")
async def gym(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")    
    
    conn, cursor = database_initialize()
    cursor.execute(f"SELECT * FROM my_pokemon WHERE name = '{username}';")
    check_player_set = cursor.fetchone()
    if check_player_set:
        gym_list = discord.Embed(title = "Gym List")
        gym_list.add_field(name="Brock", value="Pewter City Gym Leader")
        gym_list.add_field(name="Misty", value="Cerulean City Gym Leader")
        gym_list.add_field(name="Lt. Surge", value="Vermilion City Gym Leader")
        gym_list.add_field(name="Erika", value="Celadon City Gym Leader")
        gym_list.add_field(name="Koga", value="Fuchsia City Gym Leader")
        gym_list.add_field(name="Sabrina", value="Saffron City Gym Leader")
        gym_list.add_field(name="Blaine", value="Cinnabar Island Gym Leader")
        gym_list.add_field(name="Giovanni", value="Viridian City Gym Leader")
        gym_list.add_field(name="Lance", value="Hall of Fame Battle Showdown")
        gym_list.add_field(name="Ash", value="Ultimate Showdown")
        await message.send(embed=gym_list)
    else:
        await message.send("You have to register as a trainer write -pokemon then -select pokemon to be next pokemon master.")

# incomplete
@client.command(breif = "challlenge gym leaders", aliases = ['ch'])
async def challenge(message, gym_leader):
    global battle_mode, user_on, catch_mode, wild_poke, wild_hp, wild_level, gym_le
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")
        user_on = username

    conn, cursor = database_initialize()

    query2 = f"SELECT * FROM PLAYER WHERE name = '{username}';"
    userdata_sql12 = sqlio.read_sql_query(query2,conn)
    personal_lvl = int(userdata_sql12["level"].values[0])
    badge = int(userdata_sql12["badge"].values[0])

    cursor.execute(f"SELECT * FROM my_pokemon WHERE name = '{username}';")
    check_player_set = cursor.fetchone()

    if check_player_set:
        gym_leader = gym_leader.lower()
        gym_le = gym_leader.capitalize()
        if gym_leader == "brock":
            if personal_lvl < 10:
                gym_lead = discord.Embed(title = "Pewter City Gym", description = "Brock: You're not worthy of challenge reach personal level 10 to challenge me.", color=0x99aab5)
                file = discord.File("image/brock.png", filename="brock.png")
                gym_lead.set_thumbnail(url="attachment://brock.png")
                await message.send(file=file, embed=gym_lead)

            elif badge == 0 and personal_lvl >=10:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Geodude', 'Onix']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Geodude':
                    gym_level = 14
                if gym_choice == 'Onix':
                    gym_level = 15

                gym_lead = discord.Embed(title = "Pewter City Gym", description = f"Brock: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/brock.png", filename="brock.png")
                gym_lead.set_thumbnail(url="attachment://brock.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)

                
        if gym_leader == "misty":
            if personal_lvl < 20:
                gym_lead = discord.Embed(title = "Cerulean City Gym", description = "Misty: Such pity! Reach personal level 20 to challenge me.", color=0x92e3ec)
                file = discord.File("image/misty.png", filename="misty.png")
                gym_lead.set_thumbnail(url="attachment://misty.png")
                await message.send(file=file, embed=gym_lead)

            elif badge == 1 and personal_lvl >=20:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Staryu', 'Starmie']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Staryu':
                    gym_level = 23
                if gym_choice == 'Starmie':
                    gym_level = 25

                gym_lead = discord.Embed(title = "Cerulean City Gym", description = f"Misty: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/misty.png", filename="misty.png")
                gym_lead.set_thumbnail(url="attachment://misty.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)
        
        if gym_leader == "surge":
            if personal_lvl < 30:
                gym_lead = discord.Embed(title = "Vermilion City Gym", description = "Lt. Surge: You're not worthy of challenge reach personal level 30 to challenge me.", color=0xf0b237)
                file = discord.File("image/surge.png", filename="surge.png")
                gym_lead.set_thumbnail(url="attachment://surge.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 2 and personal_lvl >=30:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Electrode', 'Raichu']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Electrode':
                    gym_level = 30
                if gym_choice == 'Raichu':
                    gym_level = 35

                gym_lead = discord.Embed(title = "Vermilion City Gym", description = f"Lt. Surge: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/surge.png", filename="surge.png")
                gym_lead.set_thumbnail(url="attachment://surge.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)

        
        if gym_leader == "erika":
            if personal_lvl < 40:
                gym_lead = discord.Embed(title = "Celadon City Gym", description = "Erika: You're not worthy of challenge reach personal level 40 to challenge me.", color=0x2E8B57)
                file = discord.File("image/erika.png", filename="erika.png")
                gym_lead.set_thumbnail(url="attachment://erika.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 3 and personal_lvl >=40:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Gloom', 'Vileplume']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Gloom':
                    gym_level = 35
                if gym_choice == 'Vileplume':
                    gym_level = 40

                gym_lead = discord.Embed(title = "Celadon City Gym", description = f"Erika: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/erika.png", filename="erika.png")
                gym_lead.set_thumbnail(url="attachment://erika.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)
        
        if gym_leader == "koga":
            if personal_lvl < 50:
                gym_lead = discord.Embed(title = "Fuchsia City Gym", description = "Koga: You're not worthy of challenge reach personal level 50 to challenge me.", color=0x94a4ca)
                file = discord.File("image/koga.png", filename="koga.png")
                gym_lead.set_thumbnail(url="attachment://koga.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 4 and personal_lvl >=50:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Venonat', 'Venomoth']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Venonat':
                    gym_level = 48
                if gym_choice == 'Venomoth':
                    gym_level = 50

                gym_lead = discord.Embed(title = "Fuchsia City Gym", description = f"Koga: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/koga.png", filename="koga.png")
                gym_lead.set_thumbnail(url="attachment://koga.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)        

        if gym_leader == "sabrina":
            if personal_lvl < 60:
                gym_lead = discord.Embed(title = "Saffron City Gym", description = "Sabrina: You're not worthy of challenge reach personal level 60 to challenge me.", color=0x2b2e5c)
                file = discord.File("image/sabrina.png", filename="sabrina.png")
                gym_lead.set_thumbnail(url="attachment://sabrina.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 5 and personal_lvl >=60:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Hypno', 'Gengar']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Hypno':
                    gym_level = 58
                if gym_choice == 'Gengar':
                    gym_level = 60

                gym_lead = discord.Embed(title = "Saffron City Gym", description = f"Sabrina: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/sabrina.png", filename="sabrina.png")
                gym_lead.set_thumbnail(url="attachment://sabrina.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)

        if gym_leader == "blaine":
            if personal_lvl < 70:
                gym_lead = discord.Embed(title = "Cinnabar Island Gym", description = "Blaine: You're not worthy of challenge reach personal level 70 to challenge me.", color=0xDC143C)
                file = discord.File("image/blaine.png", filename="blaine.png")
                gym_lead.set_thumbnail(url="attachment://blaine.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 6 and personal_lvl >=70:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Magma', 'Flareon']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Magma':
                    gym_level = 67
                if gym_choice == 'Flareon':
                    gym_level = 65

                gym_lead = discord.Embed(title = "Cinnabar Island Gym", description = f"Blaine: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/blaine.png", filename="blaine.png")
                gym_lead.set_thumbnail(url="attachment://blaine.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)
        
        if gym_leader == "giovanni":
            if personal_lvl < 80:
                gym_lead = discord.Embed(title = "Viridian City Gym", description = "Giovanni: You're not worthy of challenge reach personal level 80 to challenge me.", color=0x0c0404)
                file = discord.File("image/giovanni.png", filename="giovanni.png")
                gym_lead.set_thumbnail(url="attachment://giovanni.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 7 and personal_lvl >=80:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Rhydon', 'Rhyhorn']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Rhyhorn':
                    gym_level = 70
                if gym_choice == 'Rhydon':
                    gym_level = 80

                gym_lead = discord.Embed(title = "Viridian City Gym", description = f"Giovanni: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/giovanni.png", filename="giovanni.png")
                gym_lead.set_thumbnail(url="attachment://giovanni.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)
        
        if gym_leader == 'lance':
            if personal_lvl < 90:
                gym_lead = discord.Embed(title = "Hall of Fame Battle", description = "Lance: You're not worthy of challenge collect all 8 gym badges first.", color=0x800000)
                file = discord.File("image/lance.png", filename="lance.png")
                gym_lead.set_thumbnail(url="attachment://lance.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 8 and personal_lvl >=90:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Dragonite', 'Garados']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Garados':
                    gym_level = 80
                if gym_choice == 'Starmie':
                    gym_level = 90

                gym_lead = discord.Embed(title = "Hall of Fame Battle", description = f"Lance: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/lance.png", filename="lance.png")
                gym_lead.set_thumbnail(url="attachment://lance.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)

        if gym_leader == 'ash':
            if personal_lvl >= 100:
                gym_lead = discord.Embed(title = "Ultimate Showdown", description = "Ash: You're not worthy of challenge defeat lance to battle me", color=0xf0b237)
                file = discord.File("image/ash.png", filename="ash.png")
                gym_lead.set_thumbnail(url="attachment://ash.png")
                await message.send(file=file, embed=gym_lead)
            elif badge == 9 and personal_lvl >=90:
                user_on = username
                battle_mode = True
                catch_mode = False
                gym_pokemon = ['Pikachu', 'Charizard']

                gym_choice = random.choice(gym_pokemon)
                if gym_choice == 'Pikachu':
                    gym_level = 95
                if gym_choice == 'Charizard':
                    gym_level = 98

                gym_lead = discord.Embed(title = "Ultimate Showdown", description = f"Ash: Get Ready To Rumble. Let's Go {gym_choice}", color=0x99aab5)
                file = discord.File("image/ash.png", filename="ash.png")
                gym_lead.set_thumbnail(url="attachment://ash.png")
                await message.send(file=file, embed = gym_lead)

                pokedata = pokemon_data.loc[pokemon_data["Pokemon"] == gym_choice]
                gym_hp = int(int(pokedata["HP"].values[0]) * (gym_level/5))
                pokenum = pokedata["Nat"].values[0]

                gym_embed = discord.Embed(title = gym_choice)
                gym_embed.set_thumbnail(url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/%03d.png"%pokenum)
                gym_embed.add_field(name = "lvl", value=gym_level)
                gym_embed.add_field(name = "HP", value= gym_hp)
                wild_poke = gym_choice
                wild_hp = gym_hp
                wild_level = gym_level
                await message.send(embed = gym_embed)
    else:
        await message.send("You have to register as a trainer write -pokemon then -select pokemon to be next pokemon master.")

@client.command(brief = "itemlist", aliases=['il'])
async def itemlist(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    cursor.execute(f"SELECT * FROM player WHERE name = '{username}';")
    check_player_set = cursor.fetchone()
    if check_player_set:
        shopem = discord.Embed(title = "Item List", description = "Item list you can shop buy")
        shopem.add_field(name = "Pokeball", value="10")
        shopem.add_field(name = "Greatball", value="100")
        shopem.add_field(name = "Ultraball", value="200")
        shopem.add_field(name = "Masterball", value="800")
        shopem.add_field(name = "Fire Stone", value="300")
        shopem.add_field(name = "Water Stone", value="300")
        shopem.add_field(name = "Thunder Stone", value="300")
        shopem.add_field(name = "Moon Stone", value="300")
        await message.send(embed = shopem)

@client.command(brief = "shop item")
async def shop(message, action, item_name,quantity):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    cursor.execute(f"SELECT * FROM player WHERE name = '{username}';")
    check_player_set = cursor.fetchone()
    if check_player_set:
        query09 = f"SELECT money, ball, stones FROM PLAYER WHERE name = '{username}';"
        userdata_sql = sqlio.read_sql_query(query09,conn)
        money = int(userdata_sql["money"].values[0])
        ball = userdata_sql["ball"].values[0]
        stones = userdata_sql["stones"].values[0]

        ball = ball.split(".")
        stones = stones.split("-")

        pokeball_ = int(ball[0])
        greatball_ = int(ball[1])
        ultraball_ = int(ball[2])
        masterball_ = int(ball[3])
        firestone_ = int(stones[0])
        waterstone_ = int(stones[1])
        thunderstone_ = int(stones[2])
        moonstone_ = int(stones[3])
        quantity = int(quantity)

        if action == "buy":    
            if item_name == 'pokeball':
                pokeball_ = pokeball_ + quantity
                price = 10 * quantity
            if item_name == 'greatball':
                greatball_ = greatball_ + quantity
                price = 100 * quantity
            if item_name == 'ultraball':
                ultraball_ = ultraball_ + quantity
                price = 200 * quantity
            if item_name == 'masterball':
                masterball_ = masterball_ + quantity
                price = 800 * quantity
            if item_name == 'firestone':
                firestone_ = firestone_ + quantity
                price = 300 * quantity
            if item_name == 'waterstone':
                waterstone_ = waterstone_ + quantity
                price = 300 * quantity
            if item_name == 'thunderstone':
                thunderstone_ = thunderstone_ + quantity
                price = 300 * quantity
            if item_name == 'moonstone':
                moonstone_ = moonstone_ + quantity
                price = 300 * quantity
            if money > price:
                money = money - price
                ball__ = f"{pokeball_}.{greatball_}.{ultraball_}.{masterball_}"
                stones__ = f"{firestone_}-{waterstone_}-{thunderstone_}-{moonstone_}"
                q_shop = f"UPDATE PLAYER SET money = '{money}', ball = '{ball__}', stones = '{stones__}' WHERE name = '{username}';"
                cursor.execute(q_shop)
            else:
                shoping = discord.Embed(title = str(message.author).split("#")[0]+"! You don't have sufficient money.")
                file = discord.File("image/shop.png", filename="shop.png")
                shoping.set_thumbnail(url="attachment://shop.png")
                await message.send(file = file, embed = shoping)
            
        if action == "sell":
            price = 0
            if item_name == 'pokeball' and pokeball_ > quantity:
                pokeball_ = pokeball_ - quantity
                price = 10 * quantity
            
            elif item_name == 'greatball' and greatball_ > quantity:
                greatball_ = greatball_ - quantity
                price = 100 * quantity
            
            elif item_name == 'ultraball' and ultraball_ > quantity:
                ultraball_ = ultraball_ - quantity
                price = 200 * quantity
            
            elif item_name == 'masterball' and masterball_ > quantity:
                masterball_ = masterball_ - quantity
                price = 800 * quantity
            
            elif item_name == 'firestone' and firestone_ > quantity:
                firestone_ = firestone_ - quantity
                price = 300 * quantity
            
            elif item_name == 'waterstone' and waterstone_ > quantity:
                waterstone_ = waterstone_ - quantity
                price = 300 * quantity
            
            elif item_name == 'thunderstone' and thunderstone_ > quantity:
                thunderstone_ = thunderstone_ - quantity
                price = 300 * quantity
            
            elif item_name == 'moonstone' and moonstone_ > quantity:
                moonstone_ = moonstone_ + quantity
                price = 300 * quantity
            else:
                shoping = discord.Embed(title = str(message.author).split("#")[0]+"! You don't have sufficient item.")
                file = discord.File("image/shop.png", filename="shop.png")
                shoping.set_thumbnail(url="attachment://shop.png")
                await message.send(file = file, embed = shoping)
    
            ball__ = f"{pokeball_}.{greatball_}.{ultraball_}.{masterball_}"
            stones__ = f"{firestone_}-{waterstone_}-{thunderstone_}-{moonstone_}"

            money = money + price
            q_shop = f"UPDATE PLAYER SET money = '{money}', ball = '{ball__}', stones = '{stones__}' WHERE name = '{username}';"
            cursor.execute(q_shop)



        shoping = discord.Embed(title = str(message.author).split("#")[0]+"! Thank You For Visiting")
        file = discord.File("image/shop.png", filename="shop.png")
        shoping.set_thumbnail(url="attachment://shop.png")
        await message.send(file = file, embed = shoping)

@client.command(brief = "shop item")
async def profile(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    q1 = f"SELECT * FROM player WHERE name = '{username}';"
    cursor.execute(q1)
    check_player_set = cursor.fetchone()
    if check_player_set:
        userdata_profile = sqlio.read_sql_query(q1,conn)
        personal_lvl = str(userdata_profile["level"].values[0])
        personal_badge = str(userdata_profile["badge"].values[0])
        personal_money = str(userdata_profile["money"].values[0])
        all_pball = str(userdata_profile["ball"].values[0])
        all_pball = all_pball.split(".")
        pball = all_pball[0]
        gball = all_pball[1]
        uball = all_pball[2]
        mball = all_pball[3]

        all_item = str(userdata_profile["stones"].values[0])
        all_item = all_item.split("-")
        fs = all_item[0]
        ws = all_item[1]
        ts = all_item[2]
        ms = all_item[3]
        profile_name = str(message.author).split("#")[0]

        prof = discord.Embed(title = f"{profile_name}'s Profile")
        prof.add_field(name = "Personal Level", value = personal_lvl)
        prof.add_field(name = "Badge", value = personal_badge)
        prof.add_field(name = "Money", value = personal_money)
        prof.add_field(name = "Pokeball", value = pball)
        prof.add_field(name = "Greatball", value = gball)
        prof.add_field(name = "Ultraball", value = uball)
        prof.add_field(name = "Masterball", value = mball)
        prof.add_field(name = "Fire Stone", value = fs)
        prof.add_field(name = "Water Stone", value = ws)
        prof.add_field(name = "Thunder Stone", value = ts)
        prof.add_field(name = "Moon Stone", value = ms)
        await message.send(embed = prof)

# completed
@client.command(breif = "guides to play", aliases=['g'])
async def guide(message):
    username = message.author.mention

    if username.__contains__("!"):
        username = username.replace("!", "")

    conn, cursor = database_initialize()
    cursor.execute(f"SELECT * FROM player WHERE name = '{username}';")
    check_player_set = cursor.fetchone()
    if check_player_set:
        guide = discord.Embed(title = "Prof. Oak", description = "Professor Oak: Some guides are given below. Good Luck !")
        file = discord.File("image/prof.png", filename="prof.png")
        guide.set_thumbnail(url="attachment://prof.png")
        
        guide.add_field(name = "Search Pokemon", value = '-search <pokemon name> : depends on your luck, experience and rarity of pokemon')
        guide.add_field(name = "Forest", value = '-forest : random pokemon appears')
        guide.add_field(name = "Choose Pokemon", value = '-go <pokemon> : to choose pokemon for battle')
        guide.add_field(name = "Catch", value = '-pb : normal pokeball, -gb : greatball, -ub : ultraball, -mb : masterball')
        guide.add_field(name = "Heal", value = '-heal : heal pokemon after battle')
        guide.add_field(name = "Use", value = '-use <move> : to use battle moves while in battle')
        guide.add_field(name = "Battle Friend", value = '-battle @Mention Friend : battle with you friends')
        guide.add_field(name = "Gym", value = '-gym : shows gym leader names')
        guide.add_field(name = "Gym Battle", value = '-challenge <gym leader> : to get badges')
        guide.add_field(name = "Item List", value = '-itemlist : to show items')
        guide.add_field(name = "Shop", value = '-shop <action> <item name> <quantity>: to buy or sell item')
        guide.add_field(name = "Profile", value = '-profile : your profile')
        guide.add_field(name = "Guide", value = '-guide : shows guide to play the game')
        
        await message.send(file=file, embed=guide)
    else:
        await message.send("You have to register as a trainer write -pokemon to become the pokemon master.")

client.run(TOKEN)
