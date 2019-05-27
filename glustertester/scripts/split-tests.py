from __future__ import print_function

import os
import sys
import glob
from argparse import ArgumentParser


def get_list_of_tests(rootdir, testdir, tests, output_prefix=None):
    for testfile in os.listdir(testdir):
        if testfile == "00-geo-rep":
            continue

        full_path = os.path.join(testdir, testfile)
        if testfile.endswith(".t"):
            outpath = full_path.replace(rootdir + "/", "")
            if output_prefix is not None:
                outpath = os.path.join(output_prefix, outpath)

            tests.append(outpath)

        if os.path.isdir(full_path):
            get_list_of_tests(rootdir, full_path, tests, output_prefix)


def main():
    parser = ArgumentParser()
    parser.add_argument("-n", "--batches", help="Number of Batches", type=int, default=3)
    parser.add_argument("--testsdir", help="Tests Root directory", default="tests")
    parser.add_argument("--outdir", help="Output directory", default=".out")
    parser.add_argument("--output-prefix", help="Output Prefix")
    args = parser.parse_args()

    if not args.outdir:
        print("Invalid ouput directory", file=sys.stderr)
        sys.exit(1)

    for testbatch in glob.glob("%s/tests-*.dat" % args.outdir):
        os.remove(testbatch)

    tests = []
    get_list_of_tests(args.testsdir, args.testsdir, tests, args.output_prefix)

    # Split the list based on number of parallel executors required
    num_tests = len(tests)
    split_number = int((num_tests + args.batches - 1) / args.batches)
    last = 0
    tests_batch = []
    while last < num_tests:
        tests_batch.append(tests[int(last):int(last + split_number)])
        last += split_number

    for idx, testbatch in enumerate(tests_batch):
        with open(os.path.join(args.outdir, "tests-%d.dat" % (idx+1)), "w") as batchfile:
            batchfile.write("\n".join(testbatch))

    print("Tests split into %d batches" % args.batches)


if __name__ == "__main__":
    main()
