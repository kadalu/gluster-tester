import os
import subprocess
from argparse import ArgumentParser
import sys
import logging

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
    out, _ = proc.communicate()
    if proc.returncode == 0:
        logger.info("Completed " + cmd)
        if out.strip() != "":
            logger.info("Output:\n" + out)
    else:
        if not ignore_failure:
            logger.error("Failed " + cmd)
            if out.strip() != "":
                logger.info("Output:\n" + out)
            sys.exit(1)

        logger.warn("Failed " + cmd + ". ignoring..")
        if out.strip() != "":
            logger.info("Output:\n" + out)


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

    return parser.parse_args()


def subcmd_run(args):
    scriptsdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    test_env = os.environ.copy()
    test_env["NPARALLEL"] = str(args.num_parallel)
    test_env["REFSPEC"] = args.refspec

    run_else_exit("bash %s/build-container.sh "
                  "&>%s/build-container.log" % (scriptsdir, args.logdir),
                  env=test_env
    )

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
        run_else_exit(
            "docker run -d"
            " --privileged=true"
            " --device /dev/fuse"
            " --name " + name +
            " --mount type=bind,source=" + logdir + ",target=/var/log"
            " --mount type=bind,source=" + bddir + ",target=/d"
            " " + imgname
        )

    run_cmd = "python %s/run-tests.py --num-parallel %d --logdir %s" % (
        scriptsdir, args.num_parallel, args.logdir
    )
    if args.ignore_failure:
        run_cmd += " --ignore-failure"

    run_else_exit(run_cmd)


def main():
    try:
        args = get_args()

        if args.subcmd == "run":
            subcmd_run(args)
            return
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
