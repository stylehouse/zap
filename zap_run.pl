#!/usr/bin/perl
use strict;
use warnings;

my $command = $ARGV[0];

# Ignore SIGINT (Ctrl+C)
$SIG{INT} = 'IGNORE';
# Enable autoflush for stdout
$| = 1;

# Run the command, never to return
exec($command);