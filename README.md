# zap
supervisor running|monitoring all these commands

## description

runs the commands specified in zap.py. they a split into systems, so individual `./zap.py $system` can be run, or all will be.

I used it to make a dev environment for [letz](https://github.com/stylehouse/letz), instead of a village of terminals to constantly rebuild.

- can fixup common errors with the commands
- has curses interface which becomes `less -R` (supports colours) when looking at commands (not a fully-fledged terminal)

## installation

* copy somewhere
* adjust the commands specified in `zap.py`
  * various podman-build are implied

should be secure, only uses core python.

## long description

I want to automate running and monitoring all these commands.

It needs to present an interface (in the terminal?) showing things running normally.

## examples

Here in `zap.py` are several sequences of commands,
    the first is usually an ssh session the rest happen in
    then we wait observing the last command forever

Please look to the wiki for more examples, feel free to add yours.

## caveats

the podman-run commands seem to exit(0) while they're still outputting stuff. [who knows why?](https://stackoverflow.com/questions/881388/double-fork-when-creating-a-daemon/5386753#5386753)

see `zap.py`

## TODO

### restart failed jobs|systems
without restarting `zap.py`.
restart 2x daily: memleak mode.
### improve view_systems
make the system/job/cmd hierarchy clearer
more indicators, eg that unseen output|errors exist per job
### ssh in to watch progress
getting the pid of the remote shell, then with `ps faux`, figure which cmd in the job we are doing, take cpu|mem stats, etc.
### novelty analysis
if anything makes unusual noise (learn what things usually do) it should bring that information into view, ie showing the user novel events.
### command marketplace
how do everyone's technical struggles fruit
### fixup marketplace
the general-knowledge version of the above.
sequences of commands that diagnose & rectify situations.



