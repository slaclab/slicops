#!/bin/bash
#
# Start development environment, including building conda environment "slicops"
#
# Start in this order:
#   bash etc/run.sh sim
#   bash etc/run.sh vue
#   bash etc/run.sh api
set -eou pipefail
shopt -s nullglob

_root_dir=$(cd "$(dirname "$0")/.." && pwd)
_run_dir=$_root_dir/run
_docker_image=docker://radiasoft/slicops
declare -A _port_map=(
    [api]=0
    [repeater]=2
    [server]=3
    [vue]=1
)
_run_env=$_run_dir/bashrc.sh
_python_version=3.12.10
_sif=${SLICOPS_APPTAINER_SIF:-$_run_dir/slicops.sif}
_sim_dir=/home/vagrant/.local/epics/extensions/synApps/support/areaDetector-R3-12-1/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector
_vue_dir=$_root_dir/ui

_assert_conda_env() {
    if ! type -t conda &> /dev/null; then
        _err 'conda not installed; please install and rerun'
    fi
    _source_bashrc
    if ! conda activate slicops &> /dev/null; then
        _msg 'Creating conda environment slicops'
        conda create --quiet --yes --name slicops
        if ! conda activate slicops; then
            _err 'unable to activate slicops after creating'
        fi
    fi
    if type -t slicops &> /dev/null; then
        return
    fi
    _assert_conda_package python "$_python_version"
    _assert_conda_package nodejs
    _msg 'Installing slicops'
    cd "$_root_dir"
    pip install -q -e .
}

_assert_conda_package() {
    declare name=$1
    declare version=${2:-}
    if ! conda list | grep -q "^$name "; then
        declare p=$name${version:+=$version}
        _msg "Installing $p"
        conda install --quiet --yes "$p"
    fi
}

_assert_sif() {
    if [[ -r $_sif ]]; then
        return
    fi
    _msg "Building $_sif from $_docker_image. This will take about 45 minutes..."
    declare f=$_run_dir/image.log
    if ! TMPDIR=$PWD apptainer build "$_sif" $_docker_image &> "$f"; then
        tail --lines=50 "$f"
        _err "build image=$_sif failed. Full log: $f"
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

_base_port() {
    declare p=${SLICOPS_BASE_PORT:-}
    if [[ $p ]]; then
        _base_port_assert "$p"
        return
    fi
    if [[ ! -r $_run_env ]]; then
        _run_env_create
    fi
    source "$_run_env"
    _base_port_assert "${SLICOPS_BASE_PORT:-}" "$_run_env"
}

_base_port_assert() {
    declare port=$1
    declare file=${2:-}
    if [[ ! $port =~ ^[0-9]+$ ]] || (( port <= 5000 )); then
        _err "SLICOPS_BASE_PORT=$port must be an integer above 5000${file:+

rm $file
and run this script again}"
    fi
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
$(compgen -A function _op_ | sed -e 's/^_op_//')

To develop, start the servers in this order in separate terminals:
bash etc/run.sh sim # sim-detector for DEV_CAMERA
bash etc/run.sh vue # vue server for javascript
bash etc/run.sh api # tornado for business logic and main server
"
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
    _cd_run_dir
    _base_port
    _assert_python_env
    _dispatch_op "$op" "${@:2}"
}

_msg() {
    echo "$*" 1>&2
}

_op_api() {
    declare e=$(_epics_env)
    declare p=$(_port api assert)
    declare v=$(_port vue)
    if ! [[ $e && $p && $v ]]; then
        return 1
    fi
    _msg "
Ignore error about caRepeater couldn't be located.

Connect to: http://localhost:$p
"
    # not in quotes, because eval
    eval $e SLICOPS_CONFIG_UI_API_VUE_PORT=$v \
         exec slicops service ui-api --tcp-port="$p"
}

_op_sim() {
    _assert_sif
    declare e=$(_epics_env assert)
    if [[ ! $e ]]; then
        return 1
    fi
    exec apptainer run --containall "$_sif" bash -c "$e slicops epics sim-detector --ioc-sim-detector-dir='$_sim_dir'"
}

_op_vue() {
    cd "$_vue_dir"
    declare v=$(_port vue assert)
    if [[ ! $v ]]; then
        return 1
    fi
    SLICOPS_VUE_PORT=$v exec npm run dev -- --host
}

_port() {
    declare name=${1:-}
    declare assert=${2:-}
    declare p=${_port_map[$name]}
    if [[ ! $p ]]; then
        _err "assertion error: _port missing port arg=${1:-<missing arg>}"
    fi
    p=$(( SLICOPS_BASE_PORT + p ))
    if [[ $assert ]] && ! _port_check "$p"; then
        _err "port=$p in use; is service=$name already running? Or, choose a different SLICOPS_BASE_PORT=$SLICOPS_BASE_PORT"
    fi
    echo "$p"
}

_port_check() {
    declare num=$1
    declare count=${2:-1}
    declare i
    for i in $(seq 0 $(( count - 1)) ); do
        if ss --tcp --udp --listening --numeric | grep -q ":$(( num + i ))"; then
            return 1
        fi
    done
}

_port_find() {
    declare -i p=$(( $(id -u) % 10000 + 10000 ))
    declare i
    for _ in {1..10}; do
        #TODO(robnagler) 4 should be a constant
        if _port_check "$p" 4; then
           echo "$p"
           return
        fi
    done
    # Should not happen
    _err 'could not find an open port; Set SLICOPS_BASE_PORT manually in ~/.bashrc'
}

_run_env_create() {
    declare p=$(_port_find)
    if [[ ! $p ]]; then
        return 1
    fi
    cat <<EOF_cat > "$_run_env"
#!/bin/bash
# Configuration dynamically generated by etc/run.sh.
# Copy to ~/.bashrc, source ~/.bashrc, and remove this file.
export SLICOPS_BASE_PORT=$p
EOF_cat
    _msg "Created $_run_env
which sets:

export SLICOPS_BASE_PORT=$p

You can also put this value in your ~/.bashrc.
"
}

_source_bashrc() {
    set +eou pipefail
    shopt -u nullglob
    source ~/.bashrc
    set -eou pipefail
    shopt -s nullglob
}

_main "$@"
