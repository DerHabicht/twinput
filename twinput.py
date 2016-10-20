#!/bin/python3

import tempfile, os, re
from taskw import TaskWarrior
from taskw.exceptions import TaskwarriorError
from subprocess import call

# Get the system editor, defaulting to Vim
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
            print("Couldn't parse description for " + line)
            continue

        # Get the Taskwarrior task
        try:
            task = taskw.task_add(description)
            task_id = task["id"]
        except TaskwarriorError as err:
            msg = err.stderr.decode("utf-8").split("\n")[-1]
            print("Adding task " + description + " failed:\n\t" + msg)
            continue

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
        for match in re.finditer(r"(\w+):(\S+)", line):
            try:
                task[match.group(1)] = match.group(2)
            except (AttributeError, IndexError):
                pass

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
            print("Adding task " + description + " failed:\n\t" + msg)
            taskw.task_delete(id=task_id)


def main():
    # Initialize the file buffer
    initial_message = b"# TaskWarrior Input 0.1.3\n"
    initial_message += b"# www.the-hawk.us\n"
    initial_message += b"#\n# Input tasks in the form:\n"
    initial_message += b"#    (N) \"Task\" @CONTEXT +PROJECT due: scheduled:"
    initial_message += b"\n\n"

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
