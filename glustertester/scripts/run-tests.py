import os
import sys
import subprocess
import tarfile
from argparse import ArgumentParser


def runner_wait(proc):
    while proc.poll() is None:
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())

    proc.communicate()
    return proc.returncode == 0


def run_tests(args):
    jobs = []
    scriptsdir = os.path.dirname(os.path.abspath(__file__))  # scriptsdir
    playbookdir = os.path.dirname(scriptsdir) + "/playbooks"
    for num in range(args.num_parallel):
        test_env = os.environ.copy()
        test_env["BATCHNUM"] = str(num+1)

        cmd = ("docker exec glusterfs-tester-%d bash /usr/share/glusterfs/regression.sh "
               "-i /root/tests/tests-%d.dat &>/var/log/gluster-tester/regression-%d.log" % (
                   num+1,
                   num+1,
                   num+1
               ))
        
        jobs.append(subprocess.Popen(
            cmd,
            shell=True,
            env=test_env,
            stdout=subprocess.PIPE
        ))

    # All Jobs started in parallel, now wait for each job
    ret = 0
    for job in jobs:
        if not runner_wait(job):
            ret = 1

    if ret != 0:
        with tarfile.open("/var/log/gluster-tester/glusterfs-logs.tgz", "w:gz") as tar:
            tar.add(args.logdir, arcname=os.path.basename(args.logdir))

    sys.exit(ret)


def main():
    parser = ArgumentParser()
    parser.add_argument("--num-parallel", help="Number of parallel executions", type=int)
    parser.add_argument("--sourcedir", help="Glusterfs Source directory")
    parser.add_argument("--logdir", help="Log directory")
    args = parser.parse_args()

    run_tests(args)


if __name__ == "__main__":
    main()
