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

Make sure `dm_thin_pool` kernel module is loaded using `lsmod | grep
dm_thin_pool`. Run `modprobe dm_thin_pool` if not loaded already.

Cleanup the backend directory and log directories and run the tests
using the following command,

```
gluster-tester cleanup --backenddir=/d --logdir=/var/log/gluster-tester
mkdir -p /var/log/gluster-tester /d

gluster-tester run \
    --num-parallel=5 \
    --backenddir=/d \
    --include-nfs-tests \
    --logdir=/var/log/gluster-tester \
    --refspec="refs/changes/60/22760/1" \
    | tee /var/log/gluster-tester/tests.log
```

Add `--ignore-failure` to not stop on single test failure.

To ignore tests, use `--ignore-from=<filename>`. Note: Test file path
should be relative to glusterfs source directory. For example,

(file: ignored_tests.dat)
```
tests/basic/changelog/changelog-snapshot.t
tests/basic/mount-nfs-auth.t
tests/basic/op_errnos.t
tests/basic/open-fd-snap-delete.t
```

## Logs

- **<logdir>/regression-{1..N}.log** Regression tests output
- **<logdir>/ld-{1..N}/\*** Gluster Logs from each container
