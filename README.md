# Clawd 3D

Ein Voxel-3D-Modell von Clawd.

- `models/clawd.obj` + `clawd.mtl` – mit Farben (Orange + schwarze Augen), für Blender, Windows 3D-Viewer usw.
- `models/clawd.stl` – wasserdicht, steht auf der Bodenplatte, direkt druckbar (60 × 35 × 30 mm)
- `viewer.html` – interaktiver Viewer im Browser (Three.js)
- `clawd.py` – Generator; Form oder Maßstab (`SCALE`, mm pro Voxel) anpassen und neu bauen:

```bash
python3 clawd.py
```
