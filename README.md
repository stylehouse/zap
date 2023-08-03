# zap
supervisor running|monitoring all these commands

https://github.com/stylehouse/zap/assets/20439374/0800f95b-b321-46e8-a03d-103786e080b6

# description

Runs and watches commands specified in **zap.py**, for bringing up flocks of programs, some management.

- can fixup common errors with the commands
- curses interface which becomes `less -R` (supports ansii colours) when looking in to job output (not a proper terminal), Ctrl+C twice to return from it.
- press **R** to restart a job
- Jobs (of commands) are grouped into systems, so individual `./zap.py $system` can be run, or most will be.
- all jobs at once, each job's commands in sequence (joined by &&)

Instead of a village of terminals to constantly rebuild.

# similar tools

Not sure. I have only heard of "the supervisor process" being a project-bound minimalist perl script or so.

Keen on the idea of healing a command with another command automatically. Computers should have developed a receptor for gathering this knowledge by now, so here it is.

**systemd** ~~ zap for LinuxSystem clutter: switches services on, might monitor, not sure.

**tmux** ~~ a bunch of terminal sessions to show you, predefined and instantiated.

**kubernetes** ~~ zap orchestrating vms with ports and mounts is like infrastructure as code.

# installation

* copy somewhere
* adjust the commands specified in `zap.py` for yourself
  * various podman-build are implied

# long description

A terminal program to automate running and monitoring all these commands, having fixups for common error-response side-tracking.

It present an interface (curses) listing things running normally or catching fire.

Run a bunch of commands at once, tailing the outputs.

Sysadmin glue code for clusters of vms with various sshfs etc commands involved in their running.

# examples

In `zap.py` is configured several sequences of commands,
    the first is usually an ssh session the rest happen in,
    and we wait observing the command forever, unless it says **%restart**

Please look to the wiki to pick up or drop off more examples. Think of it as social media for software.

# caveats

When the UI shells out to **less** and we need to use Ctrl+C to exit it, this **SIGINT** affects **lsyncd** and **serve.pl** also (they auto-restart), despite being inside **zap_run.pl** which supposedly handles that signal.

We shell out to **less** for lack of putting ascii colour codes in curses.

## exits

The podman-run|ipfs commands seem to exit(125|0) while they're still outputting stuff. [who knows why?](https://stackoverflow.com/questions/881388/double-fork-when-creating-a-daemon/5386753#5386753) This means they can't %restart, because they always seem to need restarting.

These commands are left running when zap exits, reparented to `/lib/systemd/systemd --user`. Via fixups they won't get in the way of a new zap instance.

Needs knowledge. Ideally we handle Ctrl+C for zap exit and end jobs smoothly. Even knowing the process tree to track cpu|mem would be nice.

## other

Periodically truncates **job.output** to 6000 lines.

See **TODO / clear exit code on restart**, the UI may have stale exit codes.

For more caveats, see `zap.py`

# TODO

## rewrite in golang
lots of nice Console-UI things are over there

## clear exit code on restart
The fixups can't be gauged for failure, eg `podman rm -f cos1` often errs "container has already been removed", meaning good.

## logger
Python errors are obscured by curses but apparently this will get them, avail them as a job.

## memleak mode
restart job 2x daily: memleak mode

## port forwarding
Find out how to efficiently port forward (without `SSH -L`)

## dependencies
Could need A finished before B starts. perhaps the cmd_source sets or gets markers. do **%early** before others?

Achieve **job.ready**=True when exit(0) or eg **lsyncd** could have a fixup notice when it says Ready, since it runs forever.

Workaround: `sleep 1` before the **%later** jobs. Potential very elsewhere to run the dev server while still copying its files into place for the first time.

## improve view_systems
make the system/job/cmd hierarchy clearer, toggle them on|off...

more indicators, eg that unseen output|errors exist per job

## improve view_job
while in the less of `less_job()`, indication of action in other jobs should be visible. lose less.

## ssh in to watch progress
getting the pid of the remote shell, then with `ps faux`, figure which cmd in the job we are doing, take cpu|mem stats, etc.

we currently dont know which cmd of a job failed, eg `ssh n 'any && of && these && coulda'`.

jobs could `echo PID:$$` first so we can find sshd/*:cmds in `ps faux`, for all jobs on n: etc, and then `echo some-marker` to put pagination markets in the output. `out%%ch=cmd,s:cmd`

## novelty analysis
learn what normal output looks like for each command.

if anything makes unusual noise it should bring that information into view, ie showing the user novel events.

## command marketplace
how do everyone's technical struggles fruit.

Please look to the wiki to pick up or drop off more examples. Think of it as social media for software.

## fixup marketplace
the general-knowledge version of the above.

sequences of commands that diagnose & rectify situations.

should distribute only chunks of cmd_source, which would have a general-knowledge section besides the systems definition.

# see also

The example dev environment is for [letz](https://github.com/stylehouse/letz)

# support

`S Group` is here to help! Let me know.
