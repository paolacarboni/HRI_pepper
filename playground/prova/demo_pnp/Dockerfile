FROM iocchi/pnp

ARG DEMONAME=demo_pnp

USER robot

RUN cd $HOME/src && \
    catkin_create_pkg $DEMONAME std_msgs rospy roscpp pnp_ros actionlib && \
	cd $HOME/ros/catkin_ws/src && \
	ln -s $HOME/src/$DEMONAME .

# Compile ROS packages

RUN /bin/bash -ci "cd $HOME/ros/catkin_ws; catkin_make -j1"

# Set working dir and container command

WORKDIR /home/robot

CMD /usr/bin/tmux
