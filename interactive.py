#!/usr/bin/python3

from curses import (A_STANDOUT, curs_set, doupdate,
                    echo, KEY_ENTER, noecho, wrapper)
from datetime import datetime
from taskw import TaskWarrior
from taskw.exceptions import TaskwarriorError


class TaskList:
    class Iterator:
        def __init__(self, task_list, max_count=-1):
            self.task_list = task_list
            self.index = task_list.get_offset()
            self.count = 0
            if max_count < 0:
                self.max_count = self.task_list.length()
            else:
                self.max_count = max_count

        def __iter__(self):
            return self

        def __next__(self):
            if self.index >= self.task_list.length() \
               or self.count >= self.max_count:
                raise StopIteration
            else:
                self.index += 1
                self.count += 1
                return self.task_list[self.index - 1]

    def __init__(self):
        self._dep_idx = -1
        self._offset = 0
        self._task_list = []
        self._dep_sel = []

    def __iter__(self):
        return TaskList.Iterator(self)

    def __add__(self, count):
        self._offset += count

        if self._offset >= len(self._task_list):
            self._offset = len(self._task_list) - 1

    def __getitem__(self, index):
        return self._task_list[self._offset + index]

    def __setitem__(self, index, value):
        self._task_list[self._offset + index] = value

    def __sub__(self, count):
        self._offset -= count

        if self._offset < 0:
            self._offset = 0

    def add_task(self, task):
        self._task_list.append(task)

    def at_begin(self):
        if self._offset == 0:
            return True
        else:
            return False

    def at_end(self, size):
        if self._offset + size >= len(self._task_list) - 1:
            return True
        else:
            return False

    def begin(self):
        self._offset = 0

    def get_offset(self):
        return self._offset

    def end(self, size):
        self._offset = len(self._task_list) - (size + 1)

    def get_selection(self, size):
        return TaskList.Iterator(self, size)

    def length(self):
        return len(self._task_list) - self._offset

    def abs_length(self):
        return len(self._task_list)

    def remove_task(self, index):
        return self._task_list.pop(index)

    def toggle_dep(self, index, primary=False, dep_mode=0):
        if primary:
            self._dep_idx = index + self._offset
            self._dep_sel = []

            if dep_mode == 1:
                try:
                    dep_str = self._task_list[self._dep_idx]["depends"]
                    current_deps = dep_str.split(",")
                    for task in self._task_list:
                        if task["uuid"] in current_deps:
                            self._dep_sel.append(self._task_list.index(task))
                except KeyError:
                    pass
            elif dep_mode == 2:
                current_uuid = self._task_list[index]["uuid"]
                for task in self._task_list:
                    try:
                        if current_uuid in task["depends"]:
                            self._dep_sel.append(self._task_list.index(task))
                    except KeyError:
                        pass
            else:
                self.clear_deps()
        elif index in self._dep_sel:
            self._dep_sel.remove(index + self._offset)
        elif index != self._dep_idx:
            self._dep_sel.append(index + self._offset)

    def clear_deps(self):
        self._dep_idx = -1
        self._dep_sel = []

    def get_deps(self):
        if self._dep_idx != -1:
            depends = []
            for index in self._dep_sel:
                depends.append(self._task_list[index]["uuid"])

            return self._task_list[self._dep_idx]["uuid"], depends

    def check_dep(self, index):
        """Check for marking as a dependency.

        Returns a tuple with the first element representing whether this
        element is currently marked as a dependency and the second element
        representing whether this is the primary selection, if selected at all.

        :param index: the index of the task in this TaskList to check.
        :return: boolean tuple of form: (selected, primary)
        """
        if index + self._offset == self._dep_idx:
            return True, True
        elif index + self._offset in self._dep_sel:
            return True, False
        else:
            return False, False

    def is_primary_set(self):
        if self._dep_idx == -1:
            return False
        else:
            return True

    def refresh(self, task):
        w = TaskWarrior()
        uuid = task["uuid"]

        index = 0
        for cur_task in self._task_list:
            if cur_task["uuid"] == uuid:
                index = self._task_list.index(cur_task)

        (_, self._task_list[index]) = w.get_task(uuid=uuid)


def get_tasks():
    tasks = TaskList()

    w = TaskWarrior()
    all_tasks = w.load_tasks()["pending"]
    scheduled = []
    unscheduled = []

    tasks = TaskList()

    for task in all_tasks:
        if task.get("scheduled", None):
            scheduled.append(task)
        else:
            unscheduled.append(task)

    for task in scheduled:
        tasks.add_task(task)

    for task in unscheduled:
        tasks.add_task(task)

    return tasks


