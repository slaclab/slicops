#!/bin/bash

build_vars() {
    : ${build_image_base:=radiasoft/python3}
    build_is_public=1
    build_passenv='PYKERN_BRANCH SLICOPS_BRANCH'
    : ${PYKERN_BRANCH:=} ${SLICOPS_BRANCH:=}
}

build_as_root() {
    build_yum install \
        libXt-devel \
        libtirpc-devel \
        motif-devel \
        nodejs \
        perl-ExtUtils-Command \
        perl-FindBin \
        rpcgen
}

build_as_run_user() {
    install_source_bashrc
    cat > ~/.post_bivio_bashrc <<'EOF'
export EPICS_BASE=$HOME/.local/epics
# $EPICS_BASE/startup/EpicsHostArch outputs linux-x86_64; no need to be dynamic here
export EPICS_HOST_ARCH=linux-x86_64
bivio_path_insert "$EPICS_BASE/bin/$EPICS_HOST_ARCH"
export EPICS_PCAS_ROOT=$EPICS_BASE
f=$EPICS_BASE/extensions/synApps/support/areaDetector-R3-12-1
export EPICS_DISPLAY_PATH=.:$f/ADSimDetector/simDetectorApp/op/adl:$f/ADCore/ADApp/op/adl:$f/ADUVC/uvcApp/op/adl:$EPICS_BASE/modules/asyn/asyn-R4-45/opi/medm
EOF
    install_not_strict_cmd source ~/.post_bivio_bashrc
    bash epics-install.sh
    cd ~/src/
    _slicops_pip_install radiasoft/pykern "$PYKERN_BRANCH"
    _slicops_pip_install slaclab/slicops "$SLICOPS_BRANCH"
    cd slaclab/slicops/ui
    npm install
    npx ng build --output-path ../slicops/package_data/ng-build
}

_slicops_pip_install() {
    declare org_and_repo=$1
    declare branch=$2
    mkdir -p "$org_and_repo"
    git clone -q -c advice.detachedHead=false ${branch:+--branch "$branch"} https://github.com/"$org_and_repo" "$org_and_repo"
    cd "$org_and_repo"
    pip install -e .
    cd - &> /dev/null
}

build_vars
