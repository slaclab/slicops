## Running a graphical application in podman over X11

Setup for RS development machines:
```
# On mac install xquartz https://www.xquartz.org/

# ssh into server with X11 forwarding enabled
ssh -o ForwardX11=yes ...

# ssh into development vm (again enable X11 forwarding)
ssh -o ForwardX11=yes ...

# in vm install podman
dnf install -y podman

# Run podman with X11 setup
podman run --rm -it --user=root -e DISPLAY=$DISPLAY -v $HOME/.Xauthority:/root/.Xauthority --network=host docker.io/radiasoft/python3 bash
# dnf install -y xeyes
<snip>
xeyes
# See eyes on Mac host
```

For the ACR an X11 server will need to be installed on the host
machine. Then run the podman command. It may be that we need to share
the X11 socket file `-v /tmp/.X11-unix:/tmp/.X11-unix:rw` instead of
the `.Xauthority` file
