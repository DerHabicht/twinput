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


from hashlib import md5
from re import finditer, search, sub
from os import environ
from tempfile import NamedTemporaryFile
from taskw import TaskWarrior
from taskw.exceptions import TaskwarriorError
from subprocess import call, run, PIPE
from sys import argv, exit

# Get the system editor, defaulting to Vim
EDITOR = environ.get("EDITOR", "vim")
VERSION = "TaskWarrior Input 0.2.0a"

# Load TaskWarrior
taskw = TaskWarrior()


def parse_todos(text):
    lines = text.split("\n")
    failed_lines = []

    # TODO: Handle a line of spaces
    for line in lines:
        try:
            if line[0] == "#":
                continue
        except IndexError:
            continue


        # Metadata will be trimmed from the line.
        # The leftovers will be interpreted as the task description.
        description = line

        # Build a dictionary that will become the task
        task_data = {}

        # Get the task priority
        try:
            task_data["priority"] = search(r"^\((\w+)\)", line).group(1)
            description = sub(r"^\(\w+\)", "", description)
        except AttributeError:
            pass

        # Get the task project
        try:
            task_data["project"] = search(r"\+(\S+)", line).group(1)
            description = sub(r"\+\S+", "", description)
        except AttributeError:
            pass

        # Get the task context(s)
        task_data["tags"] = []
        for match in finditer(r"@(\S+)", line):
            try:
                task_data["tags"].append(match.group(1))
            except AttributeError:
                pass

        description = sub(r"@\S+", "", description)

        # Get any other tags
        for match in finditer(r"(\w+):(\S+)", line):
            try:
                task_data[match.group(1)] = match.group(2)
            except (AttributeError, IndexError):
                pass

        description = sub(r"\w+:\S+", "", description)
        description = description.strip()

        if description == "":
            msg = "No description found."
            failed_lines.append((line, msg))
            continue

        # Hash the input description case insensitively.
        twi_hash = md5(description.upper().encode("utf-8")).hexdigest()

        # Try to retrieve the task by its hash. If we find it, we'll update
        # instead of creating a new task.
        (task_id, task) = taskw.get_task(twi_hash=twi_hash)

        if not task_id:
            # Task not found, so we attempt to create the task
            try:
                task = taskw.task_add(description, twi_hash=twi_hash)
                task_id = task["id"]

                for key, value in task_data.items():
                    task[key] = value

            except TaskwarriorError as err:
                msg = err.stderr.decode("utf-8").split("\n")[-1]
                failed_lines.append((line, msg))
                continue

        # Attempt to update tasks
        try:
            taskw.task_update(task)

            # Make sure description didn't go away
            (_, task) = taskw.get_task(id=task_id)
            if task["description"] != description:
                task["description"] = description
                taskw.task_update(task)
        except TaskwarriorError as err:
            msg = err.stderr.decode("utf-8").split("\n")[-1]
            failed_lines.append((line, msg))
            continue


    return failed_lines


def open_file_buffer(lines=None):
    # TODO: Build buffer header as a regular string and then encode
    # Initialize the file buffer
    initial_message = (b"# " + VERSION.encode("utf-8") + b"\n"
                       + b"# www.the-hawk.us\n"
                       + b"#\n# Input tasks in the form:\n"
                       + b"#    (N) Task @CONTEXT +PROJECT due: scheduled:"
                       + b"\n\n")

    if lines:
        initial_message += (b"# The following lines were not successfully "
                            b"imported into Taskwarrior.\n"
                            b"# Uncomment to re-attempt parsing or leave "
                            b"commented to abort.\n"
                            b"# In some cases, the task might have been added,"
                            b"but some parts didn't parse.\n"
                            b"# As long as you don't change the description "
                            b"(case-insensitive) the task will be updated, "
                            b"not duped.")

        for line in lines:
            initial_message += (b"# " + line[0].encode("utf-8")
                                + b"\n#    ERROR: "
                                + line[1].encode("utf-8") + b"\n\n")

    # Open editor for input
    with NamedTemporaryFile(suffix=".tmp") as tf:
        # Create a temporary file
        tf.write(initial_message)
        tf.flush()

        # Send temporary file to the editor
        call([EDITOR, tf.name])

        # Retrieve the edited file
        # NOTE: This almost works for making the script wait on a gui editor
        #       HOWEVER, this will make the script hang if the editor is closed
        #       without changing the file. So,
        # FIXME: Make this not hang if the file is not changed

        #while True:
        #    tf.seek(0)
        #    if tf.read() != initial_message:
        #        break

        tf.seek(0)
        return tf.read().decode("utf-8")


def print_usage():
    print("\n    " + VERSION)
    print("    www.the-hawk.us")
    print("\n    Usage: " + argv[0] + " [-e|--editor {EDITOR}]\n")

    exit()


def run_git_grep():
    with open(".twparse", "r") as template_file:
        template = template_file.readline()

    print(template)

    result = run(["git", "grep", "TODO:"], stdout=PIPE).stdout.decode()
    lines = result.split("\n")

    text = ""
    for line in lines:
        try:
            task = search(r"\s+TODO:\s(.+)", line).group(1)
            task = sub(r"\$TODO", task, template)
            text += task
        except AttributeError:
            pass

    parse_todos(text)


def get_direct_input():
    failed = None
    while True:
        to_parse = open_file_buffer(lines=failed)
        failed = parse_todos(to_parse)
        if not failed:
            break


if __name__ == "__main__":
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
                    print_usage()
            elif arg == "-g" or arg == "--gitgrep":
                run_git_grep()
            else:
                get_direct_input()

