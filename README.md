# Gluster Tester

Collection of utilities to run Gluster tests in parallel.

## Setup

Clone the repo and install using,

```
git clone https://github.com/aravindavk/gluster-tester.git
cd gluster-tester
sudo python setup.py install
```

Run the tests using the following command(Multi VM support is coming soon),

```
gluster-tester run \
    --testenv=container \
    --num-parallel=3 \
    --sourcedir=/usr/local/src/glusterfs \
    --backenddir=/d \
    --logdir=/var/logs/gluster-tester
    --patch=22760
    --patchset=1
```
