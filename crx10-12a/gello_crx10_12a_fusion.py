"""GELLO leader arm for the FANUC CRX-10/12A -- parametric model.

Run this inside Autodesk Fusion (Utilities > Add-Ins > Scripts). It builds the
five moving links plus the J1 support ring and writes L1.STL .. L5.STL and
ring.STL next to this file. base.STL is the unmodified UR5 GELLO base plate
and is simply copied from ../ur5.

Design notes
------------
* Link lengths are the real CRX-10/12A link lengths multiplied by ALPHA.
  Everything that touches hardware (DYNAMIXEL body, horn, screw pattern, plate
  thickness) stays 1:1. This is the same convention used by the UR5 GELLO in
  this repository (its links are exactly 0.5x the real UR5) and by
  ../ar4/gello-ar4.scad (scale_factor).
* The DYNAMIXEL interface is a direct port of dynamixel() in
  ../ar4/gello-ar4.scad. It was verified against ../ur5/base.STL and
  ../ur5/L1.STL: horn face at Y=23, four M2 holes on a 6 mm radius with 4 mm
  counterbores, motor body spanning Z=-9.5..24.5 in the base pocket.
* Joint topology and link lengths follow FANUC's own URDF, crx10ia_urdf_macro
  .xacro in https://github.com/FANUC-CORPORATION/fanuc_description. It is a
  conventional 6R arm in which J4 is a roll about the forearm, J4 is
  coincident with J3, and J6 is offset from J5 along the J5 axis. The UR5 has
  a pitch at J4 and no such offset, so L3..L5 are new geometry rather than
  rescaled UR5 wrist parts.
* Assembly coordinate frame matches the UR5 GELLO STLs:
  Y = up (J1 axis), Z = arm reach direction, X = pitch-axis direction.
  Origin = J1 axis on the top face of the base plate. Home pose = arm
  stretched horizontally along +Z.
"""

import math
import os

import adsk.core
import adsk.fusion

# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------

ALPHA = 0.5  # link-length coefficient

# Real FANUC CRX-10/12A link lengths [mm]. These are the l_* xacro properties
# of FANUC's own crx10ia_urdf_macro.xacro:
#   https://github.com/FANUC-CORPORATION/fanuc_description
#     fanuc_crx_description/urdf/crx10ia_urdf_macro.xacro
# l_1 = l_3 = 0, i.e. J2 sits on the J1 axis and J4 is COINCIDENT with J3.
# The 540 mm forearm is therefore the J4->J5 link: the whole forearm rolls.
CRX_D1 = 245.0  # l_base, base mounting face -> J1 = J2 axis
CRX_A2 = 540.0  # l_2,    J2 -> J3 (upper arm)
CRX_A3 = 540.0  # l_4,    J4 -> J5 (forearm); J4 is coincident with J3
CRX_D5 = 150.0  # l_5,    J5 -> J6, measured ALONG the J5 axis
CRX_D6 = 160.0  # l_6,    J6 -> flange, along the forearm direction

D1 = CRX_D1 * ALPHA
A2 = CRX_A2 * ALPHA
A3 = CRX_A3 * ALPHA
D5 = CRX_D5 * ALPHA
D6 = CRX_D6 * ALPHA

# Hardware -- never scaled.
T = 8.0    # plate thickness
R = 14.5   # link half width (the UR5 GELLO uses 29 mm wide links)

DW, DL, DH = 20.0, 34.0, 23.0   # DYNAMIXEL XL330 body
DHORN = 3.0                     # horn height above the body
DFH = DH + DHORN                # 26.0, horn face to mounting face
DTOP = 16.0 / 2 + 1.5           # 9.5, horn axis -> near end of the body
DBOT = DL - DTOP                # 24.5, horn axis -> far end of the body
HORN_R = 8.0
TAP_R = 2.35 / 2
CB_R = 4.0 / 2

J1_HORN_Y = 23.0  # fixed by the reused ur5/base.STL

# J1 support ring. The J1 horn is the only place in the arm where the whole
# overturning moment has to be reacted -- no joint axis relieves it -- so the
# ring takes that moment on a large-radius thrust land and leaves the horn
# transmitting only J1 torque. It bolts to the four M2 holes the UR5 base
# plate already has on a 36 mm radius at 0/90/180/270 deg. Hardware driven,
# so none of this scales with ALPHA.
RING_BORE_R = 28.0   # clears the J1 motor body (corner radius 26.5)
RING_OUT_R = 33.0    # thrust land is the annulus 28..33, mean radius 30.5
RING_PAD_R = 39.0    # bolt pads reach past the 36 mm bolt circle
RING_BOLT_R = 36.0
RING_PAD_H = 5.0     # bolt pad thickness
RING_LAND_H = 5.0    # height of the continuous rim carrying the land
RING_LEG_HW = 12.0   # half width of the four legs; cables leave between them
SKIRT_R = RING_OUT_R  # L1 sole plate is enlarged to this radius to reach it

