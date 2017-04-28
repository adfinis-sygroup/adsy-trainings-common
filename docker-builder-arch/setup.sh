#!/bin/bash
# target image: base/archlinux

pacman -Sy
pacman -S  --noconfirm pacman pacman-mirrorlist
pacman-db-upgrade
pacman-key --init

pacman -S  --noconfirm archlinux-keyring ca-certificates
update-ca-trust

pacman -Su --noconfirm
pacman -S --noconfirm python-jinja python-yaml wkhtmltopdf pandoc xorg-server-xvfb git \
 wget unzip fontconfig xorg-fonts-encodings xorg-mkfontdir xorg-mkfontscale


cd /opt
wget http://www.latofonts.com/download/Lato2OFL.zip
unzip Lato2OFL.zip
cd Lato2OFL
cp *ttf /usr/share/fonts/TTF/
fc-cache
