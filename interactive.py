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

from curses import (curs_set, echo, noecho)
from taskw import TaskWarrior


def get_tasks(tw, someday):

    tasks_raw = tw.load_tasks("pending")["pending"]

    if someday:
        tasks = list(filter(lambda x:
                            not x.get("imask", None)
                            and "someday" in x["tags"],
                            tasks_raw))
    else:
        tasks = list(filter(lambda x:
                            not x.get("imask", None)
                            and "someday" not in x["tags"],
                            tasks_raw))

    return tasks


def refresh(tw, someday, pos):
    tasks = get_tasks(tw, someday)
    if not tasks:
        pos = -1
    elif pos > len(tasks):
        pos = len(tasks) - 1

    return tasks, pos


def draw_task(stdscr, task, flash, pos, task_count, show_help):
    def get_context():
        if "home" in task["tags"]:
            return "Home"
        elif "work" in task["tags"]:
            return "Work"
        elif "errand" in task["tags"]:
            return "Errand"
        elif "inbox" in task["tags"]:
            return "Inbox"
        else:
            return "None"

    stdscr.clear()
    stdscr.addstr(0, 0, f'{pos + 1} of {task_count} tasks:')

    stdscr.addstr(2, 0, f'{task["description"]}')
    stdscr.addstr(3, 2, f'ID:       {task["id"]}')
    stdscr.addstr(4, 2, f'Context:  {get_context()}')
    stdscr.addstr(5, 2, f'Project:  {task.get("project", "NONE")}')
    stdscr.addstr(6, 2, f'Effort:   {task.get("effort", "NONE")}')
    stdscr.addstr(7, 2, f'Priority: {task["priority"]}')
    stdscr.addstr(8, 2, f'Due:      {task.get("due", "")}')
    stdscr.addstr(9, 2, f'Started:  {task.get("start", "")}')

    if show_help:
        stdscr.addstr(13, 0, "Options:")
        stdscr.addstr(14, 2, "previous: k       toggle someday: s")
        stdscr.addstr(15, 2, "next:     j       mark completed: d")
        stdscr.addstr(16, 2, "goto:     g       delete task:    #")
        stdscr.addstr(17, 2, "quit:     q       edit effort:    e")

    if flash:
        stdscr.addstr(11, 0, flash)


def jump(stdscr):
    stdscr.addstr(10, 0, "Goto:")
    stdscr.move(10, 6)
    echo()
    resp = stdscr.getstr()
    noecho()
    return int(resp) - 1


def update_effort(stdscr, tw, task):
    stdscr.addstr(10, 0, "Effort:")
    stdscr.move(10, 8)
    echo()
    resp = stdscr.getstr()
    noecho()
    task["effort"] = int(resp)
    tw.task_update(task)


def scheduler(stdscr, someday, flash=None):
    noecho()
    curs_set(False)

    tw = TaskWarrior(marshal=True)
    tasks = get_tasks(tw, someday)

    if not tasks:
        return

    show_help = False
    pos = 0
    while pos != -1:
        draw_task(stdscr, tasks[pos], flash, pos, len(tasks), show_help)
        flash = None

        c = stdscr.getch()
        if c == ord("q"):
            pos = -1
        elif c == ord("j"):
            pos = (pos + 1) % len(tasks)
        elif c == ord("k"):
            pos = (pos - 1) % len(tasks)
        elif c == ord("g"):
            try:
                pos = jump(stdscr)
                if pos > len(tasks):
                    pos = len(tasks) - 1
                elif pos < 0:
                    pos = 0
            except ValueError:
                flash = "ERROR: Index must be an integer"
        elif c == ord("#"):
            tw.task_delete(id=tasks[pos]["id"])
            tasks, pos = refresh(tw, someday, pos)
        elif c == ord("d"):
            tw.task_done(id=tasks[pos]["id"])
            tasks, pos = refresh(tw, someday, pos)
        elif c == ord("e"):
            try:
                update_effort(stdscr, tw, tasks[pos])
            except ValueError:
                flash = "ERROR: Effort estimate must be an integer"
            tasks, pos = refresh(tw, someday, pos)
        elif c == ord("s"):
            if someday:
                tasks[pos]["tags"].remove("someday")
            else:
                tasks[pos]["tags"].append("someday")
        elif c == ord("?"):
            show_help = not show_help

            tw.task_update(tasks[pos])
            tasks, pos = refresh(tw, someday, pos)

