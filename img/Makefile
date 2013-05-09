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

#IMAGE_URL = http://files.velocix.com/c1410/images/raspbian/2012-12-16-wheezy-raspbian/2012-12-16-wheezy-raspbian.zip
IMAGE_URL = http://raspberrypi.reon.hu/images/raspbian/2013-02-09-wheezy-raspbian/2013-02-09-wheezy-raspbian.zip
#IMAGE_URL = http://ftp.snt.utwente.nl/pub/software/rpi/images/debian/7/2012-08-08-wheezy-armel/2012-08-08-wheezy-armel.zip
IMAGE_NAME := `basename $(IMAGE_URL) .zip`

all: install-dependencies download-image fix-image

install-dependencies:
	# Ensure system is up to date
	sudo apt-get update
	sudo apt-get upgrade
	# and install some new software (if already not installed)
	sudo apt-get install binfmt-support qemu qemu-user-static unzip

download-image:
	wget $(IMAGE_URL)
	wget $(IMAGE_URL).sha1
	sed -i s:/home/eben/images/raspbian/$(IMAGE_NAME)/:: $(IMAGE_NAME).zip.sha1
	sha1sum -c $(IMAGE_NAME).zip.sha1
	unzip $(IMAGE_NAME).zip
	mv $(IMAGE_NAME).img oxberrypis-$(IMAGE_NAME).img

fix-image: mount static-ssh-update umount

chroot: mount chroot-main umount

chroot-main:
	sudo chroot mnt /bin/bash

mount:
	mkdir mnt

	# offset = starting block * sector size
	# (both values can be found by running
	# `fdisk -l oxberrypis.img`
	sudo mount -o loop,offset=62914560 oxberrypis-$(IMAGE_NAME).img mnt

	sudo mount --rbind /dev mnt/dev
	sudo mount -t proc none mnt/proc
	sudo mount -o bind /sys mnt/sys

	sudo cp /usr/bin/qemu-arm-static mnt/usr/bin/
	sudo mv mnt/etc/ld.so.preload ld.so.preload.bak

umount:
	sudo mv ld.so.preload.bak mnt/etc/ld.so.preload

	sudo rm mnt/usr/bin/qemu-arm-static
	sudo umount -l mnt
	rm -rf mnt
	sha1sum oxberrypis-$(IMAGE_NAME).img > oxberrypis-$(IMAGE_NAME).img.sha1

static-ssh-update:
	#sudo cp interfaces mnt/etc/network/

	sudo mkdir -p mnt/home/pi/.ssh
	sudo cp id_rsa.pub mnt/home/pi/.ssh/authorized_keys
	sudo chmod 600 mnt/home/pi/.ssh/authorized_keys

	sudo rm -rf mnt/home/pi/OxBerryPis
	sudo git clone .. mnt/home/pi/OxBerryPis

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
	sudo chroot mnt apt-get -y install git python-setuptools python-virtualenv python-dev build-essential libtool autoconf automake uuid uuid-dev
	sudo chroot mnt apt-get clean
	sudo chroot mnt virtualenv /home/pi/venv
	
	sudo chroot mnt /home/pi/venv/bin/pip install pyzmq --install-option="--zmq=bundled"

	sudo chroot mnt bash -c "cd /home/pi/OxBerryPis && /home/pi/venv/bin/python setup.py develop"

	# Restore original resolv configuration
	sudo mv resolv.conf.bak mnt/etc/resolv.conf

	sudo chown -R 1000:1000 mnt/home/pi

clean:
	rm $(IMAGE_NAME).zip
	rm $(IMAGE_NAME).zip.sha1
	rm oxberrypis-$(IMAGE_NAME).img
