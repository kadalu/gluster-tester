FROM docker.io/fedora:29

RUN mkdir -p /root/rpms /root/tests

# Copy RPMs
COPY glusterfs/extras/LinuxRPM /root/rpms/

# Copy the tests batches
COPY gluster-tester /root/tests/

# RUN yum update -y && \
#     yum -y install epel-release

# Install Test dependencies
# TODO: Include sysvinit-tools, netstat in case of centos
RUN yum install -y perl-Test-Harness which attr dbench git \
        nfs-utils xfsprogs yajl openssh-clients openssh-server \
        openssh python2-psutil userspace-rcu

# For Geo-rep, Prepare password less ssh
RUN mkdir -p /root/.ssh
RUN rm -rf .ssh/id_rsa*
RUN ssh-keygen -N "" -f /root/.ssh/id_rsa
RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

# Install Gluster RPMs
RUN rm -f /root/rpms/*.src.rpm
RUN yum install -y /root/rpms/*.rpm

# Cleanup the RPMS
RUN rm -rf /root/rpms

COPY gluster-tester/scripts/regression.sh /usr/share/glusterfs/
COPY gluster-tester/scripts/run-tests.sh /usr/share/glusterfs/
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
