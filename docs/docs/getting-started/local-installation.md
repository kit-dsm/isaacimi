# Installation guide

## Install Isaac Sim locally

Ensure that Isaac Sim 4.5.0 is installed. Follow the instructions on the [official website](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/download.html) to install Isaac Sim locally. You can install Isaac Sim via pip, or by using pre-built binaries.

## Install Isaac IMI
Clone the isaacimi repository:
```bash
git clone git@gitlab.kit.edu:kit/imi/mairo_commons/nvidia-omniverse/isaacimi.git
```

> Isaac IMI needs to be installed in the same Python environment where Isaam Sim was installed to ensure compatibility with its dependencies.

**Case 1**: If you installed Isaac Sim using pre-built binaries, set up a symbolic link between the installed Isaac Sim root folder and `_isaac_sim` in the Isaac IMI directory before proceeding:
```bash
ln -s <path/to/isaacsim> isaacimi/_isaac_sim
```

**Case 2**: If you installed Isaac Sim via pip in a virtual environment, activate your virtual environment before proceeding.

Run the install script:
```bash
./isaacimi/scripts/install.sh
```