# SlicOps and Podman

SlicOps is deployed in a Podman container image.

## Building the image

You'll need to clone the repository and build the image:

```
git clone https://github.com/slaclab/slicops
cd slicops
curl https://radia.run | bash -s container-build
```

That will start the process of building the image on your machine.

If your curious about what those commands mean please read on. If you
just want to build an image so you can run it then you can skip this
information and jump to the next section.

The command can be broken into two parts.

First is `curl https://radia.run`. [Curl](https://curl.se/docs/manpage.html)
is a tool for making http requests from a shell. `radia.run` is a
website that RadiaSoft hosts which returns a shell script. You
can try running `curl https://radia.run` yourself in your shell. You'll see
the shell script printed out. The shell script that is downloaded
allows one to run one of [RadiaSoft's
"installers"](https://github.com/radiasoft/download). These are other
shell scripts that do some action. In our case that action is
`container-build`.

Now we are at the second part of the command `bash -s container-build`. You
can guess from the name of the command that it builds a container. In
our case, it is going to build the slicops container. If you're
curious about that command you can see what is run
[here](https://github.com/radiasoft/download/blob/master/installers/container-build/radiasoft-download.sh).
We'll breeze over the exact details and get to what is important, the
`build.sh` file. `curl https://radia.run | bash -s container-build` ends up calling
`build.sh` in the `container-conf` [directory of the SlicOps
repo](https://github.com/slaclab/slicops/blob/main/container-conf/build.sh).
That file has three important functions: `build_vars`, `build_as_root`, and `build_as_run_user`.

- `build_vars`: This is the first function that is called in the
script. It sets up variables that will be used in the script and by
other code in `container-build`. The most important is
`build_image_base`. This is set to `radiasoft/python3`. Podman images
are built in "layers". What that means is an image can be built on top
of another image. In our case we are building the SlicOps image on top
of the `radiasoft/python3` image. The `radiasoft/python3` image is a
Fedora image with some of the basic necessities (e.g. gcc) installed.
Importantly for us, it has `python3` installed (SlicOps is a Python
application).

- `build_as_root`: This function does all of its steps as the
root user. For SlicOps that is installing packages like Node.JS and
some of the EPICS dependencies.

- `build_as_run_user`: Similar to `build_as_root` this runs install
steps. But, it runs them as the `$run_user`. The `$run_user` is the
owner of the files in the container. For SlicOps this step installs
EPICS and installs the SlicOps package.

Once all of these are steps run, the build container has all the
dependences that are required run SlicOps. Podman then creates an
image of this container. Podman uses this "compiled" image very
efficiently with the run command.

Running `container-build` will take many minutes.

## Running the image

Now we have built (or you got from someone / downloaded) the image and
we are ready to run it.

To run the image

```
podman run --rm --interactive --tty --network=host slaclab/slicops
```

Breaking down the parts of that command:
- `podman`: Call the podman program
- `run`: The command we want. In this case, to run the image.
- `--rm`: Automatically remove the container when it exits. If we
  don't have this flag the container will be left "paused" when you
  exit. These paused containers tend to accumulate and just take up
  space on your machine.
- `--interactive`: Keep STDIN open. This will allow us to enter
  commands inside of the running container.
- `--tty`: Allocate a "pseudo-tty". Basically, it makes working
   inside of the container just like a normal interactive shell session.
- `--network=host`: Use the host machine's network. This allows a web
  server (or any other process) in the container to appear on the host
  (your computer). Your computer's browser can connect to the web
  server with an ordinary URL (https://localhost:<port>).
- `slaclab/slicops`: This is the name of the image we want to run.

The container starts a bash shell.
From there you can start the necessary software.

First, start the EPICS sim detector which is a simulated detector that the rest of the application
will use to read images from.
```
slicops epics sim-detector &
```

Next, start the "ui-api". This is the Python web server that
interfaces between EPICS and the GUI to read from PV's and send the
outputs to the browser.

```
slicops service ui-api --prod
```

Finally, access the application from your web browser. Visit
[http://localhost:8080](http://localhost:8080).
