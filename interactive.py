#!/usr/bin/python3

from curses import (A_STANDOUT, curs_set, doupdate,
                    echo, KEY_ENTER, noecho, ungetch, wrapper)
from datetime import date, datetime
from taskw import TaskWarrior


from taskw.exceptions import TaskwarriorError


class TaskList:
    class Iterator:
        def __init__(self, task_list, max_count=-1):
            self.task_list = task_list
            self.index = task_list._offset
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

    def __init__(self, task_list=[], offset=0):
        self._task_list = task_list

        if offset == 0 or offset < task_list(len):
            self._offset = offset
        else:
            self._offset = 0

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

    def end(self, size):
        self._offset = len(self._task_list) - (size + 1)

    def get_selection(self, size):
        return TaskList.Iterator(self, size)

    def length(self):
        return len(self._task_list) - self._offset

    def remove_task(self, index):
        return self._task_list.pop(index)


def get_tasks():
    tasks = {"unscheduled": TaskList()}

    w = TaskWarrior()
    all_tasks = w.load_tasks()["pending"]

    tasks = TaskList()

    for task in all_tasks:
        tasks.add_task(task)

    return tasks


#def build_columns(stdscr, tasks, from_date, curs_y, curs_x):
#    key = ["unscheduled"]
#    for idx in range(1, 4):
#        index_date = from_date + timedelta(days=(idx - 1))
#        key.append(index_date.strftime("%Y-%m-%d"))
#
#    max_y, max_x = stdscr.getmaxyx()
#    col_width = max_x // 4
#
#    headers = []
#    for idx in range(0, 4):
#        headers.append(stdscr.subpad(3, col_width, 0, col_width * idx))
#        headers[idx].addstr(1, 1, key[idx].upper())
#        headers[idx].border(0)
#
#    columns = []
#    for i in range(0, 4):
#        task_list = tasks.get(key[i], None)
#        columns.append(stdscr.subpad(max_y - 3, col_width,
#                                     3, col_width * i))
#        if task_list:
#            for j in range(0, max_y - 5):
#                columns[i].addstr(j + 1, 1,
#                                  task_list[j]["description"][:col_width])
#        columns[i].scrollok(True)
#        columns[i].border(0)
#
#   return headers, columns


def draw_list(stdscr, tasks, cursor):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    if max_x > 130:
        col_width = 100
    else:
        col_width = max_x - 30

    task_header = stdscr.subpad(3, col_width, 0, 0)
    task_header.addstr(1, (col_width // 2) - 2, "Tasks")
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
        except KeyError:
            pass

        if i - 1 == cursor:
            task_body.addstr(i, 1, task["description"], A_STANDOUT)
        else:
            task_body.addstr(i, 1, task["description"])

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

    if len(new_date) == 0:
        task["scheduled"] = None
    else:
        input_date = datetime.strptime(new_date, "%Y-%m-%d")
        task["scheduled"] = input_date.strftime("%Y-%m-%dT00:00Z")

    w.task_update(task)

    curs_set(False)
    noecho()

    _, task = w.get_task(uuid=task["uuid"])

    return task


def scheduler(stdscr):
    noecho()
    curs_set(False)

    max_y, max_x = stdscr.getmaxyx()
    max_cursor_pos = max_y - 9

    tasks = get_tasks()
    cursor = 0

    run = True
    while run:
        draw_list(stdscr, tasks, cursor)

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
        elif c == KEY_ENTER or c == 10 or c == 13:
            tasks[cursor] = set_scheduled_date(stdscr, tasks[cursor], max_y)

if __name__ == "__main__":
    try:
        wrapper(scheduler)
    except TaskwarriorError as err:
        msg = err.stderr.decode("utf-8").split("\n")[-1]
        print("Uncaught Taskwarrior Error: " + msg)
