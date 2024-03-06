$fa = 1;
$fs = 0.4;

width = 20;
thickness = 8;

arm_width = width+4;

scale_factor = 0.7;
j2_offset = 64.20*scale_factor;
arm1_length = 305*scale_factor;
arm2_length = 222.63*scale_factor;

dynamixel_width = 20;
dynamixel_length = 34;
dynamixel_height = 23;
dynamixel_full_height = dynamixel_height + 3;
dynamixel_horn_diam = 16;
dynamixel_horn_dist = 1.5;

dynamixel_top_length = dynamixel_horn_diam/2 + dynamixel_horn_dist;
dynamixel_bottom_offset = dynamixel_length - dynamixel_horn_diam/2 - dynamixel_horn_dist;
echo("dynamixel_bottom_offset", dynamixel_bottom_offset);

module borehole() {
    translate([0,0,3.1+50/2]) cylinder(h=50, r=4/2, center=true);
    cylinder(h=100, r=2.35/2, center=true);
}

module horn_borehole(borehole_length=10, borehole_diameter=4) {
    translate([0,0,3.1+borehole_length/2]) cylinder(h=borehole_length, r=borehole_diameter/2, center=true);
    translate([0, 0, 5]) cylinder(h=11, r=2.35/2, center=true);
}

module base_borehole(borehole_length=10, borehole_diameter=4) {
    translate([0,0,1.5+borehole_length/2]) cylinder(h=borehole_length, r=borehole_diameter/2, center=true);
    translate([0, 0, 5]) cylinder(h=11, r=2.35/2, center=true);
}

module l1() {
    padding = 1.5;
    
    difference() {
        linear_extrude(thickness) {
            translate([-width/2, 0, 0])
                square([width, j2_offset+width/2+padding]);
            circle(width/2);
        }

        dynamixel();
    }

    
    
    difference() {
        translate([0, -dynamixel_width/2 + j2_offset, 0])
            translate([-thickness/2, -padding, 0])
            cube([thickness, dynamixel_width+2*padding, dynamixel_length+padding+thickness]);

            translate([-(dynamixel_full_height + thickness/2), j2_offset, dynamixel_length-9.5+thickness])
                rotate([90, 0, -90])
                dynamixel();
    }
}

l1();

module dynamixel(borehole_length=10, horn_rotation=0, borehole_diameter=4) {
    width = 20;
    length = 34;
    height = 23;
    
    horn_height = 3;
    diam = 16;
    horn_dist = 1.5; // distance from top of dynamixel to top horn
    
    translate([-width/2, -(length - diam/2 - horn_dist), -(height+horn_height)])
    color("red", 0.3) {
        cube([width, length, height]);
        translate([width/2, length-diam/2-1.5, 1]) cylinder(h=height+horn_height-1, r=diam/2);
    }
    
    // fasteners
    
    color("green", 0.3) {
        rotate([0, 0, horn_rotation]) {
            translate([6,0,0]) horn_borehole(borehole_length, borehole_diameter=borehole_diameter);
            translate([-6,0,0]) horn_borehole(borehole_length, borehole_diameter=borehole_diameter);
            translate([0,6,0]) horn_borehole(borehole_length, borehole_diameter=borehole_diameter);
            translate([0,-6,0]) horn_borehole(borehole_length, borehole_diameter=borehole_diameter);
        }
        
        translate([dynamixel_width/2-2, dynamixel_top_length-2 ,-dynamixel_full_height]) rotate([180,0,0]) base_borehole(borehole_length);
        translate([-(dynamixel_width/2-2), dynamixel_top_length-2 ,-dynamixel_full_height]) rotate([180,0,0]) base_borehole(borehole_length);
        translate([dynamixel_width/2-2, -((dynamixel_length-dynamixel_top_length)-2) ,-dynamixel_full_height]) rotate([180,0,0]) base_borehole(borehole_length);
        translate([-(dynamixel_width/2-2), -((dynamixel_length-dynamixel_top_length)-2), -dynamixel_full_height]) rotate([180,0,0]) base_borehole(borehole_length);
        
        translate([dynamixel_width/2 - 5/2, dynamixel_top_length-10/2-14, 5-dynamixel_full_height-10]) cube([5, 10, 10], center=true);
        translate([-(dynamixel_width/2 - 5/2), dynamixel_top_length-10/2-14, 5-dynamixel_full_height-10]) cube([5, 10, 10], center=true);
    }
}

