# SlicOps and Podman

SliCops is deployed in a Podman container image.

## Building the image

From the repository root run:

```
curl radia.run | container-build
```

That will start the process of building the image on your machine.

If your curious about what those commands mean please read on. If you
just want to build an image so you can run it then you can skip this
information and jump to the next section.

The command can be broken into two parts.

First is `curl radia.run`. [Curl](https://curl.se/docs/manpage.html)
is a tool for making http requests from a shell. `radia.run` is a
website that RadiaSoft hosts which returns a shell script. You
can try running `curl radia.run` yourself in your shell. You'll see
the shell script printed out. The shell script that is downloaded
allows one to run one of [RadiaSoft's
"installers"](https://github.com/radiasoft/download). These are other
shell scripts that do some action. In our case that action is
`container-build`.

Now we are at the second part of the command `container-build`. You
can guess from the name of the command that it builds a container. In
our case, it is going to build the slicops container. If you're
curious about that command you can see what is run
[here](https://github.com/radiasoft/download/blob/master/installers/container-build/radiasoft-download.sh).
We'll breeze over the exact details and get to what is important, the
`build.sh` file. `curl radia.run | container-build` ends up calling
the `build.sh` file in the `container-conf` [directory of this
repo](https://github.com/slaclab/slicops/blob/main/container-conf/build.sh).
That file has three important functions.

First, `build_vars`. This is the first function that is called in the
script. It sets up variables that will be used in the script and by
other code in `container-build`. The most important is
`build_image_base`. This is set to `radiasoft/python3`. Podman images
are built in "layers". What that means is an image can be built on top
of another image. In our case we are building the SlicOps image on top
of the `radiasoft/python3` image. The `radiasoft/python3` image is a
Fedora image with some of the basic necessities (e.g. gcc) installed.
Importantly for us, it has `python3` installed (SlicOps is a Python
application).

Next up is `build_as_root`. This function does all of its steps as the
root user. For SlicOps that is installing packages like Node.JS and
some of the EPICS dependencies.

Finally, we have `build_as_run_user`. Similar to `build_as_root` this
runs install steps. But, it runs them as the `run_user`. That is the
user that will be running the application inside of the container. For
SliCops this step installs EPICS and installs the SlicOps package.

Once all of these steps are run then the image has all of the
dependencies that are required to run SliCops.

Running `container-build` will take many minutes.

## Running the image

Now we have built (or you got from someone / downloaded) the image and
we are ready to run it.

To run the image

```
podman run --rm --interactive --tty --network=host slaclab/slicops /bin/bash
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
- `--tt`: Allocate a "pseudo-teletypewriter". Basically, make working
  inside of the container in a shell work like how a using a terminal
  works on your computer.
- `--network=host`: Use the host machines network stack. This means
  that any http server started in the container will appear as if it
  was started on your computer. You'll be able to connect to it over
  localhost.
- `slaclab/slicops`: This is the name of the image we want to run.
- `/bin/bash`: Run the bash shell when the container is started

Once the container is started you will be dropped into a bash shell.
From there you can start the necessary software.

First, start the EPICS sim detector which is a simulated detector that the rest of the application
will use to read images from.
```
slicops epics sim-detector
```

Next, start the "ui-api". This is the Python web server that
interfaces between EPICS and the GUI to read from PV's and send the
outputs to the browser.

```
slicops service ui-api
```

Next, start the GUI. This is an Angular application that we access in
our web browser

```
cd ~/src/slaclab/slicops/ui/
npx ng serve --port 8080
```

Finally, access the application from your web browser. Visit
[http://localhost:8080](http://localhost:8080).
