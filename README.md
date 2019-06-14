# Gluster Tester

Collection of utilities to run Gluster tests in parallel.

## Setup

- Install [docker-ce](https://docs.docker.com/install/linux/docker-ce/fedora/)
- Clone the repo and install using,
     
       git clone https://github.com/aravindavk/gluster-tester.git
       cd gluster-tester
       sudo python3 setup.py install

## Usage

Create the base image by running the following command.(This command
can be scheduled to run nightly)

```
gluster-tester baseimg | tee /var/log/gluster-tester/build-base-container.log
```

Cleanup the backend directory and log directories and run the tests
using the following command,

```
rm -rf /var/logs/gluster-tester
rm -rf /d
mkdir -p /var/logs/gluster-tester /d

gluster-tester run \
    --num-parallel=3 \
    --backenddir=/d \
    --logdir=/var/logs/gluster-tester \
    --refspec="refs/changes/60/22760/1" \
    | tee /var/log/gluster-tester/tests.log
```

## Logs

- **<logdir>/regression-{1..N}.log** Regression tests output
- **<logdir>/ld-{1..N}/\*** Gluster Logs from each container
