# Makefile for RPi image with static IP, SSH autostart
# and up-to-date packages.
#
# Note that this file assumes use of APT in install-dependencies
#
# Image manipulation instructions for Raspbian were found at
# http://raspberrypi.stackexchange.com/questions/855/is-it-possible-to-update-upgrade-and-install-software-before-flashing-an-image
#
# Links to images found at http://www.raspberrypi.org/downloads ->
# http://downloads.raspberrypi.org/images/raspbian/2012-12-16-wheezy-raspbian/2012-12-16-wheezy-raspbian.zip


all: install-dependencies download-image fix-image

install-dependencies:
	# Ensure system is up to date
	sudo apt-get update
	sudo apt-get upgrade
	# and install some new software (if already not installed)
	sudo apt-get install binfmt-support qemu qemu-user-static unzip

download-image:
	wget http://files.velocix.com/c1410/images/raspbian/2012-12-16-wheezy-raspbian/2012-12-16-wheezy-raspbian.zip
	wget http://downloads.raspberrypi.org/images/raspbian/2012-12-16-wheezy-raspbian/2012-12-16-wheezy-raspbian.zip.sha1
	sed -i s:/home/eben/images/raspbian/2012-12-16-wheezy-raspbian/:: 2012-12-16-wheezy-raspbian.zip.sha1
	sha1sum -c 2012-12-16-wheezy-raspbian.zip.sha1
	unzip 2012-12-16-wheezy-raspbian.zip
	mv 2012-12-16-wheezy-raspbian.img oxberrypis.img

fix-image: mount static-ssh-update umount

chroot: mount chroot-main umount

chroot-main:
	sudo chroot mnt /bin/bash

mount:
	mkdir mnt

	# offset = starting block * sector size
	# (both values can be found by running
	# `fdisk -l oxberrypis.img`
	sudo mount -o loop,offset=62914560 oxberrypis.img mnt

	sudo mount --rbind /dev mnt/dev
	sudo mount -t proc none mnt/proc
	sudo mount -o bind /sys mnt/sys

	sudo cp /usr/bin/qemu-arm-static mnt/usr/bin/

umount:
	sudo rm mnt/usr/bin/qemu-arm-static

	sudo umount -l mnt
	rm -rf mnt

static-ssh-update:
	sudo cp interfaces mnt/etc/network/

	# Following is a hack caused by New College
	# network setup, which blocks DNS requests
	# to external servers. If removed no host
	# can be resolved.
	sudo mv mnt/etc/resolv.conf resolv.conf.bak
	sudo cp /etc/resolv.conf mnt/etc/resolv.conf

	# Enable SSH
	sudo chroot mnt update-rc.d ssh enable

	# Update and upgrade packages
	sudo chroot mnt apt-get update
	sudo chroot mnt apt-get -y upgrade

	# Restore original resolv configuration
	sudo mv resolv.conf.bak mnt/etc/resolv.conf

clean:
	rm 2012-12-16-wheezy-raspbian.zip
	rm 2012-12-16-wheezy-raspbian.zip.sha1
	rm oxberrypis.img
