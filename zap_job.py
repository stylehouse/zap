import threading
import os
import time
import subprocess
import json
import re
from pathlib import Path
phi = 1.613

from zap_less import truncated_job_output

def give_job_fixup(job,command):
    if 'podman run' in command:
        job["listen_out"].append(fixup_for_podmanrun_job)
    if 'py/ipfs.py' in command:
        job["listen_out"].append(fixup_for_ipfs_job)
    if 'ssh ' in command:
        job["listen_out"].append(fixup_for_ssh_job)
    
    # use the %restart job advice instead, less chatter
    #if 'lsyncd' in command:
    #    job["listen_out"].append(fixup_for_lsyncd_job)

# these two are left running re-parented when we quit zap
#  so these jobs cull their previous zombie selves
def fixup_for_ipfs_job(job,out):
    line = out['s']
    if out["std"] == "err":
        if 'Port 8000 is in use by another program. Either identify and stop that program' in line:
            run_fixup(job,r"kill $(ps fuax | grep '/python3 py/ipfs.py' | grep -v grep | awk 'NR==1{print $2}')")
def fixup_for_podmanrun_job(job,out):
    line = out['s']
    if out["std"] == "err":
        m = re.search(r'the container name "(\S+)" is already in use', line)
        if not m:
            m = re.search(r'Error: name "(\S+)" is in use: container already exists', line)
        if m:
            run_fixup(job,'podman rm -f {}'.format(m.group(1)))
# < move this nearer the config, or insist on hostname == vmname?
hostname_not_vmname = {"n":"nico"}
# no ssh -> wake up vm host vm
def fixup_for_ssh_job(job,out):
    line = out['s']
    if out["std"] == "err":
        if m := re.search(r'^ssh: connect to host (\S+) port (\d+): (No route to host|Connection refused)', line):
            host = m.group(1)
            vmname = hostname_not_vmname[host] if host in hostname_not_vmname else host
            run_fixup(job,' virsh start {}'.format(vmname))
            time.sleep(3)

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
    remark_job_ui(job,"🔧")
    # stop what we were doing
    job['process'].terminate()
    # make a heading and say line in job.output, with out.std=head
    iout(job,'fix'," oughtta fixup that with: {}".format(cmd))

    # should happen over there too
    if 'ssh_around' in job and cmd[0] != " ":
        cmd = job['ssh_around']+' '+json.dumps(cmd)
    
    # adding this other command to job.output
    run_job(job,cmd)
    if job["exit_code"]:
        # < never happens? shouldn't be trusted?
        remark_job_ui(job,"🔥")
        iout(job,'fix',"🔥fixup failed!🔥🔥🔥")
        time.sleep(0.3)
        #return

    # < report errors (exit code or any stderr) into job.fixup, so the ui say failure
    # retry job
    remark_job_ui(job,"🔧↺")
    iout(job,'fix'," ↺ fixup applied! restarting")
    job.pop("unseen_err", None)
    run_job(job)


def restart_job(job):
    # stop what we were doing
    job['process'].terminate()

    # backflip logo in job label
    remark_job_ui(job,"↺")
    #  and marked in job output
    iout(job,'fix'," ↺ manual restart")

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

def diag(s):
    #print(s)
    1
def run_job(job,actual_cmd=None,sleepytime=None):
    i = job["i"]
    command = actual_cmd or job["command"]
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
    output_handlers(job,process)
    
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
    slow = freq(0.1)
    # from the check_jobs() thread
    def check1s():
        # schedule slower checks
        if slow():
            check1m()
        # watch for falldown
        check_exit_code(job)
    
    def check1m():
        check_truncate_job_output(job)
    
    job["check1s"] = check1s

def output_handlers(job,process):
    def eatline (ch,line):
        # < do we want the ^ + and \n$
        # seem to do \n before turning off TerminalColors, just remove it
        line = re.sub("\n","",line)
        out = iout(job,ch,line.strip())
        # downstreams to have in this thread eg fixup
        for cb in job["listen_out"]:
            cb(job,out)
    def readaline(ch,std):
        linesing = iter(std.readline, "")
        for line in linesing:
            eatline(ch,line)
    def dostdout():
        readaline('out',process.stdout)
    def dostderr():
        readaline('err',process.stderr)
    # it seems the job thread (from ThreadPoolExecutor())
    #  becomes deadlocked given both of these to stream
    threading.Thread(target=dostdout).start()
    threading.Thread(target=dostderr).start()
    
def check_truncate_job_output(job):
    if len(job["output"]) > 12000:
        # truncating output here thirds our memory leakage
        job["output"] = job["output"][-6000:]
        truncated_job_output(job)

def check_exit_code(job):
    # notice it exit
    exit_code = job["process"].poll()

    if exit_code is not None:
        job["exit_code"] = exit_code

        # < perhaps shouldn't stop
        #   sometimes we get exit codes through here while stuff is still running
        #   see README / caveats / exits
        job["check1s"] = lambda: 1

        # when the job produces an error code?
        if 'restart' in job:
            remark_job_ui(job,"↺")
            iout(job,'fix'," ↺ job restart")
            # we are the check_jobs thread currently
            # Create a new thread and call run_job(job) within that thread
            threading.Thread(target=run_job, args=[job,None,'sleepy']).start()
    
# 3s remark drawn in draw_job_label()
def remark_job_ui(job,say):
    def later(say):
        time.sleep(phi)
        if "notice" in job and job["notice"] == say:
            del job["notice"]
    job["notice"] = say
    threading.Thread(target=later, args=[say]).start()

# for a loop full of if branches going off at different intervals
def freq(hz):
    hence = 0
    period = 1/hz
    def when():
        nonlocal hence
        if time.time() - hence > period:
            hence = time.time()
            return 1
    return when
