# Installation guide

## Install Isaac Sim locally

Ensure that Isaac Sim 4.5.0 is installed. Follow the instructions on the [official website](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/download.html) to install Isaac Sim locally. You can install Isaac Sim via pip, or by using pre-built binaries.

## Install Isaac IMI
Clone the isaacimi repository:
```bash
git clone git@gitlab.kit.edu:kit/imi/mairo_commons/nvidia-omniverse/isaacimi.git
```

If you installed Isaac Sim via pip, Isaac IMI needs to be installed in the same Python environment where Isaam Sim was installed to ensure compatibility with its dependencies. Activate the Python environment first before installing isaacimi with pip:
```bash
cd isaacimi
pip install -e .
```


If you installed Isaac Sim using prebuilt binaries, use the [built-in Python environment](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/python_scripting/manual_standalone_python.html) provided by Isaac Sim. Navigate to the Isaac Sim root folder (where you unzipped the Isaac Sim folder during installation) and use the provided `python.sh` script:
```bash
cd path/to/isaacsim
./python.sh -m pip install -e path/to/isaacimi
```