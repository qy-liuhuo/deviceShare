#!/bin/bash
sudo chmod 666 /dev/input/*
sudo chmod 666 /dev/uinput
sudo chmod 777 ./deviceShare
if [ -n "$WAYLAND_DISPLAY" ]; then
    echo "is wayland"
    PACKAGE="wl-clipboard"
    echo "installing wl-clipboard"
    sudo apt install wl-clipboard
    export DISPLAY=:0
    NOWUSER=$USER
    sudo touch /home/$NOWUSER/.Xauthority
    xauth generate :0 . trusted  >/dev/null 2>&1
    XAUTHORITY="/home/$USER/.Xauthority" ./deviceShare >/dev/null 2>&1 &
else
    ./deviceShare >/dev/null 2>&1 &
fi
