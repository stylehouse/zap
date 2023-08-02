import curses
import tempfile
import threading
import signal
import time
import subprocess
import os

def out_to_line(out):
    ind = '   '
    if out["std"] == 'err':
        ind = '!! '
    
    if out["std"] == 'fix':
        ind = '🔧  '
    
    line = ind + out["s"] + "\n"
    
    return line

terminatables = []
# kill less on Ctrl+C
def sigint_handler(signal, frame):
    killall()
    pass
def killall():
    for ism in terminatables:
        ism()

less_interruptables = []
def truncated_job_output(job):
    # can we simply:
    job["reless_please"] = 1
    killall()

    # < GOING naive civility of talking about the truncation
    # < if the file could be replaced, less might follow better than it does a truncation
    #   haven't tried --follow-name.
    # for jobless in less_interruptables:
    #     if jobless["job"] != job:
    #         continue
    #     jobless["interrupt"].set()

def less_job(stdscr,job):
    # End curses.
    curses.endwin()

    tmp = tempfile.NamedTemporaryFile()
    stop_less_event = threading.Event()
    trunc_less_event = threading.Event()
    jobless = {"job":job, "interrupt":trunc_less_event}
    less_interruptables.append(jobless)

    # fork to write job.output stream for less to read
    index = 0  # Keep track of the last processed index in job.output
    def write_thread(tmp,stop_less_event):
        index = 0  # Keep track of the last processed index in job.output
        while not stop_less_event.is_set():
            if trunc_less_event.is_set():
                # < GOING this is currently worked around in truncated_job_output()
                # according to https://python.hotexamples.com/examples/tempfile/TemporaryFile/truncate/python-temporaryfile-truncate-method-examples.html
                #  not in docs: https://docs.python.org/3/library/tempfile.html
                tmp.seek(0)
                tmp.truncate()
                # we will then write all remaining lines out again
                index = 0
                # < implement a signal handler in less that does this?
                #os.kill(less_process.pid, signal.SIGUSR1)
            if len(job["output"]) > index:
                for out in job["output"][index:]:
                    line = out_to_line(out)
                    # line = line[:3] + str(int(out["time"]-time.time())) + line[3:]
                    tmp.write(line.encode("utf-8"))
                tmp.flush()  # Flush the buffer to ensure data is written to the file
                index = len(job["output"])
            time.sleep(0.1)  # Sleep for a short duration before checking for new items
    write_thread = threading.Thread(target=write_thread, args=[tmp,stop_less_event])
    write_thread.start()



    # Set the custom signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, sigint_handler)
    
    # Run `less` with the job output.
    #  on +F option,
    #   man less says "If a command line option begins with +" it " is taken to be an initial command"
    #    ie +G would simply seek to the end, +10g would go 10 lines down.
    #os.system("less -R +F {}".format(tmp.name))
    less_process = subprocess.Popen(["less", "-R", "+F", tmp.name])
    terminator = lambda: less_process.terminate()
    terminatables.append(terminator)
    less_process.communicate()  # Wait for the less process to complete
    terminatables.remove(terminator)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Signal the thread to finish.
    stop_less_event.set()
    less_interruptables.remove(jobless)
    
    # if developing around here
    #  possible error message sitting in the terminal after less before curses
    #  Ctrl-Z somewhere might show it too
    #time.sleep(0.23)

    # consider the matter settled
    job.pop("unseen_err", None)

    # Initialize curses again.
    stdscr = curses.initscr()
    if "reless_please" in job:
        # from truncated_job_output(), tmpfile+less must also truncate
        del job["reless_please"]
        less_job(stdscr,job)
    # Return stdscr back to the main loop (will view_systems())
    return stdscr
