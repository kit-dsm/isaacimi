FROM nvcr.io/nvidia/isaac-sim:4.5.0

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and remove cache
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    # ROS2 Humble
    software-properties-common \
    && add-apt-repository universe \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo jammy) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-ros-base \
    ros-humble-vision-msgs \
    # Install both FastRTPS and CycloneDDS
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rmw-fastrtps-cpp \
    # This includes various dev tools including colcon
    ros-dev-tools \
    && apt -y autoremove && apt clean autoclean \
    && rm -rf /var/lib/apt/lists/* \
    # Add sourcing of setup.bash to .bashrc
    && echo "source /opt/ros/humble/setup.bash" >> ${HOME}/.bashrc

COPY . /isaacimi
# Create symlink to Isaac Sim install
RUN ln -sf /isaac-sim /isaacimi/_isaac_sim
# Install Isaam IMI
RUN /isaacimi/scripts/install.sh

WORKDIR /workspace