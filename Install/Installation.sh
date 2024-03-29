#PLEASE NOTE: This script should be ran with "sudo" for proper installation.

#Install needed packages first
apt install -y git python3 ngspice tk-dev libcairo2-dev mesa-common-dev

#Please uncomment and change the various paths that are defined here for the script to work - note that these directories must already exist for the installation to function properly

#OpenROAD-flow-scripts installation path
#OPENROAD_PATH = ~/openROAD

#Magic VLSI installation path
#MAGIC_PATH = ~/magic

#SKY130 PDK installation path
#SKY130_PATH = ~/SKY130

#Netgen installation path
#NETGEN_PATH = ~/netgen

#Install openROAD-flow-scripts
cd $OPENROAD_PATH
git clone --recursive https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts
cd OpenROAD-flow-scripts
./setup.sh
./build_openroad.sh --local

#Install Magic VLSI
cd $MAGICPATH
git clone https://github.com/RTimothyEdwards/magic.git
cd magic
./configure
make
make install

#Install the SKY130HD PDK
cd $SKY130_PATH
git clone https://github.com/RTimothyEdwards/open_pdks.git
cd open_pdks
./configure --enable-sky130-pdk --with-sky130-variants=A --enable-primitive-sky130 –disable-io-sky130 --disable-sc-hs-sky130 --enable-sc-hd-sky130 --disable-sc-ms-sky130 --disable-sc-ls-sky130 --disable-sc-lp-sky130 --disable-sc-hdll-sky130 --disable-sc-hvl-sky130 –disable-gf180mcu-pdk
make
make install

#Install Netgen
cd $NETGEN_PATH
git clone https://github.com/RTimothyEdwards/netgen.git
cd netgen
./configure
make
make install
