ARG baseversion=33
ARG baseos=fedora
FROM ${baseos}:${baseversion}

# Redefining since arg defined before FROM is not accessible here
ARG baseos=fedora

RUN mkdir -p /root/tests

# TODO: Handle CentOS dependencies
# TODO: Include sysvinit-tools, netstat in case of centos
RUN if [ "x$baseos" = "xfedora" ]; then \
        dnf install -y \
        git autoconf automake bison flex fuse-devel \
        libaio-devel libattr-devel libtool libxml2-devel lvm2-devel make \
	openssl-devel pkgconfig python3-devel python3-eventlet python3-netifaces \
	python3-paste-deploy python3-simplejson python3-sphinx readline-devel \
        rpm-build systemtap-sdt-devel tar libcmocka-devel rpcgen libacl-devel \
        libtirpc-devel userspace-rcu-devel \
        perl-Test-Harness which attr dbench nfs-utils xfsprogs \
        yajl openssh-clients openssh-server openssh firewalld libcurl-devel \
	cifs-utils e2fsprogs hostname iproute libldb libss libwbclient net-tools psmisc \
        python3-requests python3-urllib3 resource-agents rsync \
        bc libtalloc libtdb libtevent linux-atm-libs \
        python3-chardet python3-idna python3-prettytable python3-pysocks \
        python3-pyxattr iproute-tc iputils gdb systemd-udev cronie sos \
        bind-utils \
        ;fi

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
