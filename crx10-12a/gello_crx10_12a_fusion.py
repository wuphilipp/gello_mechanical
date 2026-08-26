"""GELLO leader arm for the FANUC CRX-10/12A -- parametric model.

Run this inside Autodesk Fusion (Utilities > Add-Ins > Scripts). It builds the
five moving parts and writes L1.STL .. L5.STL next to this file. base.STL is
the unmodified UR5 GELLO base plate and is simply copied from ../ur5.

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
* Joint topology follows the real CRX-10/12A, a conventional 6R arm in which
  J4 is a roll about the forearm. The UR5 has a pitch there instead, so the
  wrist (L3..L5) is new geometry rather than a rescaled UR5 wrist.
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

# Real FANUC CRX-10/12A link lengths [mm], read off 2D_CRX10-12A_v01.dxf.
CRX_D1 = 245.0  # base mounting face -> J2 axis
CRX_A2 = 540.0  # J2 -> J3 (upper arm)
CRX_A3 = 540.0  # J3 -> J5 wrist centre (forearm)
CRX_D6 = 160.0  # J5 -> J6 faceplate

D1 = CRX_D1 * ALPHA
A2 = CRX_A2 * ALPHA
A3 = CRX_A3 * ALPHA
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

# Derived joint frames (see the module docstring for the axis convention).
Y_ARM = D1            # 122.5, height of the J2/J3/J5 axes
X1 = 25.0             # +X face of the L1 column, seats the J2 motor
X2H = X1 + DFH        # 51.0,  J2 horn face, faces +X
X3H = X2H - DFH       # 25.0,  J3 horn face, faces -X
Z3 = A2               # 270.0, J3 axis
Z5 = A2 + A3          # 540.0, wrist centre (J5 axis)
# Distance from the J4 horn face back to the wrist centre. Hardware driven --
# the L4 yoke has to bridge the J5 motor body (DBOT behind its axis) plus a
# plate -- so it must NOT scale with ALPHA.
J4_TO_WRIST = 60.0
Z4H = Z5 - J4_TO_WRIST  # 480.0, J4 horn face, faces +Z
X4 = 15.0             # +X plate of the L4 yoke, seats the J5 motor
X5H = X4 - DFH        # -11.0, J5 horn face, faces -X
Z6H = Z5 + D6         # 620.0, J6 horn face / faceplate, faces +Z

YLO, YHI = Y_ARM - R, Y_ARM + R  # 108.0 .. 137.0

# The forearm and the wrist need room for a motor plus a plate at each end.
assert A3 > J4_TO_WRIST + DFH + T, 'ALPHA too small: the forearm is shorter than its two motors'
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
J6 = ((0.0, Y_ARM, Z6H), (0, 0, 1), (1, 0, 0))


# --------------------------------------------------------------------------
# The five printed links
# --------------------------------------------------------------------------

def part_l1():
    """J1 horn -> J2 motor. A sole plate on the J1 horn plus a T-section
    column that lifts the J2 axis to D1 above the base plate."""
    sole = fuse(
        box(0.0, X1, J1_HORN_Y, J1_HORN_Y + T, -R, R),
        cyl((0, J1_HORN_Y, 0), (0, J1_HORN_Y + T, 0), R))
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
    """J3 horn -> J4 motor. Forearm; carries the roll motor whose axis is the
    forearm axis itself. This is where the CRX differs from the UR5."""
    arm = fuse(
        box(X3H - T, X3H, YLO, YHI, Z3, Z4H - DFH),
        cyl((X3H - T, Y_ARM, Z3), (X3H, Y_ARM, Z3), R))
    cross = box(-R, X3H + 1.0, YLO, YHI, Z4H - DFH - T, Z4H - DFH)
    return cut(fuse(arm, cross), dynamixel(*J3), dynamixel(*J4))


def part_l4():
    """J4 horn -> J5 motor. Wrist yoke, sets the wrist centre at Z5."""
    disc = fuse(
        box(0.0, X4 + T, YLO, YHI, Z4H, Z4H + T),
        cyl((0, Y_ARM, Z4H), (0, Y_ARM, Z4H + T), R))
    arm = fuse(
        box(X4, X4 + T, YLO, YHI, Z4H, Z5),
        cyl((X4, Y_ARM, Z5), (X4 + T, Y_ARM, Z5), R))
    return cut(fuse(disc, arm), dynamixel(*J4), dynamixel(*J5))


def part_l5():
    """J5 horn -> J6 motor. The J6 horn is the faceplate that the shared
    gripper handle (../gripper/handle.STL) bolts onto."""
    plate = fuse(
        box(X5H - T, X5H, YLO, YHI, Z5, Z6H - DFH),
        cyl((X5H - T, Y_ARM, Z5), (X5H, Y_ARM, Z5), R))
    # the flange has to cover the four J6 mounting screws, which sit at
    # X = DTOP - 2 and X = -(DBOT - 2); 1.5 mm of material beyond the
    # motor body keeps the flange edge off the pocket wall.
    cross = box(-(DBOT + 1.5), DTOP + 1.5, YLO, YHI, Z6H - DFH - T, Z6H - DFH)
    return cut(fuse(plate, cross), dynamixel(*J5), dynamixel(*J6))


PARTS = [("L1", part_l1), ("L2", part_l2), ("L3", part_l3),
         ("L4", part_l4), ("L5", part_l5)]


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
