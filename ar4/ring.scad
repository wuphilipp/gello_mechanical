$fa = 1;
$fs = 0.4;

module ring() {
    // height = 24
    translate([-100,-100,0])
    import("ur5_support_ring.stl");
}
    

module ringtop() {
    difference() {
        ring();
        cube([100,100,23*2], center=true);
    }
}

translate([0,0,1]) ringtop();
translate([0,0,2]) ringtop();
difference() {
    ring();
    translate([0,45,16]) rotate([90,0,0]) cylinder(h=20, r=5);
}


