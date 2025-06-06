#!/bin/bash

build_vars() {
    : ${build_image_base:=radiasoft/python3}
    # TODO(robnagler) push to this namespace, since we have write privs
    build_image_name=radiasoft/slicops
    build_is_public=1
    build_passenv='PYKERN_BRANCH SLICOPS_BRANCH'
    _slicops_demo=$build_run_user_home/bin/slicops-demo
    _slicops_entry=$build_run_user_home/bin/slicops-entry
    build_docker_cmd='["'"$_slicops_entry"'"]'
    : ${PYKERN_BRANCH:=} ${SLICOPS_BRANCH:=}
}

build_as_root() {
    # re2c is for synapps; rpcgen and libtirpc-devel is for asyn
    install_yum_install \
        libXt-devel \
        libtirpc-devel \
        motif-devel \
        nodejs \
        perl-ExtUtils-Command \
        perl-FindBin \
        re2c \
        rpcgen
}

build_as_run_user() {
    set -x
    _slicops_bashrc
    # sets epics_synapps_dir
    source epics-install.sh
    _slicops_pkg_install
    _slicops_bin
}


_slicops_bashrc() {
    cat > ~/.post_bivio_bashrc <<'EOF'
export EPICS_BASE=$HOME/.local/epics
# $EPICS_BASE/startup/EpicsHostArch outputs linux-x86_64; no need to be dynamic here
export EPICS_HOST_ARCH=linux-x86_64
bivio_path_insert "$EPICS_BASE/bin/$EPICS_HOST_ARCH"

# for newer nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EOF
    install_source_bashrc
}

_slicops_bin() {
    build_replace_vars "$build_guest_conf"/slicops-entry.sh "$_slicops_entry"
    # POSIT: epics-install.sh sets sim_det_dir
    build_replace_vars "$build_guest_conf"/slicops-demo.sh "$_slicops_demo"
    # Sanity check that the file contains somethng
    if ! grep sim-detector "$_slicops_demo" &> /dev/null; then
        cat "$_slicops_demo"
        install_err "$_slicops_demo was not generated properly"
    fi
    chmod a+rx "$_slicops_demo" "$_slicops_entry"
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

_slicops_pkg_install() {
    declare p=$PWD
    cd ~/src
    _slicops_pip_install radiasoft/pykern "$PYKERN_BRANCH"
    _slicops_pip_install slaclab/slicops "$SLICOPS_BRANCH"
    cd slaclab/slicops/ui
    rm ~/.npmrc
    # upgrade nvm and node
    curl -s -S -L https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
    source $HOME/.nvm/nvm.sh
    nvm install node
    npm install
    npm run build
    mv dist ../slicops/package_data/vue
    cd "$p"
}

build_vars
