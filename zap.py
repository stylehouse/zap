#!/usr/bin/env python3
import os
import time
import concurrent.futures
import threading
import subprocess
import sys
import re
import json
from pathlib import Path
os.environ["PYTHONUNBUFFERED"] = "1"

import zap_parser
import zap_ui

import pprint
def dd(data,depth=7):
    pp = pprint.PrettyPrinter(depth=depth)
    pp.pprint(data)

'''
    prompt:
        I want to automate running and monitoring all these commands.

        It needs to present an interface (in the terminal or gtk) showing things running normally, also everything should begin slowly. if anything makes unusual noise (learn what things usually do) it should bring that information into view, ie showing the user novel events.

        Here are several sequences of commands,
         the first is usually an ssh session the rest happen in
         then we wait observing the last command forever

    has nobody made a harness for this though,
     that unifies all the potential messaging these commands could emit
      certainly STDERR would be top priority
      perhaps with machine learning their expected output and scanning for novelty.

    caveats:
     ansiicolours
       are via `less -R`
       curses strings dont let them happen
     STDIN
       writes (via job["give_stdin"]) are not getting there
        if interrupted, the thread was apparently in: process.stdin.flush()
       we want something similar to:
        echo input | ssh gox -v 'perl test.pl'
        which in this case fails to echo our input
         while trying to convert the above to a one liner
         this weird behaviour came up:
            s@g:~$ echo that
            that
            s@g:~$ echo lep | perl -E "say qq{this:$_} while <>"
            this:that
         this is because $_ is being interpolated by the shell
          it is the last word of the last command
           ie what Esc-. will insert for you
     sudo
       password prompting must be avoided, see STDIN
        by editing /etc/sudoers, and adding something like:
         someuser   ALL=(ALL:ALL) NOPASSWD: /bin/echo "non"
        at the end
       it might work for you!
        scars left in, see sudostdin
        
    
'''















# By using the r prefix before the opening quotes ('''),
#  the string is treated as a raw string
#  and backslashes within the string are not treated as escape characters.
cmd_source = r'''
    # letz_dev
       lsyncd py/letz.lsyncdconf
        echo yep
        %restart
         #    this seems to get a SIGINT from the UI doing less
         # fast code deployment over ssh
         #  inotify on s: -> replication -> inotify on gox (-> vite etc)
         # unlike sshfs ~~ ftp needing ongoing ls
       ssh -A gox
        sshfs s:/media/s/Elvis/Photo v
         # s is 192.168.122.1, virbr0 on sa
         # v is the mount at gox:~s/v, goes into:
       ssh gox
        cd src/letz
        podman run -v ~/v:/v:ro -v .:/app:exec -p 5000:5000 --rm -it --name pyt py bash -c './yt.sh'
       ssh gox
        cd src/letz
        podman run -v .:/app:exec -p 8000:8000 --rm -it --name cos1 cos npm run dev -- --port 8000 --host 0.0.0.0

       code .
        # taken to this to dev modern javascript
       echo chromium \
        http://192.168.122.92:5000/dir/ \
        http://192.168.122.92:8000/
        # remove echo to enable

# trusted environs:
        
    # style_dev
       cd ~/stylehouse
        ./serve.pl
        %restart
       echo chromium \
        http://editong.localhost:1812/
        # edits javascript as perl
    # ipfs
       ssh sa
        cd src/letz
        py/ipfs.py
        # < why can't this be %restart? it detects exit immediately, as flask daemonises..?
        # < seems to output less via zap
        #   should we seem more like a terminal to it?
        
       
    # init
     # see INSTALL
       lsyncd py/letz.lsyncdconf
         # < avoid sleep: when is this ready?
       ssh gox
        sleep 1
        cd src/letz
        podman build -t cos .
        podman build -t py py

        
    # nico
       ssh n
        sudo mount -t 9p -o trans=virtio allmusic allmusic/
         # input: share, is a qemu filesystem%%type="mount"/source,target,readonly
         #  note the readonly
       cd ~
        sshfs n:Downloads/ Mail
         # output: to sort
       ssh -X n
        cd Downloads/
         # it sometimes drops files where it cd?
        nicotine
         # a python window
       upnpc -r 2234 TCP
        ssh -L 0.0.0.0:2234:n:2234 n
         # let peer in

    # test
       cd ~/stylehouse
        ./serve.pl
       ssh gox
         # < fixup /no route/
         #       virsh start gox
         #       fixup /bridge helper: stderr=failed to create tun device: Operation not permitted/
         #           # freshly installed something needs:
         #           sudo chmod u+s /usr/lib/qemu/qemu-bridge-helper
        echo rop
        #perl test.pl
        sudo /bin/echo "non"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooongnesses!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Several!"
        sleep 1
        echo "Completo!"
       echo "noncommand"
        sleep 2
        ll non-command
         # 'll' is not found, exit code 127
        echo "Very nearly!"
        %restart
       echo hi
        lsyncd py/letz.lsyncdconf
        sleep 1
        %restart
       echo "non-existence"
        ls v
       echo "an-exit-four"
        exit 4
        echo "Not nearly!"
       echo "a-good-time"
        echo "here"
        sleep 0.2
        echo "there"
        sleep 0.13
        echo "around"
'''




















