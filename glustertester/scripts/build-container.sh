#! /bin/bash

set -e -o pipefail

DOCKER_USER="${DOCKER_USER:-gluster}"
CONTAINER_VERSION="${CONTAINER_VERSION:-latest}"
NPARALLEL="${NPARALLEL:-3}"
REFSPEC="${REFSPEC}"
BASEOS="${BASEOS:-fedora}"
BASEVERSION="${BASEVERSION:-32}"

RUNTIME_CMD=${RUNTIME_CMD:-docker}
build="build"
if [[ "${RUNTIME_CMD}" == "buildah" ]]; then
	build="bud"
fi

VERSION=$(date -u '+0.0.0+%Y%m%d%H%M%S')
BUILDDATE="$(date -u '+%Y-%m-%dT%H:%M:%S.%NZ')"

build_args=()
build_args+=(--build-arg "version=$VERSION")
build_args+=(--build-arg "builddate=$BUILDDATE")
build_args+=(--build-arg "sourcedir=$SOURCEDIR")
build_args+=(--build-arg "nparallel=$NPARALLEL")
build_args+=(--build-arg "baseos=$BASEOS")
build_args+=(--build-arg "baseversion=$BASEVERSION")
build_args+=(--build-arg "refspec=$REFSPEC")

# Print Docker version
echo "=== $RUNTIME_CMD version ==="
$RUNTIME_CMD version

function build_container()
{
    IMAGE_NAME=$1
    DOCKERFILE=$2
    cd $(dirname `realpath $0`);
    $RUNTIME_CMD $build \
                 -t "${DOCKER_USER}/${IMAGE_NAME}:${CONTAINER_VERSION}" \
                 "${build_args[@]}" \
                 --network host \
                 -f "$DOCKERFILE" \
                 . ||
        exit 1
}

build_container $1 $2
