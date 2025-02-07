#!/bin/bash
#
# Install epics, asyn, and synaps
#
set -eou pipefail
shopt -s nullglob

_asyn_version=R4-45
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

_build_base_and_asyn() {
    sudo dnf -y install re2c
    declare d=$(dirname "$EPICS_BASE")
    mkdir -p "$d"
    cd "$d"
    b=base-"$_epics_version"
    _curl_untar https://epics-controls.org/download/base/"$b".tar.gz "$b" "$EPICS_BASE"
    cd "$EPICS_BASE"
    cd modules
    _curl_untar https://github.com/epics-modules/asyn/archive/refs/tags/"$_asyn_version".tar.gz "asyn-$_asyn_version" asyn
    perl -pi -e 's/^# (?=TIRPC)//' configure/CONFIG_SITE
    cd ..
    echo 'SUBMODULES += asyn' > Makefile.local
    cd ..
    # parallel make does not work
    make
}

_build_synapps() {
    declare d=synApps
    # Must be absolute or fails silently
    declare f=$PWD/$d.modules
    cat <<'EOF' > "$f"
AREA_DETECTOR=R3-12-1
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
    perl -pi -e 's/asyn-.*/asyn-4-42/' busy-R1-7-4/configure/RELEASE
    make -j 4
    cd - >& /dev/null
}

_main() {
    bivio_path_remove "$EPICS_BASE"/bin
    _build_base_and_asyn
    cd "$EPICS_BASE"
    mkdir -p extensions
    cd extensions
    _build_synapps
}

_main "$@"
