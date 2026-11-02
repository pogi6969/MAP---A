// Square castle tower, 80 mm tall, 18 mm footprint. Prints upright, no supports.
$fn = 48;

W = 15;                          // shaft width
B = 18;                          // plinth and parapet width
H = 80;                          // total height
base_h  = 2;                     // plinth height
shaft_z = base_h + (B - W) / 2;  // top of the 45° plinth chamfer
flare_z = 66;                    // corbel flare starts
par_z   = flare_z + (B - W) / 2; // parapet starts (45° flare)
walk_z  = 74;                    // walkway
cren_z  = 77;                    // crenel bottom
wall    = 1.5;                   // parapet wall

module frustum(z0, w0, w1, h) translate([0, 0, z0]) linear_extrude(height = h, scale = w1 / w0) square(w0, center = true);
module box(z0, w, h) translate([-w / 2, -w / 2, z0]) cube([w, w, h]);

// stone band, 45° underside
module band(z0) { frustum(z0, W, W + 1.2, 0.6); box(z0 + 0.6, W + 1.2, 0.6); }

// pointed arch, w wide, h tall, base at y = 0
module arch2d(w, h) {
    s = h - w * sqrt(3) / 2;
    translate([-w / 2, 0]) square([w, s + 0.01]);
    translate([0, s]) intersection() {
        translate([-w / 2, 0]) circle(r = w);
        translate([ w / 2, 0]) circle(r = w);
        translate([-w / 2, 0]) square([w, w]);
    }
}

// recess into the face at `angle` (0 = +X), base at height z, floor at distance d from the axis
module recess(angle, z, d, len = 4) rotate([0, 0, angle]) translate([d, 0, z]) rotate([90, 0, 90]) linear_extrude(height = len) children();

difference() {
    union() {
        box(0, B, base_h);
        frustum(base_h, B, W, shaft_z - base_h);
        box(shaft_z - 0.01, W, flare_z - shaft_z + 0.02);
        frustum(flare_z, W, B, par_z - flare_z);
        box(par_z, B, H - par_z);
        band(12);
        band(38);
    }
    box(walk_z, B - 2 * wall, H);                                   // walkway
    for (a = [0 : 90 : 270], o = [-3, 3])                            // crenels
        rotate([0, 0, a]) translate([B / 2 - wall - 1, o - 1.5, cren_z]) cube([wall + 2, 3, 10]);
    recess(270, base_h, W / 2 - 1.2) arch2d(4, 8);                  // door
    for (a = [0 : 90 : 270]) recess(a, 18, W / 2 - 1) arch2d(2, 7);    // windows
    for (a = [0 : 90 : 270]) recess(a, 46, W / 2 - 1) arch2d(2.4, 9);
}
