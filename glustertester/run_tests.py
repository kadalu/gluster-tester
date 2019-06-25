import os
import sys
import subprocess
import tarfile
import time
import errno
import logging

logger = logging.getLogger()
last_printed = None


def print_summary(logdir, njobs, starttime, totaltests):
    global last_printed
    # Print summary once in 2 minutes
    if last_printed is None or (int(time.time()) - last_printed) >= 70:
        last_printed = int(time.time())

        totalpass = 0
        totalfail = 0
        total = 0
        jobs_msg = "Jobs: "
        for job in range(1, njobs+1):
            tpass = 0
            tfail = 0
            logfile = os.path.join(logdir, "regression-%s.log" % job)

            # Log file not yet created
            if not os.path.exists(logfile):
                continue

            with open(logfile) as logf:
                for line in logf:
                    if "Result: PASS" in line:
                        tpass += 1
                    if "Result: FAIL" in line:
                        tfail += 1

            totalfail += tfail
            totalpass += tpass
            jobs_msg += "[Job-%d  passed=%d  failed=%d]  " % (job,
                                                              tpass,
                                                              tfail)
        total = totalpass + totalfail
        duration = int(time.time()) - starttime
        speed = int(total / (duration/60))
        progress = int(total * 100 / totaltests)
        # estimated = remaining / speed
        if speed > 0:
            estimated_time = "%d minutes" % int((totaltests - total) / speed)
        else:
            estimated_time = "-"

        logger.info("Summary: %s tests complete  passed=%s  "
                    "failed=%s  speed=%s tpm  progress=%s%% "
                    "estimate=%s  duration=%d minutes" % (
                        total,
                        totalpass,
                        totalfail,
                        speed,
                        progress,
                        estimated_time,
                        (duration / 60)))
        logger.info(jobs_msg)


def run_tests(args, starttime, totaltests):
    jobs = []
    for num in range(args.num_parallel):
        test_env = os.environ.copy()
        test_env["BATCHNUM"] = str(num+1)

        cmd = ("docker exec -t glusterfs-tester-%d python3 "
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

        cmd += " &>%s" % (os.path.join(args.logdir,
                                       "regression-%d.log" % (num+1)))

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
        print_summary(args.logdir, args.num_parallel, starttime, totaltests)
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
        tarfilename = os.path.join(args.logdir, "glusterfs-logs.tgz")
        with tarfile.open(tarfilename, "w:gz") as tar:
            tar.add(args.logdir, arcname=os.path.basename(args.logdir))

    return ret
