#!/bin/python3

import tempfile, os, re
from taskw import TaskWarrior
from subprocess import call

# Get the system $EDITOR, default to Vim
EDITOR = os.environ.get("EDITOR", "vim")

# Load TaskWarrior
taskw = TaskWarrior()


def parse_todos(text):
    lines = text.split("\n")

    for line in lines:
        try:
            if line[0] == "#":
                continue
        except IndexError:
            continue

        # Get task description
        try:
            description = re.search(r"\"(.+)\"", line).group(1)
        except AttributeError:
            print("Couldn't description for " + line)
            continue

        # Get the Taskwarrior task
        task = taskw.task_add(description)
        task_id = task["id"]

        # Get the task priority
        try:
            task["priority"] = re.search(r"\(([UHMNLT])\)", line).group(1)
        except AttributeError:
            pass

        # Get the task project
        try:
            task["project"] = re.search(r"\+(\S+)", line).group(1)
        except AttributeError:
            pass

        # Get the task context(s)
        task["tags"] = []
        for match in re.finditer(r"@(\S+)", line):
            try:
                task["tags"].append(match.group(1))
            except AttributeError:
                pass

        # Get any other tags
        for match in re.finditer(r"(\w+):(\w+)", line):
            try:
                task[match.group(1)] = match.group(2)
            except (AttributeError, IndexError):
                pass

        # Attempt to update tasks
        taskw.task_update(task)

        # Make sure description didn't go away
        (_, task) = taskw.get_task(id=task_id)
        if task["description"] != description:
            task["description"] = description
            taskw.task_update(task)


def main():
    # Initialize the file buffer
    initial_message = b"#(N) \"Task\" @CONTEXT +PROJECT due: scheduled:"

    # Open editor for input
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        # Create a temporary file
        tf.write(initial_message)
        tf.flush()

        # Send temporary file to the editor
        call([EDITOR, tf.name])

        # Retrieve the edited file
        tf.seek(0)
        edited_message = tf.read().decode("utf-8")

    parse_todos(edited_message)

if __name__ == "__main__":
    main()
