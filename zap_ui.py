
import curses
import time
import textwrap
import threading
import pprint
def dd(data,depth=7):
    pp = pprint.PrettyPrinter(depth=depth)
    pp.pprint(data)

from zap_job import restart_job
from zap_less import less_job

def begin(i_job, job_i, systems):
    try:
        curses.wrapper(main, i_job, job_i, systems)
    except KeyboardInterrupt:
        curses.endwin()  # Reset the terminal before exiting

def dothing(job):
    threading.Thread(target=thred, args=[job]).start()
def thred(job):
    restart_job(job)


def main(stdscr,i_job,job_i,systems):
    # Initialize curses settings
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # for non-blocking stdscr.getch() (loop must sleep)
    stdscr.nodelay(1)
    # Define the dimensions of the interface
    rows, cols = stdscr.getmaxyx()

    # Initially selected row
    selected_row = 0

    # Draw the interface
    view_systems(stdscr, systems, selected_row)

    # Clear the screen
    stdscr.clear()
    # Event loop
    while True:
        key = stdscr.getch()

        # Handle key events
        if key == curses.KEY_UP:
            if selected_row > 0:
                selected_row -= 1
            else:
                # wrap up
                selected_row = len(i_job) - 1
        elif key == curses.KEY_DOWN:
            if selected_row < job_i - 1:
                selected_row += 1
            else:
                # wrap down
                selected_row = 0
        elif key == ord('R') or  key == ord('r'):
            job =  i_job[selected_row]
            threading.Thread(target=restart_job, args=[job]).start()
            stdscr.addstr(rows-2, 2, "job restarting")
        elif isenter(key):
            # look into selected command
            job = i_job[selected_row]
            stdscr = less_job(stdscr, job)

        # Redraw the interface
        view_systems(stdscr, systems, selected_row)

        # Refresh the screen
        stdscr.refresh()
        time.sleep(0.1)
        # Clear the screen
        stdscr.clear()

# view everything
#  list of jobs and their state
# < inc systems
def dotdotdotat(s,n):
    wrapped_text = textwrap.wrap(s,n)
    if len(wrapped_text) > 1:
        wrapped_text[0] += '...'
    if len(wrapped_text):
        return wrapped_text[0]
    return ""
    





def view_systems(stdscr, systems, selected_row):

    # Define the dimensions of the interface
    rows, cols = stdscr.getmaxyx()

    # Draw the list of jobs
    for system in systems:
        jobs = system['jobs']
        for job in jobs:
            i = job["i"]
            # hilight selection
            if i == selected_row:
                stdscr.attron(curses.color_pair(1))
            
            draw_job_label(stdscr,job,i)
            if i == selected_row:
                # turn off again
                stdscr.attroff(curses.color_pair(1))
    
    stdscr.addstr(rows-1, 0, "sel:"+str(selected_row))
    # Refresh the screen
    stdscr.refresh()

def draw_job_label(stdscr,job,i):
    rows, cols = stdscr.getmaxyx()

    # title
    stdscr.addstr(i, 0, "["+str(job["i"])+"] "+dotdotdotat(job["t"], cols - 23))

    col_status = cols - 15
    col_in = cols - 10
    col_weather = cols - 5
    # status
    if "check1s" in job:
        if job["exit_code"] is not None:
            if not job["exit_code"]:
                # 0 - good
                stdscr.addstr(i, col_status, "done")
            else:
                # 127 etc - bad
                stdscr.addstr(i, col_status, "exit("+str(job["exit_code"])+")")
    if "wrote_stdin" in job:
        much = job["wrote_stdin"]
        stdscr.addstr(i, col_in, "in:"+str(much))
    if not 'output' in job:
        # won't have stdin before starting command
        stdscr.addstr(i, col_in, "!yet?")
    if "unseen_err" in job:
        stdscr.addstr(i, col_weather, "🔥")
    if "notice" in job:
        says = job["notice"]
        stdscr.addstr(i, col_weather+1, says)


def isenter(key):
    return key == curses.KEY_ENTER or key == ord('\n')

