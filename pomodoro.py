from taskw import TaskWarrior
from time import sleep
from datetime import timedelta
from curses import (noecho, curs_set)
from subprocess import (run, DEVNULL)


def print_time(stdscr, task, clock):
    stdscr.clear()

    minutes = clock.seconds // 60
    seconds = clock.seconds % 60

    s = f'0{seconds}' if seconds < 10 else f'{seconds}'
    m = f'0{minutes}' if minutes < 10 else f'{minutes}'

    stdscr.addstr(0, 0, f'Pomodoro: {m}:{s}')
    stdscr.addstr(2, 0, f'{task["description"]} '
                        f'({task.get("pom", 0)}'
                        f'/{task.get("effort", 0)})')
    stdscr.refresh()


def timer(stdscr, task_id, minutes=25):
    noecho()
    curs_set(False)

    tw = TaskWarrior(marshal=True)
    task = tw.get_task(id=task_id)[1]
    clock = timedelta(minutes=minutes)

    while clock > timedelta():
        clock -= timedelta(seconds=1)
        print_time(stdscr, task, clock)
        sleep(1)

    task["pom"] = task.get("pom", 0) + 1
    tw.task_update(task)
    run(["zenity",
         "--info",
         "--title=Pomodoro",
         "--text=Pomodoro Finished."],
        stdout=DEVNULL,
        stderr=DEVNULL)
