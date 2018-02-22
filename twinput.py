#!/usr/bin/python3

# Copyright (C) 2018 Robert Herschel Hawk
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

"""TaskWarrior Input
Copyright (C) 2018 Robert Herschel Hawk
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions. See the GNU General Public License v3
for more details: https://www.gnu.org/licenses/gpl-3.0.en.html

Usage:
  twinput [options]

Options:
  -h, --help                     Show this screen.
  -e EDITOR, --editor=EDITOR     Select editor for use with TWInput.
  -g, --gitgrep                  Parse TODOs in this Git repository.
  -i, --interactive              Iterate through each task interactively.
  -o, --orgmode                  Parse Org agenda TODOs into TaskWarrior.
  -s, --someday                  Show only someday tasks in interactive.
  --version                      Show the current version.
"""

from docopt import docopt
from curses import wrapper
from os import environ, getcwd
from taskw import TaskWarrior
from taskw.exceptions import TaskwarriorError
from sys import argv

from buffer import get_header, get_fail_message, open_file_buffer
from parse import git_grep_todos, parse_todos, read_pim
from interactive import scheduler

# Get the system editor, defaulting to Vim
EDITOR = environ.get("EDITOR", "vim")
VERSION = "TaskWarrior Input 1.1.0"

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
    arguments = docopt(__doc__, version=VERSION)

    if arguments["--editor"]:
        EDITOR = arguments["--editor"]

    try:
        if arguments["--gitgrep"]:
            grepd = git_grep_todos(getcwd())
            failed = parse_todos(taskw, grepd)
            while failed:
                initial_message = (get_header(VERSION)
                                   + get_fail_message(failed))
                to_parse = open_file_buffer(initial_message,
                                            editor=EDITOR)
                failed = parse_todos(taskw, to_parse)
        elif arguments["--interactive"]:
            if arguments["--someday"]:
                wrapper(scheduler, True)
            else:
                wrapper(scheduler, False)
        elif arguments["--orgmode"]:
            try:
                pim_dir = environ["pim"]
                pim = read_pim(pim_dir)
                failed = parse_todos(taskw, pim)
                while failed:
                    initial_message = (get_header(VERSION)
                                       + get_fail_message(failed))
                    to_parse = open_file_buffer(initial_message,
                                                editor=EDITOR)
                    failed = parse_todos(taskw, to_parse)
            except KeyError:
                print("\n$pim environment variable is not set.\n")
        else:
            get_direct_input()

    except TaskwarriorError as err:
        msg = err.stderr.decode("utf-8").split("\n")[-1]
        print("Uncaught Taskwarrior Error: " + msg)
