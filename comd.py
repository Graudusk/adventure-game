#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Functions handling commands 
"""

import copy
import time
import room_cmds
import inventory as inv

def get_command(data, choice):
    """
    Parse the command input and gets the command value
    """
    if " " in choice:
        choice_arr = choice.split(" ", 1)
        try:
            command = data["commands"][choice_arr[0]]
        except Exception:
            print("Kommandot kändes inte igen.")
            command = False
    else:
        try:
            command = data["commands"][choice]
        except Exception:
            print("Kommandot kändes inte igen.")
            command = False
    return command

def get_cmd_target(data, choice):
    """
    Parse the command input and gets the target value
    """
    room = room_cmds.get_curr_room(data)
    target = None
    if " " in choice:
        choice_arr = choice.split(" ", 1)
        temp_target = choice_arr[1].strip()
        try:
            if temp_target in room["objects"]:
                target = room["objects"][temp_target]["name"]
            elif temp_target in room["items"] or inv.in_inv(data, temp_target) is True:
                target = temp_target
        except Exception:
            print("Objektet kändes inte igen.")
            target = False

    return target

def send_item_error(room, target, command):
    """
    Check for error message in object and print if exists
    """
    if 0 <= room["objects"][target]["itemstate"] <= len(room["objects"][target]["actions"]) - 1:
        if "errormessage" in room["objects"][target]["actions"][room["objects"][target]["itemstate"]]:
            if command in room["objects"][target]["actions"][room["objects"][target]["itemstate"]]["errormessage"]:
                print(room["objects"][target]["actions"][room["objects"][target]["itemstate"]]["errormessage"][command])
            elif "errormessage" in room["objects"][target] and command in room["objects"][target]["errormessage"]:
                print(room["objects"][target]["errormessage"][command])

def check_requires(data, target):
    """
    check if required objective for object is solved
    """
    room = room_cmds.get_curr_room(data)
    ret = False
    
    if room["objectives"][room["objects"][target]["actions"][room["objects"][target]["itemstate"]]["requires"]] is True:
        ret = True
    return ret

def check_requires_item(data, target):
    """
    Check if required item for object is in inventory
    """
    room = room_cmds.get_curr_room(data)
    ret = False

    if inv.in_inv(data, room["objects"][target]["actions"][0]["required_item"]) is True:
        # do_solving_command(data, target)
        ret = True
    return ret

def check_solving_command(data, command, target):
    """
    Check if the command needed to progress is the command provided
    """
    ret = False
    room = room_cmds.get_curr_room(data)
    if "actions" in room["objects"][target]:
        actions = room["objects"][target]["actions"]
        if room["objects"][target]["itemstate"] >= 0 and room["objects"][target]["itemstate"] < len(actions):
            curr_action = actions[room["objects"][target]["itemstate"]]
            if curr_action["action"] == command and room["objects"][target]["name"] == target:
                if "requires" in curr_action:
                    if check_requires(data, target):
                        ret = True
                elif "required_item" in curr_action:
                    if check_requires_item(data, target):
                        ret = True
                else:
                    ret = True
        if ret is True:
            do_solving_command(data, target)
        else:
            send_item_error(room, target, command)

def check_command(data, command, target):
    """
    check if the command is valid and if events should trigger
    """
    do_command(data, command, target)
    check_solving_command(data, command, target)

def open_door(data, room, door):
    """
    open the door if not locked or key is in inventory
    """
    if room["objectives"]["door_unlocked"] is True:
        room["objectives"]["door_open"] = True
        # print("Du öppnade dörren!")   
    else:
        if inv.in_inv(data, door["actions"][0]["required_item"]) is True:
            # print("Du låste upp dörren med " + door["actions"][0]["required_item"] + "!")
            inv.remove_item(data, door["actions"][0]["required_item"])
            room["objectives"]["door_unlocked"] = True
            room["objectives"]["door_open"] = True
        else:
            print("Jag har inte rätt nyckel för den här dörren.")

def do_command(data, command, target):
    """
    run command provided
    """
    room = room_cmds.get_curr_room(data)

    if command == "titta":
        state = room["objects"][target]["itemstate"]

        if target in room["objects"] and "descr" in room["objects"][target]:
            descr = room["objects"][target]["descr"]
            if state == -1:
                if "inactive_descr" in room["objects"][target]:
                    print(room["objects"][target]["inactive_descr"])
            elif state < len(descr):
                print(descr[state])
            else:
                print(descr[state - 1])
    else:
        pass

def do_solving_command(data, target):
    """
    run solving command provided and eventual events triggered
    """
    room = room_cmds.get_curr_room(data)

    result = room["objects"][target]["actions"][room["objects"][target]["itemstate"]]["done"]

    if "solve" in result:
        room["state"] += 1
        room["objects"][target]["itemstate"] += 1

    command_return(result, data, target)

def command_return(result, data, target):
    """
    handle return values from solving function
    """
    room = room_cmds.get_curr_room(data)
    print(result["msg"])
    if result["event"] == "activate":
        activate_object(result["value"], data)
    elif result["event"] == "drop_item":
        for item in result["value"]:
            room["items"].append(item)
    elif result["event"] == "get_item":
        for item in result["value"]:
            data["inventory"].append(item)
    elif result["event"] == "unlock_door":
        open_door(data, room, room["objects"][target])
        print("Mystisk röst: " + room["unlock_msg"])
    elif result["event"] == "open_chest":
        open_chest(result, data)
    elif result["event"] == "riddle":
        ask_riddle(result, data)
    elif result["event"] == "read_book":
        read_book(result, data)
    elif result["event"] == "solve":
        solve(result, data)

    if "complete_objective" in result:
        room["objectives"][result["complete_objective"]] = True

def print_wall(result, signs):
    """
    print out the graphic for the stone wall
    """
    temp_wall = copy.deepcopy(result["wall"])
    
    graphic = ""
    changed_line = temp_wall[3]
    # print("signs", signs)

    solution = signs
    changed_line = changed_line.format(solution[0], solution[1], solution[2], solution[3])

    # print(changed_line)

    temp_wall[3] = changed_line
    for line in temp_wall:
        graphic += line + "\n"

    print(graphic)

def solve(result, data):
    """
    Main function for the solve stone wall-game
    """
    print("Skriv 1, 2, 3 eller 4 och tryck på 'enter' för att byta tecken.")
    print("Skriv 'ok' och tryck på 'enter' när du är klar.")
    allowed = ["1", "2", "3", "4"]
    signs = ['0', '0', '0', '0']
    print_wall(result, signs)
    while True:
        key = input("-->")
        if key == "":
            continue
        if key == "ok": #Enter
            check_wall(data, signs, result)
            break
        elif key in allowed:
            signs = change_sign(data, key, signs)
        print_wall(result, signs)

def check_wall(data, signs, result):
    """
    check if the stone wall-game is solved
    """
    room = room_cmds.get_curr_room(data)

    if data["stone_wall_solution"] == signs:
        result["cinematic"][0][5] = result["cinematic"][0][5].format(signs[0], signs[1], signs[2], signs[3])
        result["cinematic"][1][6] = result["cinematic"][1][6].format(signs[0], signs[1], signs[2], signs[3])
        room["state"] += 1
        room["objects"]["stenvägg"]["itemstate"] += 1

        room["objectives"]["door_open"] = True
        room["objectives"]["door_unlocked"] = True

        for picture in result["cinematic"]:
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            print("Du löste hemligheten!")
            graphic = ""
            for line in picture:
                graphic += line + "\n"

            print(graphic)
            time.sleep(1)
        time.sleep(1)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        print("Du löste hemligheten!")
        print("Du kan lämna källaren och äntligen komma ut!")
        print("Mystisk röst: Är du ute?! Hur är det end möjligt?! Du ska få igen för det här!")
    else:
        print("Alla tecken återställs till sin ursprungliga position.")
        print("Du angav fel lösning på pusslet.")

def change_sign(data, index, signs):
    """
    function to change the signs on the stone wall
    """
    index = int(index) - 1
    sign = signs[int(index)]
    amount = len(data["stone_wall_signs"])
    characters = data["stone_wall_signs"]
    # print("signs", signs, "amount", amount, "sign", sign, "characters", characters)

    if sign == "0" or amount == characters.index(sign) + 1:
        signs[int(index)] = characters[0]
    else:
        signs[int(index)] = characters[characters.index(sign) + 1]
    # print("signs2", signs)
    return signs

def read_book(result, data):
    """
    function for the read book-event
    """
    graphic = ""
    book_line = result["book"][3]
    solution = data["stone_wall_solution"]
    book_line = book_line.format(solution[0], solution[1], solution[2], solution[3])

    result["book"][3] = book_line
    for line in result["book"]:
        graphic += line + "\n"

    print(graphic)

    data["rooms"][4]["objectives"]["book_read"] = True

    input("Fortsätt...")

def ask_riddle(result, data):
    """
    function for the solve riddle-event
    """
    print("Trollet: Jaså, du har fått tag i den magiska spegeln?")
    print("Jag är anställd av vålnaden som gjorde den här källaren för att vakta dörren.")
    print("Men jag gillar dig, jag ska hjälpa dig ut hätifrån.")
    print("Svara på min fråga så får du nyckeln till dörren! ")
    riddles = data["riddles"]

    from random import randint
    riddle = riddles[randint(0, 4)]
    while 1:

        print(riddle["riddle"])
        answer = input("svar: ")
        if answer == "":
            print("Trollet: Ge mig ett svar då!")
            continue
        if answer == riddle["answer"]:
            print("Trollet: Haha! Helt rätt! Här har du!")
            data["inventory"].append(result["value"])
            print("Trollet gav dig en röd nyckel.\nDu stoppar den i fickan.")
            break
        else:
            print("Trollet: Det var fel! ")
            break

def open_chest(result, data):    
    """
    function for the open chest-event
    """
    data["rooms"][1]["objects"]["bok"]["itemstate"] += 1
    data["rooms"][data["current_room"]]["items"].append(result["value"][0])

def use_item(data, target):
    """
    checks if item has event handler attached and runs specific event
    """
    if inv.in_inv(data, target) is True:
        if target == "lykta":
            print("Rummet lyser upp och jag kan se mycket mer. ")
            data["rooms"][data["current_room"]]["objectives"]["lantern_lit"] = True
        elif target == "magisk spegel":
            print("Du tittar in i spegeln och väggen\n bakom dig lyser upp och verkar flimmra.")
            print("Kanske spegeln kan visa något som inte kunde synas förut?")
        else:
            print("Du kan inte använda den nu!")
    else:
        print("Du har inget sådant föremål.")

def activate_object(curr_object, data):
    """
    make object active and usable
    """
    room = room_cmds.get_curr_room(data)
    room["objects"][curr_object]["itemstate"] += 1
