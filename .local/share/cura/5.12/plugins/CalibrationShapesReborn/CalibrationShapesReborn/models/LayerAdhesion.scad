// layer adhesion

$fn=120;

translate([0, 0, 0]) union() {
    translate([0, 0, -0.75]) difference() {
        minkowski()
        {
          cylinder(4,8,8,center = false);
          sphere(r=1);
        }
        translate([0, 0, -3]) cylinder(4,10,10,center = false);
    }
  cylinder(0.25,8.5,9,center = false);
  translate([0, 0, 4]) cylinder(18,3,3,center = false);
}
