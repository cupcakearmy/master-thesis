#!/bin/sh

TARGET=~/.fonts
mkdir -p $TARGET
unzip -o -d "$TARGET/roboto_mono" "./fonts/Roboto_Mono.zip"
unzip -o -d "$TARGET/open_sans" "./fonts/Open_Sans.zip"
