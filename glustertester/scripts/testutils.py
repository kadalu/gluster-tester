from __future__ import print_function
import os
import tarfile
import subprocess


TEST_TAG_BAD_TEST = "BAD_TEST"
TEST_TAG_NFS_TEST = "NFS_TEST"
TEST_TAG_KNOWN_ISSUE = "KNOWN_ISSUE"
SEP = "=" * 80
KILL_AFTER_TIME = 5

KEY_STARTTIME = "starttime"
KEY_ENDTIME = "endtime"
KEY_SKIPPED_TESTS = "skipped_tests"
KEY_BAD_TESTS = "bad_tests"
KEY_KNOWN_ISSUE_TESTS = "known_issue_tests"
KEY_NFS_TESTS = "nfs_tests"
KEY_RETRY_NEEDED_TESTS = "retry_needed_tests"
KEY_TOTAL_TESTS = "total_tests"
KEY_RUN_TESTS = "run_tests"
KEY_TESTS_ELAPSED_TIMES = "elapsed_times"
KEY_FAILED_TESTS = "failed_tests"
KEY_CORE_GENERATED_TESTS = "core_generated_tests"


SUMMARY = {
    KEY_STARTTIME: 0,
    KEY_ENDTIME: 0,
    KEY_SKIPPED_TESTS: 0,
    KEY_BAD_TESTS: 0,
    KEY_KNOWN_ISSUE_TESTS: 0,
    KEY_NFS_TESTS: 0,
    KEY_RETRY_NEEDED_TESTS: [],
    KEY_TOTAL_TESTS: 0,
    KEY_RUN_TESTS: 0,
    KEY_TESTS_ELAPSED_TIMES: {},
    KEY_FAILED_TESTS: [],
    KEY_CORE_GENERATED_TESTS: []
}


def get_list_of_tests(rootdir, testdir, tests, output_prefix=None):
    for testfile in os.listdir(testdir):
        full_path = os.path.join(testdir, testfile)

        if testfile.endswith(".t"):
            outpath = full_path.replace(rootdir + "/", "")
            if output_prefix is not None:
                outpath = os.path.join(output_prefix, outpath)

            tests.append(outpath)

        if os.path.isdir(full_path):
            get_list_of_tests(rootdir, full_path, tests, output_prefix)


def print_summary(ret):
    print()
    print("Run complete")
    print(SEP)
    print("Number of tests found:                                %4s" % (
        SUMMARY[KEY_TOTAL_TESTS]))
    print("Number of tests skipped as they were marked bad:      %4s" % (
        SUMMARY[KEY_BAD_TESTS]))
    print("Number of tests skipped because of known_issues:      %4s" % (
        SUMMARY[KEY_KNOWN_ISSUE_TESTS]))
    print("Number of tests skipped because of NFS tests ignored: %4s" % (
        SUMMARY[KEY_NFS_TESTS]))
    print("Number of tests that were run:                        %4s" % (
        SUMMARY[KEY_RUN_TESTS]))
    print()
    print("Tests ordered by time taken(in seconds), slowest to fastest: ")

    import operator
    sorted_elapsed_times = sorted(SUMMARY[KEY_TESTS_ELAPSED_TIMES].items(),
                                  key=operator.itemgetter(1))
    for key, value in sorted_elapsed_times:
        print("%4s  %s" % (value, key))

    if SUMMARY[KEY_RETRY_NEEDED_TESTS]:
        print("\n%s test(s) needed retry:\n %s" % (
            len(SUMMARY[KEY_RETRY_NEEDED_TESTS]),
            "\n".join(SUMMARY[KEY_RETRY_NEEDED_TESTS])
        ))
        print()

    print()
    print("Result is %s" % ret)
    print()


def which(file_name):
    for path in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(path, file_name)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path

    return None


def getliblistfromcore(corepath):
    cmd = ("gdb -c \"%s\" -q -ex \"set pagination off\" "
           "-ex \"info sharedlibrary\" -ex q 2>/dev/null")
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as err:
        print("Unable to get list of sharedlibrary from core \"%s\": %s" % (
            corepath,
            err
        ))
        return []

    record_started = False
    libs = []
    for line in out.split(b"\n"):
        if record_started:
            libs.append(line.split()[-1].strip().decode())

        if b"Shared Object Path" in line:
            record_started = True

    # Return only libs with prefix /usr
    return [l for l in libs if "/usr" in l]


# Function for use in generating filenames with increasing "-<n>" index
# In:
#       $1 basepath: Directory where file needs to be created
#       $2 filename: Name of the file sans extension
#       $3 extension: Extension string that would be appended to the generated
#               filename
# Out:
#       string of next available filename with appended "-<n>"
# Example:
#       Interested routines that want to create a file name, say foo-<n>.txt at
#       location /var/log/gluster would pass in "/var/log/gluster" "foo" "txt"
#       and be returned next available foo-<n> filename to create.
# Notes:
#       Function will not accept empty extension, and will return the same name
#       over and over (which can be fixed when there is a need for it)
def get_next_filename(basepath, filename, extension):
    num = 1
    tfilename = "%s-%s" % (filename, num)
    while os.path.exists(os.path.join(basepath, tfilename + "." + extension)):
        num += 1
        tfilename = "%s-%s" % (filename, num)

    return tfilename + "." + extension


