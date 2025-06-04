#!/bin/bash
#
# usage: SLICOPS_BASE_PORT=5790 bash etc/run.sh (sim|api|ui)
#
set -eou pipefail
shopt -s nullglob

_root_dir=$(cd "$(dirname "$0")/.." && pwd)
_docker_image=docker://radiasoft/slicops
declare -A _port_map=(
    [api]=1
    [repeater]=2
    [server]=3
    [ui]=0
)
_python_version=3.12.10
_run_dir=$_root_dir/run
_image=slicops.sif
_sim_dir=/home/vagrant/.local/epics/extensions/synApps/support/areaDetector-R3-12-1/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector
_ui_dir=$_root_dir/ui

_assert_base_port() {
    declare p=${SLICOPS_BASE_PORT:-<not set>}
    if [[ ! $p =~ ^[0-9]+$ ]] || (( p <= 5000 )); then
        _err "SLICOPS_BASE_PORT=$p must be an integer above 5000"
    fi
}

_assert_conda_env() {
    if ! type -t conda &> /dev/null; then
        _err 'conda not installed; please install and rerun'
    fi
    _source_bashrc
    if ! conda activate slicops &> /dev/null; then
        _msg 'creating conda environment slicops'
        conda create -y -n slicops
        if ! conda activate slicops; then
            _err 'unable to activate slicops after creating'
        fi
    fi
    if type -t slicops &> /dev/null; then
        return
    fi
    _assert_conda_package python "$_python_version"
    _assert_conda_package nodejs
    cd "$_root_dir"
    _msg 'installing slicops'
    pip install -e .
}

_assert_conda_package() {
    declare name=$1
    declare version=${2:-}
    if ! conda list | grep -q "^$name "; then
        declare p=$name${version:+=$version}
        _msg "installing $p"
        conda install -y "$p"
    fi
}

_assert_image() {
    if [[ -r $_image ]]; then
        return
    fi
    _msg "Building $_image from $_docker_image. This will take about 45 minutes..."
    declare f=$_run_dir/image.log
    if ! TMPDIR=$PWD apptainer build "$_image" $_docker_image &> "$f"; then
        tail --lines=50 "$f"
        _err "build image=$_image failed. Full log: $f"
    fi
    rm -f "$f"
}

_assert_python_env() {
    if type -t slicops &> /dev/null; then
        return
    fi
    # RadiaSoft environment
    if type -t pyenv &> /dev/null; then
        _err 'need to pip install slicops in pyenv python environment'
    fi
    _assert_conda_env
}

_cd_run_dir() {
    if [[ ! -d $_run_dir ]]; then
        mkdir "$_run_dir"
    fi
    cd "$_run_dir"
}

_dispatch_op() {
    declare op=$1
    declare -a args=( "${@:2}" )
    declare f=_op_$op
    if [[ $(type -t "$f") != 'function' ]]; then
        _err "invalid op=$op
usage: bash ${BASH_SOURCE[0]} <op>
where <op> is one of:
$(compgen -A function _op_ | sed -e 's/^_op_//')"
    fi
    "$f" "${args[@]}"
}

_epics_env() {
    declare assert=${1:-}
    declare s=$(_port server $assert)
    declare r=$(_port repeater $assert)
    if ! [[ $s && $r ]]; then
        # Used in subshell and error already printed
        return 1
    fi
    echo "EPICS_CA_REPEATER_PORT=$r EPICS_CA_SERVER_PORT=$s EPICS_CA_AUTO_ADDR_LIST=NO EPICS_CA_ADDR_LIST=127.0.0.1:$s"
}

_err() {
    _msg "$@"
    exit 1
}

_log() {
    _msg $(date +%H%M%S) "$@"
}

_main() {
    declare op=${1:-<not set>}
    _assert_base_port
    _assert_python_env
    _dispatch_op "$op" "${@:2}"
}

_msg() {
    echo "$*" 1>&2
}

_op_api() {
    _cd_run_dir
    declare e=$(_epics_env)
    declare p=$(_port api assert)
    if ! [[ $e && $p ]]; then
        return 1
    fi
    # not in quotes, because eval
    eval $e exec slicops service ui-api --tcp-port=$p
}

_op_sim() {
    _cd_run_dir
    _assert_image
    declare e=$(_epics_env assert)
    if [[ ! $e ]]; then
        return 1
    fi
    exec apptainer run --containall "$_image" bash -c "$e slicops epics sim-detector --ioc-sim-detector-dir='$_sim_dir'"
}

_op_ui() {
    cd "$_ui_dir"
    declare v=$(_port ui assert)
    declare a=$(_port api)
    if ! [[ $a && $v ]]; then
        return 1
    fi
    SLICOPS_VITE_TARGET=http://127.0.0.1:$a exec npm run dev -- --port "$v" --host
}

_port() {
    declare name=${1:-}
    declare assert=${2:-}
    declare p=${_port_map[$name]}
    if [[ ! $p ]]; then
        _err "assertion error: _port missing port arg=${1:-<missing arg>}"
    fi
    p=$(( SLICOPS_BASE_PORT + p ))
    if [[ $assert ]] && ss --tcp --udp --listening --numeric | grep -q ":$p "; then
        _err "port=$p in use; is service=$name already running? Or, choose a different SLICOPS_BASE_PORT=$SLICOPS_BASE_PORT"
    fi
    echo "$p"
}

_source_bashrc() {
    set +eou pipefail
    shopt -u nullglob
    source ~/.bashrc
    set -eou pipefail
    shopt -s nullglob
}

_main "$@"


: <<'IGNORE_this_error'
**** The executable "caRepeater" couldn't be located
**** because of errno = "No such file or directory".
**** You may need to modify your PATH environment variable.
**** Unable to start "CA Repeater" process.
IGNORE_this_error
