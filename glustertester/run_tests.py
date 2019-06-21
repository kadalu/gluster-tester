import os
import sys
import subprocess
import tarfile
import time
import errno


def run_tests(args):
    jobs = []
    for num in range(args.num_parallel):
        test_env = os.environ.copy()
        test_env["BATCHNUM"] = str(num+1)

        cmd = ("docker exec glusterfs-tester-%d python3 "
               "/root/runner.py "
               "--tests-from=/root/tests/tests-%d.dat " % (num+1, num+1))

        if args.ignore_failure:
            cmd += " --ignore-failure"  # exit_on_failure=no in run-tests.sh

        if args.ignore_from:
            cmd += " --ignore-from=/root/ignore_tests.dat"

        if args.include_bad_tests:
            cmd += " --include-bad-tests"

        if args.include_known_bugs:
            cmd += " --include-known-bugs"

        if args.include_nfs_tests:
            cmd += " --include-nfs-tests"

        if args.run_timeout > 0:
            cmd += " --run-timeout=%s" % args.run_timeout

        if args.retry:
            cmd += " --retry"

        if args.skip_preserve_logs:
            cmd += " --skip-preserve-logs"

        if args.preserve_success_logs:
            cmd += " --preserve-success-logs"

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
                if job_ret != 0:
                    ret = 1

                if job_ret != 0 and not args.ignore_failure:
                    print("Job %d failed. Stopping all "
                          "other running jobs" % (idx+1))
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

    return ret