def draw_list(stdscr, tasks, cursor, render_deps=False):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    if max_x > 130:
        col_width = 100
    else:
        col_width = max_x - 30

    task_header = stdscr.subpad(3, col_width, 0, 0)
    task_header_text = "Tasks (" + str(tasks.abs_length()) + ")"
    task_header.addstr(1, (col_width // 2) - (len(task_header_text) // 2),
                       task_header_text)
    task_header.border(0)

    date_header = stdscr.subpad(3, 30, 0, col_width)
    date_header.addstr(1, 11, "Scheduled")
    task_header.border(0)

    task_body = stdscr.subpad(max_y - 6, col_width, 3, 0)
    date_body = stdscr.subpad(max_y - 6, 30, 3, col_width)

    footer = stdscr.subpad(3, col_width + 30, max_y - 3, 0)
    footer.border(0)

    i = 1
    for task in tasks.get_selection(max_y - 7):
        try:

            scheduled_date = datetime.strptime(task["scheduled"],
                                               "%Y%m%dT%H%M%SZ")
            formatted_date = scheduled_date.strftime("%Y-%m-%d <%a> %H:%M:%S")
            date_body.addstr(i, 1, formatted_date)
        except (KeyError, TypeError):
            pass

        if render_deps:
            sel, prim = tasks.check_dep(i - 1)

            if prim and render_deps == 1:
                line_text = ">>> " + task["description"]
            elif prim and render_deps == 2:
                line_text = "<<< " + task["description"]
            elif sel:
                line_text = "--- " + task["description"]
            else:
                line_text = "    " + task["description"]
        else:
            line_text = task["description"]

        if i - 1 == cursor:
            task_body.addstr(i, 1, line_text, A_STANDOUT)
        else:
            task_body.addstr(i, 1, line_text)

        i += 1

    task_header.border(0)
    date_header.border(0)
    task_body.border(0)
    date_body.border(0)

    task_header.noutrefresh()
    date_header.noutrefresh()
    task_body.noutrefresh()
    date_body.noutrefresh()

    doupdate()

    return footer


# Yes, I know there's probably a better way, I don't care
def set_scheduled_date(stdscr, task, max_y):
    w = TaskWarrior()

    stdscr.move(max_y - 2, 1)
    curs_set(True)
    echo()

    new_date = stdscr.getstr().decode()

    if new_date is None or len(new_date) == 0:
        task["scheduled"] = None
    else:
        input_date = datetime.strptime(new_date, "%Y-%m-%d")
        task["scheduled"] = input_date.strftime("%Y%m%dT000000Z")

    w.task_update(task)

    curs_set(False)
    noecho()


def update_deps(deps, dep_mode):
    w = TaskWarrior()

    if dep_mode == 1:
        _, task = w.get_task(uuid=deps[0])
        dep = ""
        for uuid in deps[1]:
            if len(dep) != 0:
                dep += ","

            dep += uuid

        task["depends"] = dep
        w.task_update(task)
    elif dep_mode == 2:
        for dep in deps[1]:
            _, task = w.get_task(uuid=dep)
            try:
                task["depends"] += "," + deps[0]
            except KeyError:
                task["depends"] = deps[0]
            w.task_update(task)


def scheduler(stdscr):
    noecho()
    curs_set(False)

    max_y, max_x = stdscr.getmaxyx()
    max_cursor_pos = max_y - 9

    cursor = 0

    tasks = get_tasks()
    render_deps = 0
    run = True
    while run:

        draw_list(stdscr, tasks, cursor, render_deps)

        c = stdscr.getch()
        if c == ord("d"):
            pass
        elif c == ord("h"):
            if cursor == max_cursor_pos:
                if not tasks.at_end(max_cursor_pos):
                    tasks + 1
            else:
                cursor += 1
        elif c == ord("t"):
            if cursor == 0:
                tasks - 1
            else:
                cursor -= 1
        elif c == ord("n"):
            pass
        elif c == ord("g"):
            d = stdscr.getch()
            if d == ord("g"):
                tasks.begin()
                cursor = 0
        elif c == ord("G"):
            tasks.end(max_cursor_pos)
            cursor = max_cursor_pos
        elif c == ord("q"):
            run = False
        elif c == ord(" "):
            (_, primary) = tasks.check_dep(cursor)
            if primary or render_deps == 0:
                render_deps = (render_deps + 1) % 3
                tasks.clear_deps()
                tasks.toggle_dep(cursor, True, render_deps)
            else:
                tasks.toggle_dep(cursor)
        elif c == KEY_ENTER or c == 10 or c == 13:
            if render_deps:
                update_deps(tasks.get_deps(), render_deps)
                render_deps = 0
            else:
                set_scheduled_date(stdscr, tasks[cursor], max_y)
                tasks.refresh(tasks[cursor])


if __name__ == "__main__":
    #try:
        wrapper(scheduler)
    #except TaskwarriorError as err:
    #    msg = err.stderr.decode("utf-8").split("\n")[-1]
    #    print("Uncaught Taskwarrior Error: " + msg)
