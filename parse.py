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

from hashlib import md5
from os import path, walk
from re import findall, finditer, search, sub
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


def read_pim(pim_dir):
    org_files = []

    # Find the org files
    for root, dirs, files in walk(pim_dir):
        for file in files:
            if not file.startswith(".") and file.endswith("org"):
                org_files.append(path.join(root, file))

    # Parse all found org files
    org_tasks = ""
    for org_file in org_files:
        org_tasks += parse_org_mode(org_file)

    return org_tasks


def parse_org_mode(org_file_path):
    # Read the org file into memory
    with open(org_file_path, "r") as org_file:
        org_text = org_file.read()

    prop = False
    tasks = ""
    todo = ""
    for line in org_text.split("\n"):
        try:
            # Check for a new to do entry
            todo_check = search(r"\*+ +TODO +(.*)", line)

            # If we have an existing to do entry, commit it
            if todo_check:

                if todo != "":
                    tasks += todo + "\n"

                todo = todo_check.group(1).strip()

                try:
                    priority = search(r"(\[#[ABCDEF]\])", todo).group(1)
                    todo = sub(r"\[#[ABCDEF]\]", "", todo).strip()

                    if priority == "[#A]":
                        todo = "(U) " + todo
                    elif priority == "[#B]":
                        todo = "(H) " + todo
                    elif priority == "[#C]":
                        todo = "(M) " + todo
                    elif priority == "[#E]":
                        todo = "(L) " + todo
                    elif priority == "[#F]":
                        todo = "(T) " + todo
                    else:
                        todo = "(N) " + todo
                except AttributeError:
                    todo = "(N) " + todo

                try:
                    tags = search(r":(\S+):", todo).group(1)
                    tags = tags.split(":")
                    todo = sub(r":\S+:", "", todo)
                    todo = todo.strip()

                    for tag in tags:
                        todo += " @" + tag
                except AttributeError:
                    todo += " @home"

        except AttributeError:
            pass

        if not todo_check and todo != "":
            match = False

            # Check for the start of the PROPERTIES drawer
            tag = search(r"\s*:PROPERTIES:\s*", line)
            if tag:
                continue

            # Check for the end of the PROPERTIES drawer
            tag = search(r"\s*:END:\s*", line)
            if tag:
                tasks += todo + "\n"
                todo = ""
                continue

            # Look for a deadline
            try:
                deadline = search(r".*DEADLINE: *<(\d{4}-\d{2}-\d{2}) "
                                  r"\w{3} ?(\d{2}:\d{2})?>", line)
                due_date = deadline.group(1)
                due_time = deadline.group(2)
                match = True

                if due_date and due_time:
                    todo += " due:" + due_date + "T" + due_time
                elif due_date:
                    todo += " due:" + due_date
            except AttributeError:
                pass

            # Look for a scheduled date
            try:
                scheduled = search(r".*SCHEDULED: *<(\d{4}-\d{2}-\d{2}) "
                                   r"\w{3} ?(\d{2}:\d{2})?>", line)
                sched_date = scheduled.group(1)
                sched_time = scheduled.group(2)
                match = True

                if sched_date and sched_time:
                    todo += " scheduled:" + sched_date + "T" + sched_time
                elif sched_date:
                    todo += " scheduled:" + sched_date
            except AttributeError:
                pass

            try:
                org_prop = search(r"\s*:project:\s*(.*)", line)

                proj_name = org_prop.group(1)
                match = True

                todo += " +" + proj_name
            except AttributeError:
                pass

            # Look for any properties tags
            if not match:
                try:
                    org_prop = search(r"\s*:(.+?):\s*(.*)", line)

                    prop_tag = org_prop.group(1).lower()
                    prop_val = org_prop.group(2)
                    match = True

                    todo += " " + prop_tag + ":" + prop_val
                except AttributeError:
                    pass

            if not match and line.strip() != "":
                tasks += todo + "\n"
                todo = ""

    if todo != "":
        tasks += todo + "\n"

    org_text = sub(r"TODO", "TASKED", org_text)
    with open(org_file_path, "w") as org_file:
        org_file.write(org_text)

    return tasks


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

