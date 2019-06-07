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
        firewalld libcurl-devel python3-devel cifs-utils e2fsprogs hostname \
        iproute libldb libss libwbclient lmdb-libs net-tools psmisc \
        python3-requests python3-urllib3 resource-agents rsync samba-client-libs \
        samba-common samba-common-libs bc libtalloc libtdb libtevent linux-atm-libs \
        python3-chardet python3-idna python3-prettytable python3-pysocks \
        python3-pyxattr iproute-tc iputils \
        ;fi

# For Geo-rep, Prepare password less ssh
RUN mkdir -p /root/.ssh
RUN rm -rf .ssh/id_rsa*
RUN ssh-keygen -N "" -f /root/.ssh/id_rsa
RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

ARG version="(unknown)"
# Container build time (date -u '+%Y-%m-%dT%H:%M:%S.%NZ')
ARG builddate="(unknown)"

LABEL build-date="${builddate}"
LABEL io.k8s.description="Glusterfs Tests"
LABEL name="glusterfs-tester-base"
LABEL Summary="GlusterFS Tester"
LABEL vcs-type="git"
LABEL vcs-url="https://github.com/gluster/glusterfs"
LABEL vendor="gluster"
LABEL version="${version}"

ENTRYPOINT ["tail", "-f", "/dev/null"]
