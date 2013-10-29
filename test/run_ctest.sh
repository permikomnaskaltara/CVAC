# command arguments must be:
# $1: super-dir to bin/startIcebox.sh
# $2: dir where tests are located
# $3: ctest arguments, such as "-R File --verbose"
ROOT_DIR=$1
BUILD_DIR=$2
CTEST_ARGS=$3

# start up services
cd ${ROOT_DIR}
bin/startIcebox.sh
sleep 5

# run the tests, capture exit status
cd ${BUILD_DIR}
ctest ${CTEST_ARGS}
EXIT_STATUS=$?

# irrespective of exit status: shut down services
# then return exit status
cd ${ROOT_DIR}
bin/stopIcebox.sh
exit ${EXIT_STATUS}