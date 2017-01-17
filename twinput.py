#!/usr/bin/python3

# Copyright (C) 2017 Robert Herschel Hawk
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

from os import environ, getcwd
from taskw import TaskWarrior
from taskw.exceptions import TaskwarriorError
from sys import argv

from buffer import get_header, get_fail_message, open_file_buffer
from parse import git_grep_todos, parse_todos, read_pim

# Get the system editor, defaulting to Vim
EDITOR = environ.get("EDITOR", "vim")
VERSION = "TaskWarrior Input 1.0.0-rc2"

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
    try:
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
                    failed = parse_todos(taskw, grepd)
                    while failed:
                        initial_message = (get_header(VERSION)
                                           + get_fail_message(failed))
                        to_parse = open_file_buffer(initial_message,
                                                    editor=EDITOR)
                        failed = parse_todos(taskw, to_parse)
                elif arg == "-o" or arg == "--orgmode":
                    try:
                        pim_dir = environ["pim"]
                    except KeyError:
                        print("\n$pim environment variable is not set.\n")
                        continue

                    pim = read_pim(pim_dir)
                    failed = parse_todos(taskw, pim)
                    while failed:
                        initial_message = (get_header(VERSION)
                                           + get_fail_message(failed))
                        to_parse = open_file_buffer(initial_message,
                                                    editor=EDITOR)
                        failed = parse_todos(taskw, to_parse)
                else:
                    print("\n" + "Bad argument" + "\n")
        else:
            get_direct_input()

    except TaskwarriorError as err:
        msg = err.stderr.decode("utf-8").split("\n")[-1]
        print("Uncaught Taskwarrior Error: " + msg)
