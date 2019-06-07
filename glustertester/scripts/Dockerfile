FROM gluster/glusterfs-tester-base

# Redefining since arg defined before FROM is not accessible here
ARG baseos=fedora

RUN mkdir -p /root/tests

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
