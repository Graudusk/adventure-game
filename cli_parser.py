#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parse CLI options.

Using argparse to parse options.
"""

import argparse

VERSION = "v0.1.1 (2017-10-17)"

options = {}

def add_options(parser):
    """
    Adds options
    """
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument("-h", "--help", action="help", 
                       help="Skriver ut denna beskrivning av programmet och vilka parameterar som fungerar.")
    group.add_argument("-v", "--version", action="version", version=VERSION, 
                       help="Skriver ut versionen av spelet")
    group.add_argument("-i", "--info", action="store_true", 
                       help="Skriver ut en beskrivning av spelet och spelets idé.")
    group.add_argument("-a", "--about", action="store_true", 
                       help="Skriver ut en kort beskrivning av upphovsmannen till spelet.")
    group.add_argument("-c", "--cheat", action="store_true", 
                       help="Skriver ut minsta möjliga väg för att klara spelet.")

def parse_options():
    """
    Parse all command line options and arguments and return them as a dictionary.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, add_help=False)

    add_options(parser)

    args, unknownargs = parser.parse_known_args()

    options["known_args"] = vars(args)
    options["unknown_args"] = unknownargs
    
    return options
