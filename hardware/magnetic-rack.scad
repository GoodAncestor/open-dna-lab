// Magnetic separation rack for 1.5 mL microcentrifuge tubes
// Good Ancestor open lab
//
// Magnets: N52 neodymium discs, 12 mm dia x 5 mm thick.
// Print: PLA or PETG, 0.2 mm layers, 3 perimeters, 20% infill. No supports.
// Magnets press-fit from the back. Add a drop of superglue if loose.
//
// ALL DIMENSIONS PARAMETRIC — measure your actual magnets and edit.

/* [Tubes] */
tube_d        = 11.2;   // 1.5 mL tube is 10.8 mm OD; 0.4 mm clearance
tube_count    = 6;
tube_pitch    = 20;     // centre-to-centre spacing
bore_depth    = 26;     // how deep the tube sits

/* [Magnets] */
magnet_d      = 12.0;   // disc diameter
magnet_h      = 5.0;    // disc thickness
magnet_fit    = 0.2;    // press-fit clearance; increase if too tight
magnet_z      = 9;      // centre height above base — keep LOW, at the
                        // liquid level in the tube cone

/* [Body] */
wall          = 1.0;    // between magnet pocket and tube bore.
                        // Thinner = stronger pull. Do not go below 0.8.
base          = 3;      // solid floor under the bores
side          = 6;      // material outboard of the magnet pocket
end           = 6;      // material at the ends of the block

$fn = 64;

// ---- derived ----------------------------------------------------------
mag_d   = magnet_d + magnet_fit;
mag_h   = magnet_h + magnet_fit;
// magnet pocket centre, offset from tube centre on -Y
mag_y   = -(tube_d/2 + wall + mag_h/2);

body_x  = tube_pitch * (tube_count - 1) + tube_d + 2*end;
body_y  = tube_d/2 + wall + mag_h + side;
body_z  = base + bore_depth;

function xpos(i) = -body_x/2 + end + tube_d/2 + i*tube_pitch;

// ---- parts ------------------------------------------------------------
module body() {
    translate([-body_x/2, -(tube_d/2 + wall + mag_h + side), 0])
        cube([body_x, body_y + tube_d/2, body_z]);
}

module tube_bore(x) {
    translate([x, 0, base])
        cylinder(d = tube_d, h = bore_depth + 1);
    // chamfer to guide the tube in
    translate([x, 0, body_z - 2])
        cylinder(d1 = tube_d, d2 = tube_d + 3, h = 2.01);
}

// magnet pocket, opening to the back face (-Y) so discs press in
module magnet_pocket(x) {
    translate([x, mag_y, magnet_z])
        rotate([90, 0, 0])
            cylinder(d = mag_d, h = mag_h, center = true);
    // access slot to the back face
    translate([x, mag_y - mag_h/2 - side/2 - 0.5, magnet_z])
        rotate([90, 0, 0])
            cylinder(d = mag_d, h = side + 1, center = true);
}

// finger cutout so you can grab tubes
module finger_relief(x) {
    translate([x, tube_d/2 + wall, body_z - 8])
        rotate([90, 0, 0])
            cylinder(d = 14, h = 20, center = true);
}

difference() {
    body();
    for (i = [0 : tube_count - 1]) {
        tube_bore(xpos(i));
        magnet_pocket(xpos(i));
        finger_relief(xpos(i));
    }
}
