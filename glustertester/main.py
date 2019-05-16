import os
import subprocess
from argparse import ArgumentParser
import sys


def get_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcmd")

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument("--testenv", default="container",
                            help="Test environment",
                            choices=["container", "vm"])
    parser_run.add_argument("--num-parallel", default=3,
                            help="Number of parallel testers")
    parser_run.add_argument("--sourcedir", help="Directory to clone Glusterfs",
                            default="/usr/local/src/glusterfs")
    parser_run.add_argument("--backenddir",
                            help="Root backend directory for all testers",
                            default="/d")
    parser_run.add_argument("--logdir",
                            help="Root Log directory for all testers",
                            default="/var/log/gluster-tester")
    parser_run.add_argument("--patch", help="Patch Number",
                            default=0, type=int)
    parser_run.add_argument("--patchset", help="Patchset Number",
                            default=0, type=int)

    return parser.parse_args()


def subcmd_run(args):
    test_env = os.environ.copy()
    test_env["TESTERDIR"] = os.path.dirname(__file__)
    test_env["TESTENV"] = args.testenv
    test_env["SOURCEDIR"] = args.sourcedir
    test_env["BACKENDDIR"] = args.backenddir
    test_env["LOGDIR"] = args.logdir
    test_env["NUM_PARALLEL"] = str(args.num_parallel)
    test_env["PATCH"] = str(args.patch)
    test_env["PATCHSET"] = str(args.patchset)
    test_env["CONTAINER_NAME_PFX"] = "glusterfs-tester"
    test_env["CONTAINER_VERSION"] = "latest"
    test_env["CONTAINER_IMAGE"] = "gluster/glusterfs-tester"

    # TODO: Copy scripts to src directory

    print("ansible-playbook %s/playbooks/runner.yaml 2>&1" % (
        os.path.dirname(__file__)))
    proc = subprocess.Popen(
        "ansible-playbook %s/playbooks/runner.yaml 2>&1" % (
            os.path.dirname(__file__)),
        env=test_env,
        shell=True,
        stdout=subprocess.PIPE
    )

    while proc.poll() is None:
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())

    proc.communicate()
    sys.exit(proc.returncode)


def main():
    args = get_args()

    if args.subcmd == "run":
        return subcmd_run(args)


if __name__ == "__main__":
    main()
