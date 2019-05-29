ARG baseversion=29
ARG baseos=fedora
FROM ${baseos}:${baseversion}

# Redefining since arg defined before FROM is not accessible here
ARG baseos=fedora

RUN mkdir -p /root/tests

# TODO: Handle CentOS dependencies
# TODO: Include sysvinit-tools, netstat in case of centos
RUN if [ "x$baseos" = "xfedora" ]; then \
        yum install -y \
        git autoconf automake bison dos2unix flex fuse-devel glib2-devel \
        libaio-devel libattr-devel libibverbs-devel librdmacm-devel \
        libtool libxml2-devel lvm2-devel make openssl-devel pkgconfig \
        pyliblzma python-devel python-eventlet python-netifaces python-paste-deploy \
        python-simplejson python-sphinx python-webob pyxattr readline-devel \
        rpm-build systemtap-sdt-devel tar libcmocka-devel rpcgen libacl-devel \
        sqlite-devel libtirpc-devel userspace-rcu-devel libselinux-python \
        perl-Test-Harness which attr dbench git nfs-utils xfsprogs \
        yajl openssh-clients openssh-server openssh python2-psutil userspace-rcu \
        firewalld libcurl-devel python3-devel \
        ;fi

# For Geo-rep, Prepare password less ssh
RUN mkdir -p /root/.ssh
RUN rm -rf .ssh/id_rsa*
RUN ssh-keygen -N "" -f /root/.ssh/id_rsa
RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

ARG refspec=""
RUN cd /root/ && git clone --depth 1 https://review.gluster.org/glusterfs
RUN if [ "x$refspec" != "x" ]; then \
        cd /root/glusterfs && \
        git fetch git://review.gluster.org/glusterfs $refspec && \
        git checkout -b test-${refspec//\//_} FETCH_HEAD; \
        else \
        cd /root/glusterfs && \
        git checkout -b test-master master \
        ;fi

RUN cd /root/glusterfs/extras/LinuxRPM && ./make_glusterrpms

# Install Gluster RPMs
RUN rm -f /root/glusterfs/extras/LinuxRPM/*.src.rpm
RUN yum install -y /root/glusterfs/extras/LinuxRPM/*.rpm

COPY split-tests.py /root/

# Split the tests
ARG nparallel=3
RUN python /root/split-tests.py \
        --testsdir=/root/glusterfs/tests \
        --output-prefix="/usr/share/glusterfs/tests/" \
        --outdir=/root/tests \
        -n ${nparallel}

COPY regression.sh /usr/share/glusterfs/
COPY run-tests.sh /usr/share/glusterfs/
RUN chmod +x /usr/share/glusterfs/regression.sh
RUN chmod +x /usr/share/glusterfs/run-tests.sh

ARG version="(unknown)"
# Container build time (date -u '+%Y-%m-%dT%H:%M:%S.%NZ')
ARG builddate="(unknown)"

LABEL build-date="${builddate}"
LABEL io.k8s.description="Glusterfs Tests"
LABEL name="glusterfs-tester"
LABEL Summary="GlusterFS Tester"
LABEL vcs-type="git"
LABEL vcs-url="https://github.com/gluster/glusterfs"
LABEL vendor="gluster"
LABEL version="${version}"

ENTRYPOINT ["tail", "-f", "/dev/null"]