# Derived joint frames (see the module docstring for the axis convention).
Y_ARM = D1            # 122.5, height of the J2/J3/J5 axes
X1 = 25.0             # +X face of the L1 column, seats the J2 motor
X2H = X1 + DFH        # 51.0,  J2 horn face, faces +X
X3H = X2H - DFH       # 25.0,  J3 horn face, faces -X
Z3 = A2               # 270.0, J3 axis -- and J4 axis, they are coincident
Z5 = A2 + A3          # 540.0, J5 axis, on the forearm axis
# The J4 axis runs along the forearm through (X=0, Y=Y_ARM), so the J4 motor
# can sit anywhere along it. Park it just clear of the J3 motor and of the L3
# mounting disc. Hardware driven, so it must NOT scale with ALPHA.
J3_TO_J4H = 44.0
Z4H = Z3 + J3_TO_J4H  # 314.0, J4 horn face, faces +Z
X4 = 15.0             # +X plate of the L4 forearm, seats the J5 motor
X5H = X4 - DFH        # -11.0, J5 horn face, faces -X
# J6 is offset from J5 by D5 along the J5 axis. With Y up and the arm along +Z
# the J5 axis direction that matches FANUC's -y is -X, so the J6 roll axis is
# a line parallel to the forearm, displaced D5 in -X. This is what makes the
# CRX wrist non-spherical, and it is what turns 1080 + 160 into a 1249 reach:
# sqrt(1240^2 + 150^2) = 1249.
X6 = -D5              # -75.0, X of the J6 roll axis
Z6H = Z5 + D6         # 620.0, J6 horn face / faceplate, faces +Z

YLO, YHI = Y_ARM - R, Y_ARM + R  # 108.0 .. 137.0

# The forearm and the wrist need room for a motor plus a plate at each end.
assert A3 > J3_TO_J4H + DFH + T, 'ALPHA too small: the forearm is shorter than its two motors'
assert D5 > DFH, 'ALPHA too small: the J6 motor would sit on top of the J5 motor'
assert D6 > DFH + T, 'ALPHA too small: no room between the J5 and J6 motors'
assert D1 > J1_HORN_Y + T, 'ALPHA too small: J2 would sit inside the base plate'

MM = 0.1  # Fusion works in cm


# --------------------------------------------------------------------------
# Temporary B-Rep helpers (mm in, cm out)
# --------------------------------------------------------------------------

def _tbm():
    return adsk.fusion.TemporaryBRepManager.get()