systems = zap_parser.parse_cmd_source(cmd_source)
# Iterate over systems and create titles for jobs
for system in systems:
    jobs = system['jobs']
    for job in jobs:
        cmds = job['cmds']
        job['t'] = zap_parser.create_job_title(job,cmds)


# try one only
only = sys.argv[1] if len(sys.argv)>1 else None
if only:
    systems = [system for system in systems if system['t'] == only]
else:
    systems = [system for system in systems if not system['t'] == 'nico']
    systems = [system for system in systems if not system['t'] == 'test']
    systems = [system for system in systems if not system['t'] == 'init']

job_i = 0
i_job = {}
for system in systems:
    jobs = system['jobs']
    for job in jobs:
        cmds = job['cmds']
        match = re.search(r'^ssh ',cmds[0])
        ssh_around = ''
        if match:
            ssh_around = cmds.pop(0)

        if 0 and 'sudostdin':
            # sudo to accept password on stdin
            # < we should note which cmd had it,
            #    check that cmd is currently executing via a supervisory ssh 'ps faux'
            cmds = [cmd.replace("sudo ", "sudo -S ") for cmd in cmds]
        job['cmds'] = cmds

        # we lose their individuality:
        #  each exit code
        #  each slice of stdout
        cmds = ' && '.join(cmds)
        # it all happens over there if cmds starts with ssh
        #  eg ssh -X n 'cd Downloads; nicotine'
        if ssh_around:
            cmds = ssh_around+' '+json.dumps(cmds)
            job['ssh_around'] = ssh_around
        
        job["command"] = cmds
        job["i"] = job_i
        i_job[job_i] = job
        job_i = job_i + 1








def give_job_fixup(job,command):
    if 'podman run' in command:
        job["listen_out"].append(fixup_for_podmanrun_job)
    if 'py/ipfs.py' in command:
        job["listen_out"].append(fixup_for_ipfs_job)
    # use the %restart job advice instead, less chatter
    #if 'lsyncd' in command:
    #    job["listen_out"].append(fixup_for_lsyncd_job)

# these two are left running re-parented when we quit zap:

def fixup_for_ipfs_job(job,out):
    line = out['s']
    if out["std"] == "err":
        if 'Port 8000 is in use by another program. Either identify and stop that program' in line:
            run_fixup(job,r"kill $(ps fuax | grep '/python3 py/ipfs.py' | grep -v grep | awk 'NR==1{print $2}')")
def fixup_for_podmanrun_job(job,out):
    line = out['s']
    if out["std"] == "err":
        if m := re.search(r'the container name "(\S+)" is already in use', line):
            run_fixup(job,'podman rm -f {}'.format(m.group(1)))
            # < subsequent steps?

# < GOING? just being a %restart job good enough?
#   might be some outage while "fading"
# was affected by Ctrl+C to the UI doing less
#  as is serve.pl
def fixup_for_lsyncd_job(job,out):
    line = out['s']
    if out["std"] == "out":
        if '--- INT signal, fading ---' in line:
            run_fixup(job,'echo nothing')
            # < subsequent steps?



def run_fixup(job,cmd):
    # stop what we were doing
    job['process'].terminate()
    # make a heading and say line in job.output, with out.std=head
    iout(job,'fix'," oughtta fixup that with: {}".format(cmd))

    # should happen over there too
    if 'ssh_around' in job:
        cmd = job['ssh_around']+' '+json.dumps(cmd)
    
    # adding this other command to job.output
    run_job(job,cmd)
    if job["exit_code"]:
        iout(job,'fix',"🔥fixup failed!🔥stopping🔥🔥")
        return

    # < report errors (exit code or any stderr) into job.fixup, so the ui say failure
    # retry job
    iout(job,'fix'," fixup applied! retrying")
    job.pop("unseen_err", None)
    run_job(job)

    
