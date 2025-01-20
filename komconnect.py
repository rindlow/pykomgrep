# -*- coding: iso-8859-1 -*-
# Utility routines for connection setup (replaces komparam.py)
# $Id: komconnect.py,v 1.2 2007-01-15 21:02:37 kent Exp $
# (C) 1999,2003 Kent Engstr�m. Released under GPL.

import argparse
import getpass
import os

import kom


# FIXME: Things to support in this module if needed:
# -) port numbers added to the server name ("kom.foo.bar:4894")
# -) ~/.komrc

# Error reporting
class Error(Exception):
    pass

# Add standard server, name and password arguments to an optparse
# option parser.


def add_server_name_password(parser: argparse.ArgumentParser):
    ogrp = parser.add_argument_group("connection arguments")
    ogrp.add_argument("--server", action="store",
                      help="connect to SERVER")
    ogrp.add_argument("--name", action="store",
                      help="login as NAME")
    ogrp.add_argument("--password", action="store",
                      help="authenticate using PASS", metavar="PASS")

# Connect and login using the information in an optparse options object
# (e.g. one set up using add_server_name_password)


def connect_and_login(options: argparse.Namespace):

    # Get server
    server = options.server
    if server is None:
        if "KOMSERVER" in os.environ:
            server = os.environ["KOMSERVER"]
        else:
            raise Error("server not specified")

    # Get name
    name = options.name
    if name is None:
        if "KOMNAME" in os.environ:
            name = os.environ["KOMNAME"]
        else:
            raise Error("name not specified")

    # Get password
    password = options.password
    if password is None:
        if "KOMPASSWORD" in os.environ:
            password = os.environ["KOMPASSWORD"]
        else:
            password = getpass.getpass(f"Password for {name} on {server}")

    # Connect
    try:
        conn = kom.CachedConnection(server, trace=False)
    except kom.LocalError as err:
        raise Error(f"failed to connect ({err})")

    # Lookup name
    persons = conn.lookup_name(name, want_pers=1, want_confs=0)
    if len(persons) == 0:
        raise Error("name not found")
    elif len(persons) != 1:
        raise Error("name not unique")
    person_no = persons[0][0]

    # Login
    try:
        kom.ReqLogin(conn, person_no, password).response()
    except kom.Error as err:
        raise Error(f"failed to log in ({err})")

    # Done!
    return conn
