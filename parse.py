from hashlib import md5
from re import finditer, search, sub
from taskw.exceptions import TaskwarriorError
from subprocess import run, PIPE


def git_grep_todos(directory):
    with open(directory + "/.twparse", "r") as template_file:
        template = template_file.readline()

    result = run(["git", "grep", "TODO:"], cwd=directory,
                 stdout=PIPE).stdout.decode()
    lines = result.split("\n")

    text = ""
    for line in lines:
        try:
            task = search(r"\s+TODO:\s(.+)", line).group(1)
            task = sub(r"\$TODO", task, template)
            text += task
        except AttributeError:
            pass

    return text


def get_projects_from_tw(pending):
    projects = {"B": {}, "R": {}, "N": {}, "I": {}, "W": {}}

    for task in pending:
        try:
            project = task["project"]
        except KeyError:
            continue

        if project not in projects[task["delay"]]:
            projects[task["delay"]][project] = []

        projects[task["delay"]][project].append(task)

    return projects


def parse_todos(taskw, text):
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

        # Get the task ID, if present
        try:
            task_data["id"] = search(r"^\[([0-9]+)\]", line).group(1)
            description = sub(r"^\(\w+\)", "", description)
        except AttributeError:
            pass

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

        # There are two ways we know we're updating a task that was
        # previously entered:
        #   1. if a task id is given immediately before the
        #      priority in brackets, or
        #   2. if we can find a task with the same hash as this task's
        #      description.
        #
        # So, first we try to find the task by id, then by hash.
        task_id = task_data.get("id", None)
        if task_id:
            (task_id, task) = taskw.get_task(id=task_id)
        else:
            (task_id, task) = taskw.get_task(twi_hash=twi_hash)

        # If we fail to retrieve a task, then we create a new one.
        if not task_id:
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

            # TODO: Figure out why descriptions get dropped.
            # This is here because task descriptions get dropped sometimes,
            # and I don't really know why.
            (_, task) = taskw.get_task(id=task_id)
            if task["description"] != description:
                task["description"] = description
                taskw.task_update(task)
        except TaskwarriorError as err:
            msg = err.stderr.decode("utf-8").split("\n")[-1]
            failed_lines.append((line, msg))
            continue

    return failed_lines