# < if job was not argumented this would still work
#    but all output would end up in the last job
#   how to make such borrowing fatal? if I remove the for job in ... above?
def iout(job,ch,s):
    out = {"std":ch,"s":s,"time":time.time()}
    job["output"].append(out)
    if ch == 'err':
        job["unseen_err"] = 1
    return out

# Get the directory path of the current script
script_path = os.path.abspath(__file__)
# you might link to zap.py from nearby
# < possibly where cmd_source (systems config) might live
if os.path.islink(script_path):
    script_path = os.path.realpath(script_path)
script_dir = os.path.dirname(script_path)
# Construct the full path to zap_run.pl
zap_run_path = os.path.join(script_dir, 'zap_run.pl')

def run_job(job,actual_cmd=None,sleepytime=None):
    i = job["i"]
    command = actual_cmd or job["command"]
    def diag(s):
        #print(s)
        1
    if sleepytime:
        # job.restart should not burn cpu
        time.sleep(2)
    if actual_cmd:
        diag(f"[{i}] other: "+ command)

    else:
        diag(f"[{i}] starts: "+ job["t"])

    # the ui shall tail this
    # [{std:'out',s:'hello\n',time:...}+]
    if not 'output' in job:
        job["output"] = []
    # downstreams to have in this thread eg fixup
    job["listen_out"] = []
    # attach GOFAI fixup actuators
    #  you can fixup fixups too so we pass command
    give_job_fixup(job,command)

    # json strings are shell-compatible
    #  in perl this will be $ARGV[0], not needing decode
    zap_command = zap_run_path+" "+json.dumps(command)

    process = job["process"] = subprocess.Popen(zap_command, shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                bufsize=1)
    def readaline(ch,std):
        linesing = iter(std.readline, "")
        for line in linesing:
            # < do we want the ^ + and \n$
            # seem to do \n before turning off TerminalColors, just remove it
            line = re.sub("\n","",line)
            out = iout(job,ch,line.strip())
            diag(f"[{i}] std{ch}: "+out["s"])
            # downstreams to have in this thread eg fixup
            for cb in job["listen_out"]:
                cb(job,out)
    readaline('out',process.stdout)
    readaline('err',process.stderr)

    # stdin
    def inN(N):
        if not "wrote_stdin" in job:
            job["wrote_stdin"] = 0
        
        for l in N:
            job["wrote_stdin"] = job["wrote_stdin"] + 1
            process.stdin.write(l + "\n")
            print("Wrote to "+job["t"]+":     '"+l+"'")
        # flush reduces latency and the need to \n$, but the receiver might be waiting for one?
        process.stdin.flush()
    job["give_stdin"] = inN
    # < multiple sudos in a command should work
    #   password fed only the first time
    if 0 and "sudostdin" and 'sudo ' in command:
        host = job["on_host"]
        if not host:
            raise ValueError("only know vms")
        file_path = Path("secrets/sudo-on-"+host)
        password = file_path.read_text()
        if not password:
            raise ValueError("dont know "+file_path)
        #
        time.sleep(0.4)
        inN([password])

    job["exit_code"] = None
    
    def check1s():
        exit_code = process.poll()
        if exit_code is not None:
            diag(f"[{i}] trouble! code:"+str(exit_code))
            job["exit_code"] = exit_code
            diag(f"[{i}] finito")
            job["check1s"] = lambda: 1
            # when the job produces an error code?
            if 'restart' in job:
                iout(job,'fix'," ↺ job restart")
                # we are the check_jobs thread currently
                # Create a new thread and call run_job(job) within that thread
                threading.Thread(target=run_job, args=(job,None,'sleepy')).start()
    job["check1s"] = check1s




def all_systems_go():
    # < figure out if any of this can be less terrifying
    # max_workers so that all jobs can stay happening
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit each command to the executor
        future_results = []

        for system in systems:
            jobs = system['jobs']
            for job in jobs:
                future_results.append(executor.submit(run_job, job))

        # Process the results as they become available
        for future in concurrent.futures.as_completed(future_results):
            result = future.result()


# run commands without blocking the UI
threading.Thread(target=all_systems_go).start()

# watch for exit codes etc
def check_jobs():
    while True:
        for system in systems:
            jobs = system['jobs']
            for job in jobs:
                cmds = job['cmds']
                job['t'] = zap_parser.create_job_title(job,cmds)
                if "check1s" in job:
                    check = job["check1s"]
                    check()
        time.sleep(0.4)
threading.Thread(target=check_jobs).start()

# Run the UI
zap_ui.begin(i_job,job_i,systems)



#dd(systems)