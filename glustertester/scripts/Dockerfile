FROM gluster/glusterfs-tester-base

# Redefining since arg defined before FROM is not accessible here
ARG baseos=fedora

RUN mkdir -p /root/tests

RUN date +%s

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

# To substitute proper values in test files(Example: tests/env.rc)
RUN cd /root/glusterfs && ./autogen.sh
RUN cd /root/glusterfs && ./configure --build=x86_64-redhat-linux-gnu \
        --host=x86_64-redhat-linux-gnu --program-prefix= \
        --disable-dependency-tracking --prefix=/usr --exec-prefix=/usr \
        --bindir=/usr/bin --sbindir=/usr/sbin --sysconfdir=/etc \
        --datadir=/usr/share --includedir=/usr/include --libdir=/usr/lib64 \
        --libexecdir=/usr/libexec --localstatedir=/var \
        --sharedstatedir=/var/lib --mandir=/usr/share/man \
        --infodir=/usr/share/info --enable-firewalld --enable-gnfs \
        --with-tmpfilesdir=/usr/lib/tmpfiles.d --disable-syslog

# Generate RPMs
RUN cd /root/glusterfs/extras/LinuxRPM && ./make_glusterrpms

# Install Gluster RPMs
RUN rm -f /root/glusterfs/extras/LinuxRPM/*.src.rpm
RUN dnf install -y /root/glusterfs/extras/LinuxRPM/*.rpm

COPY split_tests.py testutils.py runner.py /root/

# Split the tests
ARG nparallel=3
RUN python3 /root/split_tests.py \
        --testsdir=/root/glusterfs/tests \
        --output-prefix="/root/glusterfs/tests/" \
        --outdir=/root/tests \
        -n ${nparallel}

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

# NFS user and group setup
RUN groupadd nfsnobody
RUN useradd nfsnobody -g nfsnobody

RUN sed -i "s/LANG/\#LANG/g" /etc/locale.conf && \
    sed -i 's/Requires\=rpcbind\.service//g' /usr/lib/systemd/system/glusterd.service && \
    sed -i 's/rpcbind\.service/gluster-setup\.service/g' /usr/lib/systemd/system/glusterd.service && \
    sed -i.save -e "s#udev_sync = 1#udev_sync = 0#" -e "s#udev_rules = 1#udev_rules = 0#" -e "s#use_lvmetad = 1#use_lvmetad = 0#" -e "s#obtain_device_list_from_udev = 1#obtain_device_list_from_udev = 0#" /etc/lvm/lvm.conf && \
    systemctl mask getty.target && \
    systemctl disable systemd-udev-trigger.service && \
    systemctl disable systemd-udevd.service && \
    systemctl disable nfs-server.service && \
    systemctl enable rpcbind.service && \
    systemctl enable sshd.service && \
    mkdir -p /var/log/core;

# EXPOSE 2222 111 245 443 24006 24007 2049 8080 6010 6011 6012 38465 38466 38468 38469 49152 49153 49154 49156 49157 49158 49159 49160 49161 49162

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

CMD ["/usr/sbin/init"]
