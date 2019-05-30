# Gluster Tester

Collection of utilities to run Gluster tests in parallel.

## Setup

Clone the repo and install using,

```
git clone https://github.com/aravindavk/gluster-tester.git
cd gluster-tester
sudo python setup.py install
```

Cleanup the backend directory and log directories and run the tests
using the following command,

```
rm -rf /var/log/gluster-tester
rm -rf /d
mkdir -p /var/log/gluster-tester/ld-{1,2,3} /d/bd-{1,2,3}

gluster-tester run \
    --num-parallel=3 \
    --backenddir=/d \
    --logdir=/var/log/gluster-tester \
    --refspec="refs/changes/60/22760/1"
```

## Logs

- **$logdir/build-container.log** Logs related to git clone, RPM build,
and container preparation steps
- **$logdir/regression-{1..N}.log** Regression tests output
- **$logdir/ld-{1..N}/\* ** Gluster Logs from each container
