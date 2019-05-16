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
        nfs-utils xfsprogs yajl \
        python2-psutil userspace-rcu

# Install Gluster RPMs
RUN rm -f /root/rpms/*.src.rpm
RUN yum install -y /root/rpms/*.rpm

# Cleanup the RPMS
RUN rm -rf /root/rpms

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
