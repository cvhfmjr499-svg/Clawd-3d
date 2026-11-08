#!/usr/bin/env python3
"""Erzeugt ein Voxel-3D-Modell von Clawd und exportiert es als OBJ (+MTL) und STL.

Aufruf:  python3 clawd.py      -> schreibt models/clawd.obj, models/clawd.mtl, models/clawd.stl
Eine Einheit = 1 Voxel. Mit SCALE lässt sich die Größe (z.B. in mm für den 3D-Druck) anpassen.
"""
import os
import struct

SCALE = 5.0  # 1 Voxel = 5 mm  -> Clawd ist ca. 60 x 35 x 30 mm

BODY, EYE = "clawd_orange", "clawd_eye"


def build_voxels():
    v = {}

    def box(x0, x1, y0, y1, z0, z1, mat):
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    v[(x, y, z)] = mat

    box(1, 11, 2, 7, 0, 6, BODY)            # Körper
    box(0, 1, 3, 5, 2, 4, BODY)             # linker Arm
    box(11, 12, 3, 5, 2, 4, BODY)           # rechter Arm
    for lx in (2, 4, 7, 9):                 # vier Beinchen
        box(lx, lx + 1, 0, 2, 1, 5, BODY)
    box(3, 4, 4, 6, 0, 1, EYE)              # linkes Auge (vorne, z=0)
    box(8, 9, 4, 6, 0, 1, EYE)              # rechtes Auge
    return v


# Würfelseiten: Normale, 4 Ecken (gegen den Uhrzeigersinn von außen gesehen)
FACES = [
    ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((-1, 0, 0), [(0, 0, 1), (0, 1, 1), (0, 1, 0), (0, 0, 0)]),
    ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
    ((0, -1, 0), [(0, 0, 1), (0, 0, 0), (1, 0, 0), (1, 0, 1)]),
    ((0, 0, 1), [(1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 1)]),
    ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
]


def surface(voxels):
    """Nur Außenflächen (Nachbar leer). Vorderseite ist -z, wir drehen auf +z für die Ausgabe."""
    quads = []
    for (x, y, z), mat in voxels.items():
        for n, corners in FACES:
            if (x + n[0], y + n[1], z + n[2]) in voxels:
                continue
            pts = [((x + c[0] - 6) * SCALE, (y + c[1]) * SCALE, -(z + c[2] - 3) * SCALE) for c in corners]
            # z wurde gespiegelt -> Umlaufsinn umdrehen, damit Normalen nach außen zeigen
            quads.append((mat, (n[0], n[1], -n[2]), pts[::-1]))
    return quads


def write_obj(quads, path):
    with open(path.replace(".obj", ".mtl"), "w") as f:
        f.write("newmtl %s\nKd 0.851 0.467 0.341\nKa 0 0 0\nKs 0.05 0.05 0.05\n\n" % BODY)
        f.write("newmtl %s\nKd 0.08 0.06 0.05\nKa 0 0 0\nKs 0.2 0.2 0.2\n" % EYE)
    idx, verts, lines = {}, [], []
    for mat in (BODY, EYE):
        lines.append("usemtl %s" % mat)
        for m, _, pts in quads:
            if m != mat:
                continue
            ids = []
            for p in pts:
                if p not in idx:
                    idx[p] = len(verts) + 1
                    verts.append(p)
                ids.append(idx[p])
            lines.append("f " + " ".join(map(str, ids)))
    with open(path, "w") as f:
        f.write("# Clawd voxel model\nmtllib %s\no Clawd\n" % os.path.basename(path).replace(".obj", ".mtl"))
        f.writelines("v %g %g %g\n" % p for p in verts)
        f.write("\n".join(lines) + "\n")


def write_stl(quads, path):
    with open(path, "wb") as f:
        f.write(b"Clawd voxel model".ljust(80, b" "))
        f.write(struct.pack("<I", len(quads) * 2))
        for _, n, (a, b, c, d) in quads:
            for tri in ((a, b, c), (a, c, d)):
                # STL: Z nach oben -> (x, y, z) -> (x, z, y), Umlauf bleibt durch Spiegelung erhalten
                conv = [(p[0], -p[2], p[1]) for p in tri]
                f.write(struct.pack("<3f", n[0], -n[2], n[1]))
                for p in conv:
                    f.write(struct.pack("<3f", *p))
                f.write(b"\0\0")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "models")
    os.makedirs(out, exist_ok=True)
    q = surface(build_voxels())
    write_obj(q, os.path.join(out, "clawd.obj"))
    write_stl(q, os.path.join(out, "clawd.stl"))
    print("%d Flächen geschrieben nach %s" % (len(q), out))
