#!/bin/bash
#
# This file is sourced from build.sh so setup is there.
#
# Install epics, asyn, and synaps
#
_asyn_version=R4-45
_epics_version=7.0.8.1
_synapps_version=R6-3

_epics_base() {
    declare d=$(dirname "$EPICS_BASE")
    mkdir -p "$d"
    cd "$d"
    b=base-"$_epics_version"
    _epics_untar https://epics-controls.org/download/base/"$b".tar.gz "$b" "$EPICS_BASE"
    cd "$EPICS_BASE"
    make -j4
}

_epics_main() {
    declare p=$PWD
    install_source_bashrc
    bivio_path_remove "$EPICS_BASE"/bin
    _epics_base
    cd "$EPICS_BASE"
    mkdir -p extensions
    cd extensions
    _epics_synapps
    # Need to return, because this file is sourced
    cd "$p"
}

_epics_synapps() {
    declare d=synApps
    # Must be absolute or fails silently
    declare f=$PWD/$d.modules
    cat <<'EOF' > "$f"
AREA_DETECTOR=R3-12-1
ASYN=R4-44-2
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
    make -j 4
    # POSIT used by slicops-demo.sh
    export sim_det_dir=$(find "$PWD" -type d -path '*iocBoot/iocSimDetector')
    cd - >& /dev/null
}

_epics_untar() {
    declare url=$1
    declare base=$2
    declare tgt=$3
    curl -L -s -S "$url" | tar xzf -
    mv "$base" "$tgt"
    cd "$tgt"
}

# No "$@" since this file is sourced from build.sh (this would pass args from program)
_epics_main
