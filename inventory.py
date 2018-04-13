#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
modul som hanterar ryggsäck

"""

def take(data, item):
    """
    put item in inventory
    """
    inv = data["inventory"]
    if item in data["rooms"][data["current_room"]]["items"]:
        inv.append(item)
        if item == "blå nyckel":
            data["rooms"][data["current_room"]]["state"] += 1
            data["rooms"][data["current_room"]]["objects"]["bokhylla"]["itemstate"] += 1
        data["rooms"][data["current_room"]]["items"].remove(item)
        print("plockade upp " + str(item))
    else:
        print("Kunde inte hitta " + str(item))


def show(data):
    """
    print out items in inventory
    """
    inv = data["inventory"]

    if inv:
        print("Jag har " + str(len(inv)) + " föremål:")
        for item in inv:
            print(item)
    else:
        print("Jag har inga föremål.")

def in_inv(data, item):
    """
    check if item is in inventory
    """
    inv = data["inventory"]
    is_in = item in inv
    return is_in

def drop_item(data, item):
    """
    remove item from inventory and put in current room
    """
    inv = data["inventory"]
    if item in inv:
        inv.remove(item)
        data["rooms"][data["current_room"]]["items"].append(item)
        if item == "lykta":
            data["rooms"][0]["objectives"]["lantern_lit"] = False
        print("Släppte " + str(item) + " på marken.")

def remove_item(data, item):
    """
    remove item from game
    """
    inv = data["inventory"]
    if item in inv:
        inv.remove(item)
