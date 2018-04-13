#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Functions handling the room commands
"""

def get_curr_room(data):    
    """
    get current room-object
    """
    current_room = data["current_room"]
    return data["rooms"][current_room]

def look_around(data):
    """
    get current room's descr
    """
    room = get_curr_room(data)
    roomstate = room["state"]
    print(room["to_see"][roomstate])

def forward(data):
    """
    move to next room if door is open
    """
    room = get_curr_room(data)
    if data["current_room"] != 5:

        if room["objectives"]["door_open"] is True:
            if room["objectives"]["door_unlocked"] is True:

                data["current_room"] += 1
                if data["current_room"] != 5:
                    print(data["rooms"][data["current_room"]]["descr"])

            else:
                print("Dörren är låst.")
        else:
            print("Dörren är stängd.")

def backwards(data):
    """
    move to previous room if not first room
    """
    if data["current_room"] != 0:
        data["current_room"] -= 1
    else:
        print("Jag är tillbaka där jag började. Jag kan inte gå bakåt mer.")

def show_objects(data):
    """
    show all objects and items in current room
    """
    room = get_curr_room(data)
    if room["objects"]:
        print("Jag kan se " + str(len(room["objects"])) + " objekt i rummet:")
        for i in room["objects"]:
            print(i)
    if room["items"]:
        print("\nJag kan se " + str(len(room["items"])) + " föremål i rummet:")
    for item in room["items"]:
        print(item)
