import os
import sys
import subprocess
import tarfile
import time
import errno
from argparse import ArgumentParser


def run_tests(args):
    jobs = []
    for num in range(args.num_parallel):
        test_env = os.environ.copy()
        test_env["BATCHNUM"] = str(num+1)

        cmd = ("docker exec glusterfs-tester-%d bash "
               "/usr/share/glusterfs/regression.sh "
               "-t 300 "
               "-i /root/tests/tests-%d.dat " % (num+1, num+1)
        )

        if args.ignore_failure:
            cmd += " -c"  # exit_on_failure=no in run-tests.sh

        cmd += " &>/var/log/gluster-tester/regression-%d.log" % (num+1)

        jobs.append(subprocess.Popen(
            cmd,
            shell=True,
            env=test_env,
            stdout=subprocess.PIPE
        ))

    # Terminate all Jobs if one job fails
    ret = 0
    terminate = False
    while not terminate:
        num_jobs_complete = 0
        for idx, job in enumerate(jobs):
            job_ret = job.poll()
            if job_ret is not None:
                num_jobs_complete += 1
                if job_ret != 0 and not args.ignore_failure:
                    print("Job %d failed. Stopping all "
                          "other running jobs" % (idx+1))
                    ret = job_ret
                    terminate = True
                    break

        # If all jobs complete(success or fail)
        if num_jobs_complete == len(jobs):
            break

        time.sleep(1)

    # Now cleanup the jobs
    for job in jobs:
        if job.poll() is None:
            try:
                job.terminate()
            except OSError as err:
                if err.errno != errno.ESRCH:
                    raise

        job.communicate()

    if ret != 0:
        with tarfile.open(
                "/var/log/gluster-tester/glusterfs-logs.tgz", "w:gz") as tar:
            tar.add(args.logdir, arcname=os.path.basename(args.logdir))

    sys.exit(ret)


def main():
    parser = ArgumentParser()
    parser.add_argument("--num-parallel",
                        help="Number of parallel executions", type=int)
    parser.add_argument("--logdir", help="Log directory")
    parser.add_argument("--ignore-failure", action="store_true")
    args = parser.parse_args()

    run_tests(args)


if __name__ == "__main__":
    main()
