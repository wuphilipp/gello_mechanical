# GELLO Mechanical
This is the central repo that holds the mechanical parts for GELLO. See the website for the paper and other resources for GELLO https://wuphilipp.github.io/gello_site/

## Organization

Currently we support 3 robot types: The Franka, UR5, xArm7.
Each robot has its own folder, with its own robot specific parts. The gripper files are in its own folder, which is shared across robots.
The stls can be printed directly. See the assembly instructions for more detailed instructions.
 * `franka`: contains Franka specific parts
 * `ur5`: contains UR5 specific parts
 * `xarm7`: contains xArm7 specific parts
 * `gripper`: contains the parts for the gripper, which is also shared across robots

## Assembly Instructions
Instructions for assembly can be found here: [Assembly Instructions](https://docs.google.com/document/d/1pzV8LDIGZh6zq8z-ZyKjUZ1ISkdCQctfu_05-ZY95eg/edit?usp=sharing)

## Notes
Currently we only provide access to the raw STL files. If you would like access to the source files (Solidworks), please contact me.
If you run into any issues during assembly, please open a github issue.

# Citation

```
@misc{wu2023gello,
    title={GELLO: A General, Low-Cost, and Intuitive Teleoperation Framework for Robot Manipulators},
    author={Philipp Wu and Yide Shentu and Zhongke Yi and Xingyu Lin and Pieter Abbeel},
    year={2023},
}
```
