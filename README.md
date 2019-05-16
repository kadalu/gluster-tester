# Gluster Tester

Collection of utilities to run Gluster tests in parallel.

**WARNING:** Not yet in usable state.


## Setup

Clone the repo and install using,

```
git clone 
cd gluster-tester
sudo python setup.py install
```

(Rpm support coming soon)

Run the tests using the following command(Multi VM support is coming soon),

```
gluster-tester run \
    --testenv=container \
    --num-parallel=3 \
    --sourcedir=/usr/local/src/glusterfs \
    --backenddir=/d \
    --logdir=/var/logs/gluster-tester
```


