import os
import subprocess
from argparse import ArgumentParser
import sys
import logging
import time

from .run_tests import run_tests


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def run_else_exit(cmd, env=None, ignore_failure=False):
    logger.info("Started " + cmd)
    proc = subprocess.Popen(cmd, shell=True, env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    for line in iter(proc.stdout.readline, b''):
        try:
            print(line.rstrip().decode())
        except UnicodeDecodeError:
            print(line.rstrip())

    proc.communicate()
    if proc.returncode == 0:
        logger.info("Completed " + cmd)
    else:
        if not ignore_failure:
            logger.error("Failed " + cmd)
            sys.exit(1)

        logger.warning("Failed " + cmd + ". ignoring..")


def run_else_ignore(cmd, env=None):
    run_else_exit(cmd, env=env, ignore_failure=True)


def get_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcmd")

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument("--testenv", default="container",
                            help="Test environment",
                            choices=["container", "vm"])
    parser_run.add_argument("--num-parallel", default=3, type=int,
                            help="Number of parallel testers")
    parser_run.add_argument("--sourcedir", help="Directory to clone Glusterfs",
                            default="/usr/local/src/glusterfs")
    parser_run.add_argument("--backenddir",
                            help="Root backend directory for all testers",
                            default="/d")
    parser_run.add_argument("--logdir",
                            help="Root Log directory for all testers",
                            default="/var/log/gluster-tester")
    parser_run.add_argument("--refspec", help="Patch Refspec(Ex: refs/changes/60/22760/1)",
                            default="")
    parser_run.add_argument("--ignore-failure", action="store_true")

    parser_run.add_argument("--ignore-from",
                            help="List of ignored tests in a file")
    parser_run.add_argument("--include-bad-tests", action="store_true",
                            help="Do not skip bad tests")
    parser_run.add_argument("--include-known-bugs", action="store_true",
                            help="Do not skip known issue bugs")
    parser_run.add_argument("--include-nfs-tests", action="store_true",
                            help="Do not skip NFS tests")
    parser_run.add_argument("-t", "--run-timeout", type=int, default=300,
                            help="Each test timeout")
    parser_run.add_argument("--retry", action="store_true",
                            help="Retry on a test failure")
    parser_run.add_argument("--skip-preserve-logs", action="store_true",
                            help="Skip preserving Logs")
    parser_run.add_argument("--preserve-success-logs", action="store_true",
                            help="Preserve logs of successful tests")

    parser_baseimg = subparsers.add_parser('baseimg')
    parser_baseimg.add_argument("--logdir",
                                help="Root Log directory for all testers",
                                default="/var/log/gluster-tester")
    return parser.parse_args()


def subcmd_baseimg(args):
    scriptsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    run_else_exit("bash %s/build-container.sh glusterfs-tester-base "
                  "base.Dockerfile" % scriptsdir)


def subcmd_run(args):
    starttime = int(time.time())
    scriptsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    test_env = os.environ.copy()
    test_env["NPARALLEL"] = str(args.num_parallel)
    test_env["REFSPEC"] = args.refspec

    run_else_exit("bash %s/build-container.sh glusterfs-tester "
                  "Dockerfile" % scriptsdir,
                  env=test_env)

    # TODO: Get exact number
    totaltests = 696

    for num in range(1, args.num_parallel+1):
        run_else_exit("mkdir -p %s" % os.path.join(args.backenddir, "bd-%d" % num))
        run_else_exit("mkdir -p %s" % os.path.join(args.logdir, "ld-%d" % num))

    for num in range(1, args.num_parallel+1):
        run_else_ignore("docker kill glusterfs-tester-%d" % num)
        run_else_ignore("docker rm glusterfs-tester-%d" % num)

    for num in range(1, args.num_parallel+1):
        logdir = os.path.join(args.logdir, "ld-%d" % num)
        bddir = os.path.join(args.backenddir, "bd-%d" % num)
        imgname = "gluster/glusterfs-tester:latest"
        name = "glusterfs-tester-%d" % num
        hostname = "gnode%d" % num
        run_else_exit(
            "docker run -d"
            " --cap-add sys_admin"
            " --privileged=true"
            " --hostname " + hostname +
            " --device /dev/fuse"
            " --sysctl net.ipv6.conf.all.disable_ipv6=1"
            " --sysctl net.ipv6.conf.default.disable_ipv6=1"
            " --name " + name +
            " --mount type=bind,source=" + logdir + ",target=/var/log"
            " --mount type=bind,source=" + bddir + ",target=/d"
            " " + imgname
        )

        # Create loop files
        run_else_exit(
            "docker exec " + name +
            " bash -c 'for i in {0..20}; do mknod /dev/loop$i b 7 $i; done'"
        )

        if args.ignore_from:
            run_else_exit(
                "docker cp %s %s:/root/ignore_tests.dat" % (args.ignore_from, name)
            )

    logger.info("Started running tests")
    run_tests(args, starttime, totaltests)
    logger.info("Completed running tests")
    logger.info("Result is %s" % ret)
    sys.exit(ret)


def main():
    try:
        args = get_args()

        if args.subcmd == "run":
            subcmd_run(args)
            return

        if args.subcmd == "baseimg":
            subcmd_baseimg(args)
            return
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
