#!/bin/bash

build_vars() {
    : ${build_image_base:=radiasoft/python3}
    build_is_public=1
    build_passenv='PYKERN_BRANCH SLICOPS_BRANCH'
    : ${PYKERN_BRANCH:=} ${SLICOPS_BRANCH:=}
}

build_as_root() {
    # re2c is for synapps; rpcgen and libtirpc-devel is for asyn
    install_yum_install \
        libtirpc-devel \
        nodejs \
        perl-ExtUtils-Command \
        perl-FindBin \
        re2c \
        rpcgen
}

build_as_run_user() {
    cat > ~/.post_bivio_bashrc <<'EOF'
export EPICS_BASE=$HOME/.local/epics
# $EPICS_BASE/startup/EpicsHostArch outputs linux-x86_64; no need to be dynamic here
export EPICS_HOST_ARCH=linux-x86_64
bivio_path_insert "$EPICS_BASE/bin/$EPICS_HOST_ARCH"
EOF
    install_source_bashrc
    source epics-install.sh
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
