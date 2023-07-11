# zap
supervisor running|monitoring all these commands

https://github.com/stylehouse/zap/assets/20439374/0800f95b-b321-46e8-a03d-103786e080b6

## description

runs the commands specified in zap.py. they a split into systems, so individual `./zap.py $system` can be run, or all will be.

I used it to make a dev environment for [letz](https://github.com/stylehouse/letz), instead of a village of terminals to constantly rebuild.

- can fixup common errors with the commands
- has curses interface which becomes `less -R` (supports ansii colours and hyperlinks) when looking at commands (not a fully-fledged terminal)

## installation

* copy somewhere
* adjust the commands specified in `zap.py`
  * various podman-build are implied

should be secure, only uses core python.

## long description

A terminal program to automate running and monitoring all these commands.

It to present an interface (curses) listing things running normally.

Run a bunch of commands at one, tailing the outputs.

Sysadmin glue code for clusters of vms with various sshfs etc commands involved in their running.

## examples

Here in `zap.py` are several sequences of commands,
    the first is usually an ssh session the rest happen in
    then we wait observing the last command forever

Please look to the wiki to pick up or drop off more examples. Think of it as social media for software.

## caveats

the podman-run commands seem to exit(0) while they're still outputting stuff. [who knows why?](https://stackoverflow.com/questions/881388/double-fork-when-creating-a-daemon/5386753#5386753)

see `zap.py`

# TODO

## restart failed jobs|systems
without restarting `zap.py`.
restart 2x daily: memleak mode.

## dependencies
we could need A finished before B starts. perhaps the cmd_source sets or gets markers.

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
if anything makes unusual noise (learn what things usually do) it should bring that information into view, ie showing the user novel events.

## command marketplace
how do everyone's technical struggles fruit.

## fixup marketplace
the general-knowledge version of the above.

sequences of commands that diagnose & rectify situations.

should distribute only chunks of cmd_source, which would have a general-knowledge section besides the systems definition.

# support

`Third World Software Co` is here to help! Let me know.
