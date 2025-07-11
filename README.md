### SlicOps: Beam Physics Control Interface

SlicOps controls particle accelerators and beamlines. The web
interface is comprised of SlicLets, componentized applications, which
allow operators to read and write EPICS controls.  The Python library
can be used standalone to control accelerators and beamlines
programmatically.

Repository: https://github.com/slaclab/slicops

Documentation: https://slicops.readthedocs.io


### Setup Development
Note, these instructions are intended for use on dev-srv09.

#### Install Conda

Check if conda is installed:

```sh
conda
```

If command not found, install:

```sh
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O x.sh
bash x.sh
rm x.sh
source ~/.bashrc
```

#### Install Apptainer

Check if apptainer is installed:

```sh
apptainer
```

If command not found, install:

```sh
curl -s https://raw.githubusercontent.com/apptainer/apptainer/main/tools/install-unprivileged.sh | \
    bash -s - ~/apptainer
cat >> ~/.bashrc <<'EOF'
if [[ ! :$PATH: =~ :$HOME/apptainer/bin: ]]; then
    PATH=$HOME/apptainer/bin/apptainer:$PATH
fi
EOF
source ~/.bashrc
```

If you are at SLAC, add this to your `~/.bashrc`:

```sh
export SLICOPS_APPTAINER_SIF=~nagler/slicops.sif
```

If you are not at SLAC, slicops.sif will get built when you start the servers.


#### Clone Repo

First step is to clone the repo. We use `~/src/slaclab/slicops` in
these examples, but any directory is fine. All the software operates
relative to the repo:

```sh
mkdir -p ~/src/slaclab
cd ~/src/slaclab
git clone https://github.com/slaclab/slicops
```

#### Development Servers

In development, SlicOps uses three servers:

- sim - [ADSimDetector](https://areadetector.github.io/areaDetector/ADSimDetector/simDetector.html) simulates a camera called `DEV_CAMERA`.
- vue - [vite](https://vite.dev) serves the browser [Vue.js](https://vuejs.org) in development mode.
- api - [slicops.pkcli.service.ui_api](https://github.com/slaclab/slicops/blob/main/slicops/pkcli/service.py) is the web server to connect to, which serves APIs, communicates with ADSimDetector, and proxies vite.

#### First Time Install
NOTE: following the steps below will create a slicops conda env, and your own sif file, if they are not found on your path.
Creating a sif file can take up to 45 minutes.  

The first time run this command:

```sh
$ bash ~/src/slaclab/slicops/etc/run.sh install
<installing conda env, node, python, etc.>

Created <your home>/src/slaclab/slicops/run/bashrc.sh
which sets:

export SLICOPS_BASE_PORT=<your port>

You can also put this value in your ~/.bashrc.
```

You can add this to your `~/.bashrc`, and then remove the file
`run/bashrc.sh`. Source your bashrc before starting other servers.

You will need to tunnel this port if you are using ssh. Logout of ssh,
and login again with:

```sh
ssh -L localhost:<your port>:localhost <your host>
```

#### Start sim

Once installed, start `sim`:

```sh
$ bash ~/src/slaclab/slicops/etc/run.sh sim
/home/vagrant/src/slaclab/slicops/slicops/pkcli/epics.py:75:_log log: /sdf/home/n/nagler/sim_detector.log
/home/vagrant/src/slaclab/slicops/slicops/pkcli/epics.py:98:sim_detector started pid=200; sleep 2 seconds
/home/vagrant/src/slaclab/slicops/slicops/pkcli/epics.py:101:sim_detector initializing sim detector
/home/vagrant/src/slaclab/slicops/slicops/pkcli/epics.py:103:sim_detector waiting for pid=200 to exit
```

#### Start vue

```sh
$ bash ~/src/slaclab/slicops/etc/run.sh vue
<some output and then>
  VITE v6.3.5  ready in 701 ms

  ➜  Local:   http://localhost:<your port + 1>/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

#### Start api

```sh
$ bash ~/src/slaclab/slicops/etc/run.sh api
Ignore error about caRepeater couldn't be located.

Connect to: http://localhost:<your port>

<noise about import pkg_resources>
../../../../miniconda3/envs/slicops/lib/python3.12/site-packages/pykern/pkasyncio.py:61:_do name=None ip=127.0.0.1 port=<your port>
```

#### Visit in Browser

If everything is set up and tunneling is working, you can visit
`http://localhost:<your port>` in the browser.

#### License

License: http://github.com/slaclab/slicops/LICENSE

Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