def tar_logs(tardir, testpath):
    if not tardir:
        return

    tar_name_prefix = os.path.basename(testpath).strip(".t")
    tar_name = os.path.join(
        tardir,
        get_next_filename(tardir, tar_name_prefix, "tar")
    )

    to_delete = []
    with tarfile.open(tar_name, "w") as tar_handle:
        for root, _, files in os.walk(tardir):
            for filename in files:
                if not filename.endswith(".tar"):
                    tar_handle.add(os.path.join(root, filename))
                    to_delete.append(os.path.join(root, filename))

    for delfile in to_delete:
        os.remove(delfile)


def clean_logdir(logdir):
    if not logdir:
        return

    to_delete = []
    for root, _, files in os.walk(tardir):
        for filename in files:
            if not filename.endswith(".tar"):
                to_delete.append(os.path.join(root, filename))

    for delfile in to_delete:
        os.remove(delfile)


def core_report(corepath):
    cmd = ("gdb -ex \"core-file %s\" -ex 'set pagination off' "
           "-ex 'info proc exe' -ex q")
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as err:
        print("Unable to get executable name from core \"%s\": %s" % (
            corepath,
            err
        ))
        return

    last_line = ""
    for line in out.split(b"\n"):
        try:
            print(line.strip().decode())
        except UnicodeDecodeError:
            print(line.strip())

        last_line = line.decode()

    parts = last_line.split("'")
    executable_name = None
    executable_path = None
    if len(parts) == 3:
        executable_name = parts[1]
        executable_path = which(executable_name)

    print()
    print("=========================================================")
    print("              Start printing backtrace")
    print("         program name : %s" % executable_path)
    print("         corefile     : %s" % corepath)
    print("=========================================================")

    cmd = ("gdb -nx --batch --quiet -ex \"thread apply all bt full\" "
           "-ex \"quit\" --exec=%s --core=%s" % (executable_path, corepath))
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    try:
        print(out.decode())
    except UnicodeDecodeError:
        print(out)

    print("=========================================================")
    print("              Finish backtrace")
    print("         program name : %s" % executable_path)
    print("         corefile     : %s" % corepath)
    print("=========================================================")
    print("")


# Tests can have comment lines with some comma separated values within them.
# Key names used to determine test status are
# G_TESTDEF_TEST_STATUS_CENTOS6
# G_TESTDEF_TEST_STATUS_NETBSD7
# Some examples:
# G_TESTDEF_TEST_STATUS_CENTOS6=BAD_TEST,BUG=123456
# G_TESTDEF_TEST_STATUS_NETBSD7=KNOWN_ISSUE,BUG=4444444
# G_TESTDEF_TEST_STATUS_CENTOS6=BAD_TEST,BUG=123456;555555
# G_TESTDEF_TEST_STATUS_CENTOS6=NFS_TESTS,BUG=1385758
# You can change status of test to enabled or delete the line only if all the
# bugs are closed or modified or if the patch fixes it.
def get_testdefs(testpath, name):
    tags = {}
    script_timeout = 0
    with open(testpath) as testf:
        for line in testf:
            if line.startswith("SCRIPT_TIMEOUT"):
                parts = line.strip().split("=")
                script_timeout = int(parts[1].strip())
                continue

            if line.startswith("#G_TESTDEF_TEST_STATUS_"):
                parts = line.replace("#G_TESTDEF_TEST_STATUS_",
                                     "").strip().split("=", 1)
                if parts[0] != name:
                    continue

                tag_parts = parts[1].split(",")
                bugs = []

                for tag in tag_parts:
                    if tag.startswith("BUG="):
                        bugs.append(tag.replace("BUG=", ""))

                tags[tag_parts[0]] = bugs

    # Return tags for requested name
    return {
        "tags": tags,
        "script_timeout": script_timeout
    }


def test_execute(cmd, testpath, args,
                 max_retries=0, run_count=0, prev_ret=0, timeout=300):
    if run_count > 0:
        print("%s: bad status %s" % (testpath, prev_ret))
        print()
        print("       *********************************")
        print("       *       REGRESSION FAILED       *")
        print("       * Retrying failed tests in case *")
        print("       * we got some spurious failures *")
        print("       *********************************")
        print()
        SUMMARY[KEY_RETRY_NEEDED_TESTS].append(testpath)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    for line in iter(proc.stdout.readline, b''):
        if line.rstrip():
            try:
                print(line.rstrip().decode())
            except UnicodeDecodeError:
                print(line.rstrip())

    proc.communicate()
    run_count += 1
    ret = proc.returncode
    gluster_logdir = ""

    try:
        gluster_logdir = subprocess.check_output("gluster --print-logdir",
                                                 shell=True)
        gluster_logdir = gluster_logdir.strip().decode()
    except subprocess.CalledProcessError as err:
        print("Failed to get Gluster Log directory: %s" % err)

    # Preserve success logs if requested
    if ret == 0 and args.preserve_success_logs:
        tar_logs(gluster_logdir, testpath)

    if ret != 0:
        if not args.skip_preserve_logs:
            tar_logs(gluster_logdir, testpath)

        # timeout always return 124 if it is actually a timeout.
        if ret == 124:
            print("Result: FAIL")
            print("%s timed out after %s seconds" % (
                testpath,
                timeout
            ))

        if (run_count - 1) < max_retries:
            ret = test_execute(cmd, testpath, args,
                               max_retries, run_count,
                               proc.returncode, timeout)

    clean_logdir(gluster_logdir)

    return ret
