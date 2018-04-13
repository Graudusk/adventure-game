#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ett spel

i, info     Skriver ut beskrivningen av rummet.
h, hjälp    Skriver ut en lista av de kommandon som du kan göra.
fr, fram    Gå framåt till nästa rum, om det är upplåst.
ba, bak     Gå bakåt till föregående rum.
se          Se dig runt omkring i rummet.
l, ledtråd  Ge en ledtråd specifikt för rummet och för dina framsteg.
c, cheat    Utför automatiskt alla handlingar som krävs för att klara rummet användaren står i.
a, avsluta  Avslutar spelet.
spara [filnamn] Sparar spelet till en sparfil.
ladda [filnamn] Laddar en sparfil specificerad av användaren.

o, objekt   Skriver ut vilka objekt som finns i rummet.
t [objekt], titta [objekt]  Skriver ut beskrivningen av objektet.
ö [objekt], öppna [objekt]  Öppna objektet om det går att öppna.
s [objekt], sparka [objekt]     Sparka på objektet så det går sönder, om det kan gå sönder.
f [objekt], flytta [objekt]     Flytta på objektet så det hamnar på en annan plats,
             om det går att flytta.
p [objekt], prata [objekt]     Försöker prata med objekt, om de svarar.

inv, inventarier    Skriver ut vilka objekt som finns i ryggsäcken.
ta [objekt]     Ta ett objekt, om det går, och lägg i ryggsäcken.
sl [objekt], släpp [objekt]     Släpp ett objekt som ligger i din ryggsäck.
anv [objekt], använd [objekt]     Använd ett objekt.
"""


import json
import time
import cli_parser
import comd
import room_cmds
import inventory as inv

start = time.time()
# run your code

jsonfile = open("data.json", "r")

data = json.load(jsonfile)

def print_info_cli():
    """
    Prints out a description of the game and the mage's idea.
    """
    print("Detta spel är ett klassiskt pusselspel där spelaren ska lösa pussel i olika rum")
    print("för att låsa upp dörren och komma vidare till nästa rum. ")
    print("\nSpelets handling är att spelaren har blivit inlåst i en källare med ett antal rum ")
    print("separerade av låsta dörrar av en vålnad. ")
    print("\n")

def print_about():
    """
    Prints out information about the game's creator.
    """
    print("Eric Johansson har skapat detta spel. ")
    print("Han studerar på Blekinge tekniska Högskola på kursen Webbprogrammering 120p Distans.")

def print_cheat():
    """
    Prints out the shortest possible way to solve the game
    """
    print("Kortaste möjliga väg för att lösa spelet är i ordning: ")
    print("1. öppna låda")
    print("2. ta rostig nyckel, ta lykta")
    print("3. använd lykta")
    print("4. flytta låda")
    print("5. titta bokhylla")
    print("6. ta blå nyckel")
    print("7. öppna dörr")
    print("8. fram\n")
    print("9. öppna dörr")
    print("10. fram\n")
    print("11. sparka tunna")
    print("12. ta gul nyckel")
    print("13. öppna dörr")
    print("14. fram\n")
    print("15. öppna kista")
    print("16. ta magisk spegel")
    print("17. bak 2 gånger till andra rummet\n")
    print("18. titta bok")
    print("19. framåt 2 gånger till det fjärde rummet\n")
    print("20. prata troll och svara rätt på frågan för att få röd nyckel")
    print("21. öppna dörr")
    print("22. fram\n")
    print("23. titta stenvägg")
    print("24. skriv in teckenkombinationen som du läste i boken")
    print("25. gå ut ur källaren!")
    print()
    print("För att hamna i sista rummet med alla föremål i inventarie skriv kommandot 'ladda_sista'.")

def main():
    """
    The main func that starts the program
    """
    opts = cli_parser.parse_options()

    args = opts["known_args"]

    if args["info"] is True:
        print_info_cli()
    elif args["cheat"] is True:
        print_cheat()
    elif args["about"] is True:
        print_about()
    else:
        start_game()

def start_game():
    """
    The func that starts the game and contains the main while loop
    """
    show_intro()
    get_solution()
    print(data["rooms"][data["current_room"]]["descr"])
    while 1:

        print_room()
        choice = input("--> ").lower()

        if choice == "":
            print("Inget kommando")
            continue

        command = comd.get_command(data, choice)

        if command is False:
            continue

        target = comd.get_cmd_target(data, choice)

        if target is False:
            continue



        if command != "":
            if command == "framåt":
                print("gå framåt")
            elif command == "spara":
                save_game(choice)
            elif command == "ladda_sista":
                load_last_state()
            elif command == "ladda":
                load_game(choice)
            elif command == "ledtråd":
                print_clue()
            elif command == "fram":
                room_cmds.forward(data)
            elif command == "bak":
                room_cmds.backwards(data)
            elif command == "hjälp":
                print_help()
            elif command == "info":
                print_info()
            elif command == "se":
                room_cmds.look_around(data)
            elif command == "cheat":
                do_cheat()
            elif command == "objekt":
                room_cmds.show_objects(data)
            elif command == "inventarier":
                inv.show(data)
            elif command == "ta":
                inv.take(data, target)
            elif command == "släpp":
                inv.drop_item(data, target)
            elif command == "använd":
                comd.use_item(data, target)
            elif command == "avsluta":
                break
            else:
                if target is not None:
                    comd.check_command(data, command, target)
                else:
                    print("Kan inte hitta objektet.")
        if data["current_room"] == 5:
            do_win()
            break

def do_win():
    """
    print out win message
    """
    end = time.time()

    elapsed = end - start
    print("Grattis! Du kom ut ur källaren!")
    print("Ditt äventyr tog " + str(int(elapsed)) + " sekunder")

def load_last_state():
    """
    loads the last state before victory
    """
    load_game("final_state")

def load_game(filename):
    """writes current game status to a save file"""

    global data

    if filename == "ladda":
        filename = "spara"
    if " " in filename:
        filename = filename.split(" ", 1)
        filename = filename[1]

    if "." in filename:
        filename = filename.split(".", 1)[0]

    if filename != "data":
        try:
            with open(filename + ".json", "r") as filereader:
                data = json.load(filereader)
        except Exception as e:
            print("Ingen fil med det namnet hittad.", e)

        print("Filen " + filename  + ".json laddades!")
    else:
        print("filnamnet 'data' är ett reserverat filnamn och går inte att spara över.")

def save_game(filename):
    """
    Save the state of the game to a file. 
    """
    if filename == "":
        filename = "save"

    if " " in filename:
        filename = filename.split(" ", 1)
        filename = filename[1]

    if "." in filename:
        filename = filename.split(".", 1)[0]

    if filename != "data":

        with open(filename + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
        print("Sparade spelet till filen " + filename + ".json")
    else:
        print("filnamnet 'data' är ett reserverat filnamn och går inte att spara över.")

def get_solution():
    """
    generate the solution for the stone wall pussle
    """
    signs = "αβλμπΨΩ"

    solution = []

    for _ in range(4):
        from random import randint
        sign = signs[randint(0, len(signs) - 1)]
        signs = signs.replace(sign, '')
        solution.append(sign)


    data["stone_wall_solution"] = solution

def show_intro():
    """
    Prints out the first descr and intro text.
    """
    print("Mystisk röst: Hahaha! lycka till med att rymma från mitt fängelse!\n")

def print_room():
    """
    func to print out the graphic of the room
    """
    current_room = data["current_room"]
    room = data["rooms"][current_room]
    roomstate = room["state"]

    graphic = ""    
    for line in room["graphics"][roomstate]:
        graphic += line + "\n"

    print(graphic)

def print_help():
    """
    prints out the doc string containing help and instructions
    """
    print(__doc__)

def print_clue():
    """
    prints out a clue to solve the current step of the room
    """
    room = room_cmds.get_curr_room(data)
    roomstate = room["state"]
    print(room["clues"][roomstate])

def print_info():
    """
    prints out the descr of the room
    """
    room = room_cmds.get_curr_room(data)
    print(room["descr"])

def do_cheat():
    """
    solves the current room automatically
    """
    room = room_cmds.get_curr_room(data)

    for item_object in room["objects"]:
        if "max_state"  in room["objects"][item_object]:
            room["objects"][item_object]["state"] = len(room["objects"][item_object]["descr"]) -1

    for obj in room["objectives"]:
        room["objectives"][obj] = True

    if "got_items" in room:
        for item in room["got_items"]:
            data["inventory"].append(item)

    if data["current_room"] == 1:
        data["rooms"][4]["objectives"]["book_read"] = True

    room["state"] = len(room["clues"]) - 1

if __name__ == "__main__":
    main()
