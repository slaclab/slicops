#!/bin/bash
#
# Install epics and synaps
#
# make_cores=4 bash epics-install.sh
#
set -eou pipefail
shopt -s nullglob

: ${make_cores:=4}
_epics_version=7.0.8.1
_synapps_version=R6-3

_curl_untar() {
    declare url=$1
    declare base=$2
    declare tgt=$3
    curl -L -s -S "$url" | tar xzf -
    mv "$base" "$tgt"
    cd "$tgt"
}

_build_base() {
    sudo dnf -y install re2c rpcgen
    declare d=$(dirname "$EPICS_BASE")
    mkdir -p "$d"
    cd "$d"
    b=base-"$_epics_version"
    _curl_untar https://epics-controls.org/download/base/"$b".tar.gz "$b" "$EPICS_BASE"
    make -j "$make_cores"
}

_build_synapps() {
    declare d=synApps
    # Must be absolute or fails silently
    declare f=$PWD/$d.modules
    cat <<'EOF' > "$f"
AREA_DETECTOR=R3-12-1
ASYN=R4-42
AUTOSAVE=R5-11
BUSY=R1-7-4
CALC=R3-7-5
DEVIOCSTATS=3.1.16
SNCSEQ=R2-2-9
SSCAN=R2-11-6
EOF
    curl -s -S -L https://github.com/EPICS-synApps/assemble_synApps/releases/download/"$_synapps_version"/assemble_synApps \
        | perl - --base="$EPICS_BASE" --dir="$d" --config="$f"
    rm "$f"
    cd "$d"/support
    # otherwise gets a version conflict; This is the version that's installed already
    # synApps does not install ASYN.
    # perl -pi -e 's/asyn-.*/asyn-4-42/' busy-R1-7-4/configure/RELEASE
    make -j "$make_cores"
    cd - >& /dev/null
}

_err() {
    _msg "$@"
    return 1
}

_err_epics_base() {
    _err 'update your ~/.post_bivio_bashrc
export EPICS_BASE=$HOME/.local/epics
# $EPICS_BASE/startup/EpicsHostArch outputs linux-x86_64; no need to be dynamic here
export EPICS_HOST_ARCH=linux-x86_64
export EPICS_CA_ADDR_LIST=127.0.0.1
export EPICS_CA_AUTO_ADDR_LIST=NO
bivio_path_insert "$EPICS_BASE/bin/$EPICS_HOST_ARCH"

and then:
source ~/.post_bivio_bashrc
EpicsHostArch will not be found
'
}

_log() {
    _msg $(date +%H%M%S) "$@"
}

_main() {
    if [[ ! ${EPICS_BASE:-} ]]; then
        _err_epics_base
    fi
    if [[ -d $EPICS_BASE ]]; then
        _err "please remove:
rm -rf '$EPICS_BASE'
"
    fi
    _source_bashrc
    bivio_path_remove "$EPICS_BASE"/bin
    _build_base
    # Add epics to the path
    _source_bashrc
    cd "$EPICS_BASE"
    mkdir -p extensions
    cd extensions
    _build_synapps
}

_msg() {
    echo "$*" 1>&2
}


_source_bashrc() {
    set +eou pipefail
    shopt -u nullglob
    source $HOME/.bashrc
    set -eou pipefail
    shopt -s nullglob
}

_main "$@"
