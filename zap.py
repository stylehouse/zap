#!/usr/bin/env python3
import os
import time
import concurrent.futures
import threading
import subprocess
import sys
import re
import json
os.environ["PYTHONUNBUFFERED"] = "1"

import zap_parser
import zap_ui
from zap_job import run_job

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
    # see letz.git 518fd82d504
    #    lsyncd py/stylehouseY.lsyncdconf
    #     echo yep
    #     %restart
    #    lsyncd py/letz.lsyncdconf
    #     echo yep
    #     %restart
         #    this seems to get a SIGINT from the UI doing less
         # fast code deployment over ssh
         #  inotify on s: -> replication -> inotify on gox (-> vite etc)
         # unlike sshfs ~~ ftp needing ongoing ls
    #    ssh -A gox
    #     sshfs s:/media/s/Elvis/Photo v
         # s is 192.168.122.1, virbr0 on sa
         # v is the mount at gox:~s/v, goes into:
       # sa is the host of podman. /etc/hosts sa to localhost if none.
       cd ~/src/letz
        podman run -v ~/v:/v:ro -v .:/app:exec -p 5000:5000 --rm -it --name py1 py bash -c 'python py/serve.py'
       cd ~/src/letz
        podman run -v .:/app:exec -p 3000:3000 --rm -it --name cos1 cos bash -ci 'npm run dev -- --port 3000 --host 0.0.0.0'
        # this may be better to run directly when compiler changes happen
        #   need to restart vite after any error.
        #   which you do by pressing 'r' when you have a real terminal
        #    faster restart than podman assassinations

       /usr/share/codium/codium ~/src/letz/
        # --ozone-platform=wayland
        #%restart
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
        cd ~/src/letz
        podman run -v .:/app:exec -p 8000:8000 --rm -it --name py2 py bash -c 'python py/ipfs.py'
        # < why can't this be %restart? it detects exit immediately, as flask daemonises..?
        # < seems to output less via zap
        #   should we seem more like a terminal to it?
        
       
    # init
     # see INSTALL
     # < avoid sleep: when is the previous job ready?
     # < this seems to end up using 20G of disk on gox
     #   perhaps we should make cos FROM bun, and do imagemagick in the py container.
       ssh sa
        # lsyncd expects src/ to exist
        mkdir -p src/letz
       lsyncd py/letz.lsyncdconf
       ssh sa
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
       upnpc -r 2235 TCP
        ssh -L 0.0.0.0:2235:n:2235 n
         # let peer in

    # test
       #journalctl -xef
       # echo yep
         # < no colour, untested
       #cd ~/stylehouse
       # ./serve.pl
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
       python garbagio.py
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











def all_systems_go():
    for system in systems:
        jobs = system['jobs']
        for job in jobs:
            threading.Thread(target=run_job, args=[job]).start()


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