def _pt(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def _vec(x, y, z):
    return adsk.core.Vector3D.create(x, y, z)


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two opposite corners, in mm."""
    centre = _pt((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    obb = adsk.core.OrientedBoundingBox3D.create(
        centre, _vec(1, 0, 0), _vec(0, 1, 0),
        abs(x1 - x0) * MM, abs(y1 - y0) * MM, abs(z1 - z0) * MM)
    return _tbm().createBox(obb)


def cyl(p0, p1, r):
    """Cylinder between two mm points given as (x, y, z) tuples."""
    return _tbm().createCylinderOrCone(_pt(*p0), r * MM, _pt(*p1), r * MM)


def fuse(*bodies):
    out = _tbm().copy(bodies[0])
    for b in bodies[1:]:
        _tbm().booleanOperation(out, _tbm().copy(b),
                                adsk.fusion.BooleanTypes.UnionBooleanType)
    return out


def intersect(target, tool):
    out = _tbm().copy(target)
    _tbm().booleanOperation(out, _tbm().copy(tool),
                            adsk.fusion.BooleanTypes.IntersectionBooleanType)
    return out


def annulus(r_in, r_out, y0, y1):
    outer = cyl((0, y0, 0), (0, y1, 0), r_out)
    bore = cyl((0, y0 - 1.0, 0), (0, y1 + 1.0, 0), r_in)
    return cut(outer, bore)


def cut(target, *tools):
    out = _tbm().copy(target)
    for b in tools:
        _tbm().booleanOperation(out, _tbm().copy(b),
                                adsk.fusion.BooleanTypes.DifferenceBooleanType)
    return out


# --------------------------------------------------------------------------
# DYNAMIXEL cut tool -- a direct port of dynamixel() in ar4/gello-ar4.scad
# --------------------------------------------------------------------------

def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return (v[0] / n, v[1] / n, v[2] / n)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


class Frame(object):
    """Local motor frame: +z is the horn axis pointing at the mating part, the
    origin sits on the horn face and +y runs along the 34 mm body length."""

    def __init__(self, origin, z_dir, y_dir):
        self.o = origin
        self.z = _norm(z_dir)
        self.y = _norm(y_dir)
        self.x = _cross(self.y, self.z)  # right handed: x = y cross z

    def p(self, lx, ly, lz):
        return (self.o[0] + self.x[0] * lx + self.y[0] * ly + self.z[0] * lz,
                self.o[1] + self.x[1] * lx + self.y[1] * ly + self.z[1] * lz,
                self.o[2] + self.x[2] * lx + self.y[2] * ly + self.z[2] * lz)


def _lbox(f, x0, x1, y0, y1, z0, z1):
    """Box given in the local motor frame. Every frame used here is aligned
    with the world axes, so an axis-aligned world box is exact."""
    corners = [f.p(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    zs = [c[2] for c in corners]
    return box(min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def dynamixel(origin, z_dir, y_dir):
    """Everything that has to be removed for one XL330: body pocket, horn
    clearance, four horn screws, four mounting screws and the cable relief."""
    f = Frame(origin, z_dir, y_dir)
    parts = []

    # body pocket + horn boss clearance
    parts.append(_lbox(f, -DW / 2, DW / 2, -DBOT, DTOP, -DFH, -DHORN))
    parts.append(cyl(f.p(0, 0, -25.0), f.p(0, 0, 0.0), HORN_R))

    # four horn screws, into the part that rides on the horn
    for lx, ly in ((6, 0), (-6, 0), (0, 6), (0, -6)):
        parts.append(cyl(f.p(lx, ly, -0.5), f.p(lx, ly, 10.5), TAP_R))
        parts.append(cyl(f.p(lx, ly, 3.1), f.p(lx, ly, 13.1), CB_R))

    # four mounting screws, into the part that carries the motor
    for lx, ly in ((8, DTOP - 2), (-8, DTOP - 2),
                   (8, -(DBOT - 2)), (-8, -(DBOT - 2))):
        parts.append(cyl(f.p(lx, ly, -25.5), f.p(lx, ly, -36.5), TAP_R))
        parts.append(cyl(f.p(lx, ly, -27.5), f.p(lx, ly, -37.5), CB_R))

    # cable relief
    for lx in (7.5, -7.5):
        parts.append(_lbox(f, lx - 2.5, lx + 2.5, -14.5, -4.5, -36.0, -26.0))

    return fuse(*parts)


# (horn face origin, horn axis pointing at the mating part, body length axis)
J1 = ((0.0, J1_HORN_Y, 0.0), (0, 1, 0), (0, 0, -1))
J2 = ((X2H, Y_ARM, 0.0), (1, 0, 0), (0, 1, 0))
J3 = ((X3H, Y_ARM, Z3), (-1, 0, 0), (0, 0, 1))
J4 = ((0.0, Y_ARM, Z4H), (0, 0, 1), (-1, 0, 0))
J5 = ((X5H, Y_ARM, Z5), (-1, 0, 0), (0, 0, 1))
J6 = ((X6, Y_ARM, Z6H), (0, 0, 1), (-1, 0, 0))


# --------------------------------------------------------------------------
# The five printed links
# --------------------------------------------------------------------------

def part_l1():
    """J1 horn -> J2 motor. A sole plate on the J1 horn plus a T-section
    column that lifts the J2 axis to D1 above the base plate."""
    # the sole plate is a full SKIRT_R disc so that it lands on the support
    # ring instead of hanging off the J1 horn alone
    sole = fuse(
        box(0.0, X1, J1_HORN_Y, J1_HORN_Y + T, -R, R),
        cyl((0, J1_HORN_Y, 0), (0, J1_HORN_Y + T, 0), SKIRT_R))
    column = box(X1 - T, X1, J1_HORN_Y, YHI, -R, R)
    rib = box(0.0, X1, J1_HORN_Y, YHI, -T / 2, T / 2)
    return cut(fuse(sole, column, rib), dynamixel(*J1), dynamixel(*J2))


def part_l2():
    """J2 horn -> J3 motor. Upper arm, axis-to-axis length A2."""
    plate = fuse(
        box(X2H, X2H + T, YLO, YHI, 0.0, Z3),
        cyl((X2H, Y_ARM, 0.0), (X2H + T, Y_ARM, 0.0), R),
        cyl((X2H, Y_ARM, Z3), (X2H + T, Y_ARM, Z3), R))
    return cut(plate, dynamixel(*J2), dynamixel(*J3))


def part_l3():
    """J3 horn -> J4 motor. A short bracket: J4 is coincident with J3 on the
    real robot, so this link carries the forearm roll motor right at the elbow
    and it is the following link that is long. This is where the CRX differs
    from the UR5."""
    arm = fuse(
        box(X3H - T, X3H, YLO, YHI, Z3, Z4H - DFH),
        cyl((X3H - T, Y_ARM, Z3), (X3H, Y_ARM, Z3), R))
    cross = box(-R, X3H + 1.0, YLO, YHI, Z4H - DFH - T, Z4H - DFH)
    return cut(fuse(arm, cross), dynamixel(*J3), dynamixel(*J4))


def part_l4():
    """J4 horn -> J5 motor. The forearm: the whole A3 long link rolls with J4,
    exactly as on the real arm."""
    disc = fuse(
        box(0.0, X4 + T, YLO, YHI, Z4H, Z4H + T),
        cyl((0, Y_ARM, Z4H), (0, Y_ARM, Z4H + T), R))
    arm = fuse(
        box(X4, X4 + T, YLO, YHI, Z4H, Z5),
        cyl((X4, Y_ARM, Z5), (X4 + T, Y_ARM, Z5), R))
    return cut(fuse(disc, arm), dynamixel(*J4), dynamixel(*J5))


def part_l5():
    """J5 horn -> J6 motor. Carries the J6 roll axis out to X6, which is the
    D5 wrist offset that makes the CRX wrist non-spherical. The J6 horn is the
    faceplate the shared gripper (../gripper/handle.STL) bolts onto."""
    plate = fuse(
        box(X5H - T, X5H, YLO, YHI, Z5, Z6H - DFH),
        cyl((X5H - T, Y_ARM, Z5), (X5H, Y_ARM, Z5), R))
    # the flange reaches from the J5 horn out past the J6 motor body; 1.5 mm of
    # material beyond the body keeps the flange edge off the pocket wall.
    cross = box(X6 - DTOP - 1.5, X5H, YLO, YHI, Z6H - DFH - T, Z6H - DFH)
    return cut(fuse(plate, cross), dynamixel(*J5), dynamixel(*J6))


def part_ring():
    """J1 support ring. Bolts to the base plate and presents a flat thrust land
    at exactly the height of the J1 horn face, so the L1 skirt rests on it."""
    legs = fuse(
        box(RING_BORE_R - 9, RING_PAD_R + 1, -1.0, J1_HORN_Y + 1, -RING_LEG_HW, RING_LEG_HW),
        box(-(RING_PAD_R + 1), -(RING_BORE_R - 9), -1.0, J1_HORN_Y + 1, -RING_LEG_HW, RING_LEG_HW),
        box(-RING_LEG_HW, RING_LEG_HW, -1.0, J1_HORN_Y + 1, RING_BORE_R - 9, RING_PAD_R + 1),
        box(-RING_LEG_HW, RING_LEG_HW, -1.0, J1_HORN_Y + 1, -(RING_PAD_R + 1), -(RING_BORE_R - 9)))

    land = annulus(RING_BORE_R, RING_OUT_R, J1_HORN_Y - RING_LAND_H, J1_HORN_Y)
    shaft = intersect(annulus(RING_BORE_R, RING_OUT_R, 0.0, J1_HORN_Y - RING_LAND_H), legs)
    pads = intersect(annulus(RING_BORE_R, RING_PAD_R, 0.0, RING_PAD_H), legs)
    body = fuse(land, shaft, pads)

    holes = []
    for x, z in ((RING_BOLT_R, 0), (-RING_BOLT_R, 0), (0, RING_BOLT_R), (0, -RING_BOLT_R)):
        holes.append(cyl((x, -1.0, z), (x, RING_PAD_H + 1.0, z), 2.4 / 2))
        holes.append(cyl((x, 2.5, z), (x, RING_PAD_H + 1.0, z), 4.4 / 2))
    return cut(body, *holes)


PARTS = [("L1", part_l1), ("L2", part_l2), ("L3", part_l3),
         ("L4", part_l4), ("L5", part_l5), ("ring", part_ring)]


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def build(out_dir=None):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(
        doc.products.itemByProductType("DesignProductType"))
    design.designType = adsk.fusion.DesignTypes.DirectDesignType
    design.unitsManager.distanceDisplayUnits = \
        adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = design.rootComponent

    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(__file__))

    made = []
    for name, fn in PARTS:
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        body = occ.component.bRepBodies.add(fn())
        body.name = name
        made.append((name, occ.component))

    em = design.exportManager
    for name, comp in made:
        path = os.path.join(out_dir, name + ".STL")
        opts = em.createSTLExportOptions(comp, path)
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        opts.isBinaryFormat = True
        em.execute(opts)
        print("wrote " + path)
    return design


def run(_context: str):
    build()