// j1
dynamixel();

// j2
translate([-(dynamixel_full_height + thickness/2), j2_offset, dynamixel_length-9.5+thickness])
    rotate([90, 0, -90])
    dynamixel();

module arm1(dynamixels=false) {
    
    difference() {
        linear_extrude(thickness) {
            translate([-arm_width/2, 0, 0])
                square([arm_width, arm1_length+dynamixel_top_length+2]);
                circle(arm_width/2);
        }
        
        translate([0,0,thickness])
            rotate([0,180,0])
            dynamixel();
    
        translate([0, arm1_length, dynamixel_full_height+thickness])
            dynamixel();
    }
    
    if (dynamixels) {
        translate([0,0,thickness])
            rotate([0,180,0])
            dynamixel();
    
        translate([0, arm1_length, dynamixel_full_height+thickness])
            dynamixel();
    }
}

module arm2(dynamixels=false) {
    offset = arm2_length - thickness - dynamixel_full_height - thickness - dynamixel_bottom_offset;
    difference() {
        union() {
            translate([0, 0, -thickness/2])
            linear_extrude(thickness) {
                translate([-arm_width/2, 0, 0])
                    square([arm_width, offset]);
                    circle(arm_width/2);
            }  
            
            translate([0, dynamixel_full_height+thickness+offset, 0]) {
                translate([0, -(dynamixel_full_height+thickness/2), dynamixel_top_length-2])
                cube([arm_width, thickness, dynamixel_length+3], center=true);
                
                if (dynamixels) {
                    rotate([-90, 0, 0])
                        dynamixel();
                }
            }
    
            if (dynamixels) {
                translate([0,0,thickness/2])
                    rotate([0,180,0])
                    dynamixel();
            
            }
            
        } // union
        
        translate([0,0,thickness/2])
            rotate([0,180,0])
            dynamixel();
        
        translate([0, dynamixel_full_height+thickness+offset, 0])
            rotate([-90, 0, 0])
            dynamixel();
    
    }
    
}

module wrist(dynamixels=false) {
    offset = 20;
    wrist_offset = 36.25*scale_factor;
    
    j4_offset = dynamixel_bottom_offset+thickness;
    
    
    
    if (dynamixels) {
        rotate([-90, -90, 0])
        dynamixel();
        
        translate([-(dynamixel_top_length+thickness+2), j4_offset, 0])
        rotate([0, 90, 0])
        dynamixel(horn_rotation=90);
        
        translate([0, j4_offset+wrist_offset, 0])
        rotate([-90, 90, 0])
        dynamixel();
    }
    
    difference() {
        union() {
            translate([-(dynamixel_bottom_offset+dynamixel_full_height-3), 0, -arm_width/2])
            cube([dynamixel_length+dynamixel_full_height-3, thickness, arm_width]);
            
            translate([-(thickness+dynamixel_top_length+2+dynamixel_full_height+thickness), 0, -arm_width/2])
            cube([thickness, dynamixel_length+thickness+1.5, arm_width]);
            
            translate([-(dynamixel_top_length+2)-thickness, wrist_offset-3, -arm_width/2])
            cube([dynamixel_length+1.5+2+thickness, thickness+1.5, arm_width]);
            
            translate([-(thickness+dynamixel_top_length+2), thickness+dynamixel_bottom_offset-dynamixel_horn_diam/2-1.5, -arm_width/2])
            cube([thickness, width, arm_width]);
        }
        
        rotate([-90, -90, 0])
        dynamixel();
        
        translate([-(dynamixel_top_length+thickness+2), j4_offset, 0])
        rotate([0, 90, 0])
        dynamixel(100, horn_rotation=45, borehole_diameter=5);
        
        translate([0, j4_offset+wrist_offset, 0])
        rotate([-90, 90, 0])
        dynamixel();
    }
}


translate([-(thickness+dynamixel_full_height+thickness/2), j2_offset, dynamixel_bottom_offset+thickness])
rotate([0, 90, 0]) {
    arm1(false);
    
    translate([0, arm1_length, thickness+dynamixel_full_height+thickness-thickness/2])
    rotate([0, 180, 0]) 
    union() {
        arm2(true);
        
        offset = arm2_length - thickness - dynamixel_full_height - thickness - dynamixel_bottom_offset;
        translate([0, offset + thickness + dynamixel_full_height, 0])
        rotate([0, 90, 0])
        wrist(true);
    }
}
