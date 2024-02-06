# GELLO Mechanical
This is the central repo that holds the mechanical parts for GELLO. See the website for the paper and other resources for GELLO https://wuphilipp.github.io/gello_site/
If you have already built your GELLO, please see https://github.com/wuphilipp/gello_software for software setup and usage.

## Organization
Currently we support 4 robot types. The 3 from the original paper:
 * The Franka (from Franka Robotics)
 * UR5 (from Universal Robotics)
 * xArm7 (from uFactory)
And 2 from community contributions:
 * Lite6 (from uFactory). The lite6 design is contributed from [EL2031watson](https://twitter.com/EL2031watson). See the instructions [here](./lite6/README.md).
 * AR4 (from [Annin Robotics](https://www.anninrobotics.com/)) contributed by [@adob](https://github.com/adob)

Each robot has its own folder, with its own robot specific parts. The gripper files are in its own folder, which is shared across robots.
The stls can be printed directly. See the assembly instructions for more detailed instructions.
 * `franka`: contains Franka specific parts
 * `ur5`: contains UR5 specific parts
 * `xarm7`: contains xArm7 specific parts
 * `lite6`: contains Lite6 specific parts and instructions.
 * `ar4`: contains AR4 specific parts
 * `gripper`: contains the parts for the gripper, which is also shared across robots

## Assembly Instructions
Instructions for assembly can be found here: [Assembly Instructions](https://docs.google.com/document/d/1pzV8LDIGZh6zq8z-ZyKjUZ1ISkdCQctfu_05-ZY95eg/edit?usp=sharing)

## Notes
Currently we only provide access to the raw STL files. If you would like access to the source files (Solidworks), please contact me.
If you run into any issues during assembly, please open a github issue.

## Contribution
If you have made any improvements to GELLO or made designs for a new robot, please contribute by making a pull request!

# Citation
```
@misc{wu2023gello,
    title={GELLO: A General, Low-Cost, and Intuitive Teleoperation Framework for Robot Manipulators},
    author={Philipp Wu and Yide Shentu and Zhongke Yi and Xingyu Lin and Pieter Abbeel},
    year={2023},
}
```
