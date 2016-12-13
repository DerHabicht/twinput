#!/usr/bin/python3

# Copyright (C) 2016 Robert Herschel Hawk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO: Add a logging facility
# TODO: Write docstrings

from curses import wrapper
from os import environ, getcwd
from taskw import TaskWarrior
from sys import argv

from buffer import get_header, get_fail_message, open_file_buffer
from interactive import controller
from parse import git_grep_todos, parse_todos

# Get the system editor, defaulting to Vim
EDITOR = environ.get("EDITOR", "vim")
VERSION = "TaskWarrior Input 0.3.0a"

# Load TaskWarrior
taskw = TaskWarrior()


def get_direct_input():
    failed = None
    while True:
        initial_message = get_header(VERSION) + get_fail_message(failed)
        to_parse = open_file_buffer(initial_message, editor=EDITOR)
        failed = parse_todos(taskw, to_parse)
        if not failed:
            break


if __name__ == "__main__":
    print(getcwd())
    if len(argv) > 1:
        skip = [0]
        for index, arg in enumerate(argv):
            # Ignore the script name
            if index in skip:
                continue

            if arg == "-e" or arg == "--editor":
                try:
                    EDITOR = argv[index + 1]
                    skip.append(index + 1)
                except IndexError:
                    print("\n" + VERSION + "\n")
            elif arg == "-g" or arg == "--gitgrep":
                grepd = git_grep_todos(getcwd())
                parse_todos(taskw, grepd)
            elif arg == "-i" or arg == "--interactive":
                wrapper(controller, taskw, VERSION)
            else:
                print("\n" + "Bad argument" + "\n")
    else:
        get_direct_input()
