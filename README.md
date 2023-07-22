# zap
supervisor running|monitoring all these commands

https://github.com/stylehouse/zap/assets/20439374/0800f95b-b321-46e8-a03d-103786e080b6

## description

runs the commands specified in zap.py. they a split into systems, so individual `./zap.py $system` can be run, or all will be.

I used it to make a dev environment for [letz](https://github.com/stylehouse/letz), instead of a village of terminals to constantly rebuild.

- can fixup common errors with the commands
- has curses interface which becomes `less -R` (supports ansii colours and hyperlinks) when looking at commands (not a proper terminal)

## installation

* copy somewhere
* adjust the commands specified in `zap.py` for yourself
  * various podman-build are implied

## long description

A terminal program to automate running and monitoring all these commands, having fixups for common error-response side-tracking.

It present an interface (curses) listing things running normally or catching fire.

Run a bunch of commands at once, tailing the outputs.

Sysadmin glue code for clusters of vms with various sshfs etc commands involved in their running.

## examples

In `zap.py` is configured several sequences of commands,
    the first is usually an ssh session the rest happen in,
    and we wait observing the command forever.

Please look to the wiki to pick up or drop off more examples. Think of it as social media for software.

## caveats

the podman-run commands seem to exit(0) while they're still outputting stuff. [who knows why?](https://stackoverflow.com/questions/881388/double-fork-when-creating-a-daemon/5386753#5386753)

You cannot restart commands via the UI, the jobs must be programmed to **%restart** or have a fixup for a particular behaviour to restart after.

See **TODO / clear exit code on restart**, the UI may have stale exit codes.

The UI's shelling out to **less**:
 - (which we must kill our way out of with Ctrl+C) leaks that SIGINT to eg lsyncd. Perhaps it should be via **zap_run.pl**?
 - seems to prevent the job thread from restarting any process.

For more caveats, see `zap.py`

# TODO

## rewrite in golang
lots of nice Console-UI things are over there

## we dont exit podman-run properly
Handle Ctrl+C for zap exit, terminate() jobs first.

## clear exit code on restart
The fixups can't be gauged for failure, eg `podman rm -f cos1` often errs "container has already been removed", meaning good.

## restart failed jobs|systems
Besides making the job one that **%restart**s, operator should be able to restart jobs at will, without restarting `zap.py`.

restart 2x daily: memleak mode.

## dependencies
we could need A finished before B starts. perhaps the cmd_source sets or gets markers.

do **%early** before others? mostly for lsyncd being done, so it could have a fixup to make itself 

## improve view_systems
make the system/job/cmd hierarchy clearer

more indicators, eg that unseen output|errors exist per job

## improve view_job
while in the less of `less_job()`, indication of unseen errors occuring in other jobs should be visible. make out.ch='zap' to clearly layer those bits of the output.

## ssh in to watch progress
getting the pid of the remote shell, then with `ps faux`, figure which cmd in the job we are doing, take cpu|mem stats, etc.

we currently dont know which cmd of a job failed, eg `ssh n 'any && of && these && coulda'`.

jobs could `echo PID:$$` first so we can find sshd/*:cmds in `ps faux`, for all jobs on n: etc, and then `echo some-marker` to put pagination markets in the output. `out%%ch=cmd,s:cmd`

## novelty analysis
learn what normal output looks like for each command.

if anything makes unusual noise it should bring that information into view, ie showing the user novel events.

## command marketplace
how do everyone's technical struggles fruit.

## fixup marketplace
the general-knowledge version of the above.

sequences of commands that diagnose & rectify situations.

should distribute only chunks of cmd_source, which would have a general-knowledge section besides the systems definition.

# support

`Third World Software Co` is here to help! Let me know.
