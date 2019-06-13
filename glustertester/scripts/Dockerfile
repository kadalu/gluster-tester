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

COPY split_tests.py testutils.py runner.py /root/

# Split the tests
ARG nparallel=3
RUN python3 /root/split_tests.py \
        --testsdir=/root/glusterfs/tests \
        --output-prefix="/usr/share/glusterfs/tests/" \
        --outdir=/root/tests \
        -n ${nparallel}

# COPY regression.sh /usr/share/glusterfs/
# COPY run-tests.sh /usr/share/glusterfs/
# RUN chmod +x /usr/share/glusterfs/regression.sh
# RUN chmod +x /usr/share/glusterfs/run-tests.sh

# SSH related things
# Based on https://docs.docker.com/engine/examples/running_ssh_service/
RUN mkdir /var/run/sshd
RUN echo 'root:gluster' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN ssh-keygen -t rsa -N "" -b 4096 -f /etc/ssh/ssh_host_rsa_key

# For Geo-rep, Prepare password less ssh
RUN mkdir -p /root/.ssh
RUN rm -rf .ssh/id_rsa*
RUN ssh-keygen -N "" -f /root/.ssh/id_rsa
RUN cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

EXPOSE 22

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

CMD ["/usr/sbin/sshd", "-D"]
