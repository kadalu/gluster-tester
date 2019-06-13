from __future__ import print_function
import sys
import time
import glob
from datetime import datetime

from argparse import ArgumentParser

from testutils import get_list_of_tests, KEY_BAD_TESTS, \
    get_testdefs, TEST_TAG_BAD_TEST, KEY_SKIPPED_TESTS, \
    TEST_TAG_KNOWN_ISSUE, SUMMARY, KEY_KNOWN_ISSUE_TESTS, \
    TEST_TAG_NFS_TEST, KEY_NFS_TESTS, KEY_RUN_TESTS, SEP, \
    test_execute, KILL_AFTER_TIME, KEY_FAILED_TESTS, \
    KEY_TESTS_ELAPSED_TIMES, KEY_CORE_GENERATED_TESTS, \
    print_summary, core_report


def runtest(testpath, args):
    old_cores = glob.glob("/*-*.core")

    testdefs = get_testdefs(testpath, "CENTOS6")
    test_tags = testdefs["tags"]
    if test_tags:
        print("Test Tags: %s" % repr(test_tags))

    if test_tags.get(TEST_TAG_BAD_TEST, None) is not None \
       and not args.include_bad_tests:
        SUMMARY[KEY_SKIPPED_TESTS] += 1
        SUMMARY[KEY_BAD_TESTS] += 1
        print("Skipping bad test file %s" % testpath)
        print("Reason: bug(s): %s" % ",".join(test_tags[TEST_TAG_BAD_TEST]))
        print(SEP)
        print()
        return 0

    if test_tags.get(TEST_TAG_KNOWN_ISSUE, None) is not None \
       and not args.include_known_bugs:
        SUMMARY[KEY_SKIPPED_TESTS] += 1
        SUMMARY[KEY_KNOWN_ISSUE_TESTS] += 1
        print("Skipping test file %s due to known issue" % testpath)
        print("Reason: bug(s): %s" % ",".join(test_tags[TEST_TAG_KNOWN_ISSUE]))
        print(SEP)
        print()
        return 0

    if test_tags.get(TEST_TAG_NFS_TEST, None) is not None \
       and not args.include_nfs_tests:
        SUMMARY[KEY_SKIPPED_TESTS] += 1
        SUMMARY[KEY_NFS_TESTS] += 1
        print("Skipping nfs test file %s" % testpath)
        print(SEP)
        print()
        return 0

    SUMMARY[KEY_RUN_TESTS] += 1
    print("[%s] Running tests in file %s" % (
        datetime.now().strftime('%H:%M:%S'),
        testpath
    ))
    starttime = time.time()
    timeout = args.run_timeout
    if testdefs["script_timeout"] > 0:
        timeout = testdefs["script_timeout"]

    testcmd = "timeout -k %s %s prove -vmfe '/bin/bash' %s" % (
        KILL_AFTER_TIME,
        timeout,
        testpath
    )

    ret = test_execute(testcmd, testpath, args, timeout=timeout)
    SUMMARY[KEY_TESTS_ELAPSED_TIMES][testpath] = time.time() - starttime

    if ret != 0:
        SUMMARY[KEY_FAILED_TESTS].append(testpath)

    new_cores = glob.glob("/*-*.core")
    core_diff = len(new_cores) - len(old_cores)
    if core_diff > 0:
        print("%s: %s new core files" % (testpath, core_diff))
        SUMMARY[KEY_CORE_GENERATED_TESTS].append(testpath)
        if ret == 0:
            # Test run is success but generated core, so mark as fail
            ret = 1

        # Core Report
        for core in new_cores:
            if core not in old_cores:
                core_report(core)

    print("[%s] End of test %s" % (
        datetime.now().strftime('%H:%M:%S'),
        testpath
    ))
    print(SEP)
    print()

    return ret


def run_tests(testslist, args):
    ignored_tests = []
    global_ret = 0
    if args.ignore_from:
        with open(args.ignore_from) as ignoredtestsf:
            for testpath in ignoredtestsf:
                ignored_tests.append(testpath.strip())

    # If tests are ignored using commandline then
    # append those as well to the list. For example,
    # --ignore=test1 --ignore=test2...
    if args.ignored_list:
        ignored_tests += args.ignored_list

    for testpath in testslist:
        testpath = testpath.strip()
        if testpath in ignored_tests:
            print("Ignored test %s" % testpath)
            continue

        ret = runtest(testpath, args)
        if ret != 0:
            global_ret = ret

        if ret != 0 and not args.ignore_failure:
            break

    print_summary(global_ret)
    return global_ret


def run_tests_from_input_file(input_file, args):
    with open(input_file) as testsf:
        return run_tests(testsf, args)


def run_all_tests(args):
    tests = []
    get_list_of_tests(args.testsdir, args.testsdir, tests, args.output_prefix)
    return run_tests(tests, args)


def run_specific_tests(args):
    return run_tests(args.tests_list, args)


def run_tests_from_stdin(args):
    return run_tests(sys.stdin, args)


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--tests-from",
                        help=("Run tests which are provided in input file. "
                              "Use \"-\" for stdin"))
    parser.add_argument("--test", dest="tests_list", action="append",
                        help="Give all test path to run(Multiples allowed)")

    parser.add_argument("--ignore", dest="ignored_list", action="append",
                        help="Ignore the test(Multiples allowed)")
    parser.add_argument("--ignore-from",
                        help="List of ignored tests in a file")
    parser.add_argument("--include-bad-tests", action="store_true",
                        help="Do not skip bad tests")
    parser.add_argument("--include-known-bugs", action="store_true",
                        help="Do not skip known issue bugs")
    parser.add_argument("--include-nfs-tests", action="store_true",
                        help="Do not skip NFS tests")
    parser.add_argument("-t", "--run-timeout", type=int, default=300,
                        help="Each test timeout")

    parser.add_argument("--ignore-failure", action="store_true",
                        help="Ignore a test failure and complete all tests")
    parser.add_argument("--retry", action="store_true",
                        help="Retry on a test failure")
    parser.add_argument("--skip-preserve-logs", action="store_true",
                        help="Skip preserving Logs")
    parser.add_argument("--preserve-success-logs", action="store_true",
                        help="Preserve logs of successful tests")
    return parser.parse_args()


def main():
    args = get_args()
    if args.tests_from == "-":
        return run_tests_from_stdin(args)

    if args.tests_from != "":
        return run_tests_from_input_file(args.tests_from, args)

    if args.tests_list:
        return run_specific_tests(args)

    return run_all_tests(args)


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
