// Castle tower for FDM printing
// 100 mm tall, 32 mm footprint. Prints upright, no supports.

$fn = 120;

// ---- dimensions (mm) ----
H         = 100;    // total height
base_r    = 16;     // plinth radius (footprint 32 mm)
plinth_h  = 2.5;
talus_r   = 14.5;   // radius after the plinth chamfer
talus_z   = 4;
shaft_r0  = 12.5;   // shaft radius at the bottom
shaft_z0  = 10;
shaft_r1  = 11.75;  // shaft radius at the top
shaft_z1  = 70;     // corbel flare starts here
par_r     = 15;     // parapet outer radius
par_wall  = 2.4;    // parapet wall thickness
walk_z    = 78;     // walkway level
crenel_z  = 81.5;   // bottom of the crenels
merlon_z  = 85;     // top of the merlons
merlons   = 10;
crenel_w  = 3.5;

turret_r  = 5.5;
eave_z    = 87;     // top of the turret wall
roof_r    = 7;
roof_z    = 89;     // base of the roof cone
tip_r     = 0.8;

flare_z   = shaft_z1 + (par_r - shaft_r1);   // top of the 45° flare

function shaft_r(z) = shaft_r0 + (shaft_r1 - shaft_r0) * (z - shaft_z0) / (shaft_z1 - shaft_z0);

module body() {
    rotate_extrude()
        polygon([
            [0, 0],
            [base_r - 0.6, 0],          // bottom chamfer (elephant foot)
            [base_r, 0.6],
            [base_r, plinth_h],
            [talus_r, talus_z],         // 45° plinth chamfer
            [shaft_r0, shaft_z0],       // battered base
            [shaft_r1, shaft_z1],       // tapered shaft
            [par_r, flare_z],           // 45° corbel flare
            [par_r, merlon_z],
            [par_r - par_wall, merlon_z],
            [par_r - par_wall, walk_z],
            [0, walk_z]
        ]);
}

// raised stone band, 45° underside
module band(z0, p = 0.8) {
    r = shaft_r(z0 + 1.2);
    rotate_extrude()
        polygon([
            [r - 1, z0],
            [r, z0],
            [r + p, z0 + p],
            [r + p, z0 + p + 0.8],
            [r, z0 + 2 * p + 0.8],
            [r - 1, z0 + 2 * p + 0.8]
        ]);
}

// corbel brackets under the parapet
module corbels(n = 20, w = 1.4, drop = 4) {
    z0 = shaft_z1 - drop;
    intersection() {
        rotate_extrude()
            polygon([
                [0, z0],
                [shaft_r(z0), z0],
                [par_r, z0 + (par_r - shaft_r(z0))],
                [par_r, flare_z + 0.01],
                [0, flare_z + 0.01]
            ]);
        for (k = [0 : n - 1])
            rotate([0, 0, 360 / n * k])
                translate([0, -w / 2, z0 - 1])
                    cube([par_r + 1, w, flare_z - z0 + 2]);
    }
}

module turret() {
    rotate_extrude()
        polygon([
            [0, walk_z - 1],
            [turret_r, walk_z - 1],
            [turret_r, eave_z],
            [roof_r, eave_z + (roof_r - turret_r)],   // 45° eave
            [roof_r, roof_z],
            [tip_r, H],
            [0, H]
        ]);
}

module crenels() {
    for (k = [0 : merlons - 1])
        rotate([0, 0, 360 / merlons * (k + 0.5)])
            translate([par_r - par_wall - 1, -crenel_w / 2, crenel_z])
                cube([par_wall + 2, crenel_w, 10]);
}

// pointed arch opening, w wide, h tall, base at y = 0
module arch2d(w, h) {
    s = h - w * sqrt(3) / 2;
    translate([-w / 2, 0]) square([w, s + 0.01]);
    translate([0, s])
        intersection() {
            translate([-w / 2, 0]) circle(r = w, $fn = 64);
            translate([ w / 2, 0]) circle(r = w, $fn = 64);
            translate([-w / 2, 0]) square([w, w]);
        }
}

// cross-shaped arrow slit
module crosslet2d(w = 1.6, h = 10, bar = 4.4) {
    translate([-w / 2, 0]) square([w, h]);
    translate([-bar / 2, h * 0.55 - w / 2]) square([bar, w]);
}

// cut the 2D child outline into the wall: facing `angle`, base at height z,
// recess floor at radius floor_r, cutting outward by len
module recess(angle, z, floor_r, len = 5) {
    rotate([0, 0, angle])
        translate([floor_r, 0, z])
            rotate([90, 0, 90])
                linear_extrude(height = len) children();
}

difference() {
    union() {
        body();
        band(shaft_z0);   // base course
        band(31);
        band(52);
        corbels();
        turret();
    }
    crenels();
    // door (front)
    recess(270, plinth_h, 11.0, 6) arch2d(5, 10.8);
    // arrow slits
    for (a = [45, 135, 225, 315]) recess(a, 15, shaft_r(20) - 1.2) crosslet2d();
    // windows
    for (a = [0, 90, 180, 270]) recess(a, 36, shaft_r(40) - 1.2) arch2d(2.8, 9);
    for (a = [45, 135, 225, 315]) recess(a, 57, shaft_r(61) - 1.2) arch2d(2.8, 9);
    // turret door
    recess(270, walk_z, turret_r - 0.8, 1.5) arch2d(2.4, 5);
}
