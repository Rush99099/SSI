#!/bin/bash

#Exercício 1
#usage: capsh [args ...]
#  --addamb=xxx   add xxx,... capabilities to ambient set
#  --cap-uid=<n>  use libcap cap_setuid() to change uid
#  --caps=xxx     set caps as per cap_from_text()
#  --chroot=path  chroot(2) to this path
#  --current      show current caps and IAB vectors
#  --decode=xxx   decode a hex string to a list of caps
#  --delamb=xxx   remove xxx,... capabilities from ambient
#  --drop=xxx     drop xxx,... caps from bounding set
#  --explain=xxx  explain what capability xxx permits
#  --forkfor=<n>  fork and make child sleep for <n> sec
#  --gid=<n>      set gid to <n> (hint: id <username>)
#  --groups=g,... set the supplemental groups
#  --has-a=xxx    exit 1 if capability xxx not ambient
#  --has-b=xxx    exit 1 if capability xxx not dropped
#  --has-ambient  exit 1 unless ambient vector supported
#  --has-i=xxx    exit 1 if capability xxx not inheritable
#  --has-p=xxx    exit 1 if capability xxx not permitted
#  --has-no-new-privs  exit 1 if privs not limited
#  --help, -h     this message (or try 'man capsh')
#  --iab=...      use cap_iab_from_text() to set iab
#  --inh=xxx      set xxx,.. inheritable set
#  --inmode=<xxx> exit 1 if current mode is not <xxx>
#  --is-uid=<n>   exit 1 if uid != <n>
#  --is-gid=<n>   exit 1 if gid != <n>
#  --keep=<n>     set keep-capability bit to <n>
#  --killit=<n>   send signal(n) to child
#  --license      display license info
#  --mode         display current libcap mode
#  --mode=<xxx>   set libcap mode to <xxx>
#  --modes        list libcap named modes
#  --no-new-privs set sticky process privilege limiter
#  --noamb        reset (drop) all ambient capabilities
#  --noenv        no fixup of env vars (for --user)
#  --print        display capability relevant state
#  --quiet        if first argument skip max cap check
#  --secbits=<n>  write a new value for securebits
#  --shell=/xx/yy use /xx/yy instead of /bin/bash for --
#  --strict       toggle --caps, --drop and --inh fixups
#  --suggest=text search cap descriptions for text
#  --supports=xxx exit 1 if capability xxx unsupported
#  --uid=<n>      set uid to <n> (hint: id <username>)
#  --user=<name>  set uid,gid and groups to that of user
#  ==             re-exec(capsh) with args as for --
#  =+             cap_launch capsh with args as for -+
#  --             remaining arguments are for /bin/bash
#  -+             cap_launch /bin/bash with remaining args
#                 (without -- [capsh] will simply exit(0))

#Exercício 2
#webserver.c
gcc webserver.c -o webeserver

#Exercício 3
./webserver 80
#Não tem permissão para dar bind
sudo setcap 'cap_net_bind_service=+ep' webserver
getcap webserver
./webserver 80
#Já faz bind corretamente