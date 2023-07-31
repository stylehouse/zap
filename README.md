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

When the UI shells out to **less** and we need to use Ctrl+C to exit it, this **SIGINT** affects **lsyncd** and **serve.pl** also (they auto-restart), despite being inside **zap_run.pl** which supposedly handles that signal.

Used **less** for lack of putting ascii colour codes in curses.

### buffering woes

For some commands, streaming output from the process seems to be limited to whichever **run_job() / readaline()** comes first: out or err, but not both.

For example, this job output shows only the STDOUT of this server fetching the same thing a few times:
```
   * Serving Flask app 'ipfs'
   * Debug mode: on
   File: ipfs/58/35ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd
   File: ipfs/58/35ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd
   File: ipfs/58/35ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd
   File: ipfs/58/35ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd
```

Then if we kill it from another terminal:
```kill $(ps fuax | grep '/python3 py/ipfs.py' | grep -v grep| awk 'NR==1{print $2}')```

All the STDERR suddenly comes in:
```
! WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
!! * Running on http://127.0.0.1:8000
!! Press CTRL+C to quit
!! * Restarting with stat
!! * Debugger is active!
!! * Debugger PIN: 831-394-925
!! 127.0.0.1 - - [31/Jul/2023 15:42:08] "GET /5835ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd HTTP/1.1" 200 -
!! 127.0.0.1 - - [31/Jul/2023 15:42:09] "GET /5835ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd HTTP/1.1" 200 -
!! 127.0.0.1 - - [31/Jul/2023 15:42:10] "GET /5835ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd HTTP/1.1" 200 -
!! 127.0.0.1 - - [31/Jul/2023 15:42:10] "GET /5835ea2230e6b4ee2b6c3645038ccaa54c110c01f0a2bfa4cefabf32ffe008bd HTTP/1.1" 200 -
```

So STDERR is missing for every command, until it exits. Absurd.

### exits

The podman-run|ipfs commands seem to exit(125|0) while they're still outputting stuff. [who knows why?](https://stackoverflow.com/questions/881388/double-fork-when-creating-a-daemon/5386753#5386753) This means they can't %restart, because they always seem to need restarting.

These commands are left running when zap exits, reparented to `/lib/systemd/systemd --user`. Via fixups they won't get in the way of a new zap instance.

Needs knowledge. Ideally we handle Ctrl+C for zap exit and end jobs smoothly. Even knowing the process tree to track cpu|mem would be nice.

### other

You cannot restart commands via the UI, the jobs must be programmed to **%restart** or have a fixup for a particular behaviour to restart after.

See **TODO / clear exit code on restart**, the UI may have stale exit codes.

For more caveats, see `zap.py`

# TODO

## rewrite in golang
lots of nice Console-UI things are over there

## clear exit code on restart
The fixups can't be gauged for failure, eg `podman rm -f cos1` often errs "container has already been removed", meaning good.

## restart failed jobs|systems
Besides making the job one that **%restart**s, operator should be able to restart jobs at will, without restarting `zap.py`.

restart 2x daily: memleak mode.

## dependencies
we could need A finished before B starts. perhaps the cmd_source sets or gets markers.

do **%early** before others? could have a fixup notice when it says Ready, etc.

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

# support

`Third World Software Co` is here to help! Let me know.
