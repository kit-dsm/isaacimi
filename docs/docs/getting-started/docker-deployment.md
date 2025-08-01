# Isaac IMI Docker development
You can choose to run simulations with Isaac IMI in a Docker container on your local machine or a remote headless server.

!!! warning
    The Isaac IMI Docker image depends on the Isaac Sim docker image. By running the container you are implicitly agreeing to the NVIDIA Software License Agreement.

## System setup
Before running the container on your host system, follow the instructions outlined in the [Container Setup](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/install_container.html#container-setup) section of the Isaac Sim documentation.

The instructions outlined in that section section will:

1. Check if your host system can run NVIDIA Isaac Sim
2. Install the necessary NVIDIA drivers
3. Install Docker and complete the post install steps
4. Install the NVIDIA container toolkit to allow you to run GPU accelerated containers

## Run the container
Clone the Isaac IMI repo on the host system:
```
git clone https://gitlab.kit.edu/kit/imi/mairo_commons/nvidia-omniverse/isaacimi.git
```

A `Dockerfile` and `compose.yaml` are provided in the `isaacimi` root folder. To build the image, create the container, and start the container, run the following command in the root folder:
```bash
docker compose up
```

The container should now be up and running! A folder in your home directory `~/isaacimi-workspace` is bind mounted to the `/workspace` directory in the container.