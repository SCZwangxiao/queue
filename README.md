This is a queuing script that can automatically monitor GPU info
and run your program when condition satisfied.

## Features
automatically monitor gpu utilization rate and free memory withn a fixed duration

run your command when gpu satisfy your condition:
- gpu utilization rate <= threshold
- gpu free memory >= threshold
- condition-satisfied gpu number >= threshold

send e-mail to inform you:
- when running your command
- when error occured (comming soon)
- when your command finfished (comming soon)

## Installation
packages
- pynvml, numpy

e-mail
- change the send_mail() function

## Quick start
