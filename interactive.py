from curses import A_STANDOUT, curs_set, noecho

DELAYS = [" ", "B", "R", "N", "I", "W", "T"]


def write_items(stdscr, items, version, start, pos):
    stdscr.clear()

    stdscr.addstr(0, 0, version)
    stdscr.addstr(1, 0, items[0])

    (max_y, _) = stdscr.getmaxyx()

    if ((pos - start) + 3) >= max_y:
        start += 1
    elif pos < start:
        start -= 1

    for index, item in enumerate(items[1]):
        if index >= start:
            line = "[" + item[0] + "] " + item[1]["description"]
            if index == pos:
                stdscr.addstr((index - start) + 3, 0, line, A_STANDOUT)
            else:
                stdscr.addstr((index - start) + 3, 0, line)

        if ((index - start) + 3) >= (max_y - 1):
            break

    return start


def build_items(taskw, delay):

    # Structure of the items list:
    #   0: Name of the list
    #   1: Tasks found in list
    #       0: Delay to be set on task
    #       1: The task object itself
    tasks = taskw.load_tasks()["pending"]
    items = []

    if delay == "":
        pass
    elif delay == "T":
        for task in tasks:
            try:
                if "dotoday" in task["tags"] and "finance" not in task["tags"]:
                    items.append((" ", task))
            except KeyError:
                pass
    else:
        for task in tasks:
            if task["delay"] == delay and "finance" not in task["tags"]:
                items.append((" ", task))

    items = sorted(items, key=lambda task: task[1]["urgency"], reverse=True)

    if delay == "B":
        return "BACKLOG", items
    elif delay == "R":
        return "READY", items
    elif delay == "N":
        return "NEXT", items
    elif delay == "I":
        return "DOING", items
    elif delay == "W":
        return "WAITING", items
    elif delay == "T":
        return "DO TODAY", items
    else:
        return "NO DELAY SELECTED", items


def commit(taskw, items):
    for item in items:
        if item[0] != " ":
            item[1]["delay"] = item[0]
            taskw.task_update(item[1])


def controller(stdscr, taskw, version):
    noecho()
    curs_set(False)

    items = build_items(taskw, " ")

    pos = 0
    start = 0
    while pos != -1:
        start = write_items(stdscr, items, version, start, pos)

        c = stdscr.getch()
        if c == ord("d"):
            items[1][pos] = (DELAYS[DELAYS.index(items[1][pos][0]) - 1],
                             items[1][pos][1])
        elif c == ord("h"):
            pos += 1
            if pos >= len(items[1]):
                pos = len(items[1]) - 1
        elif c == ord("t"):
            pos -= 1
            if pos < 0:
                pos = 0
        elif c == ord("n"):
            items[1][pos] = (DELAYS[DELAYS.index(items[1][pos][0]) + 1],
                             items[1][pos][1])
        elif c == ord("B"):
            items = build_items(taskw, "B")
            pos = 0
        elif c == ord("R"):
            items = build_items(taskw, "R")
            pos = 0
        elif c == ord("N"):
            items = build_items(taskw, "N")
            pos = 0
        elif c == ord("I"):
            items = build_items(taskw, "I")
            pos = 0
        elif c == ord("W"):
            items = build_items(taskw, "W")
            pos = 0
        elif c == ord("T"):
            items = build_items(taskw, "T")
            pos = 0
        elif c == ord("c"):
            commit(taskw, items[1])
            items = build_items(taskw, " ")
        elif c == ord("q"):
            pos = -1
