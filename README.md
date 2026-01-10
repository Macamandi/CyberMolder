# CyberMolder v1.0

**A Retro Voxel Engine for Linux & Windows written in Python.**
Developed by **Samuel Sales Gomes**.

![CyberMolder Icon](Icone.png)

## 🎮 About
**CyberMolder** is a lightweight and powerful tool designed for creating Voxel art (3D pixel art). It focuses on a fast workflow, retro-futuristic aesthetics, and automation tools like "Magic Sculpt".

## ✨ Features
- **Voxel Modeling:** Pencil, Paint Bucket, Eraser, and Color Picker tools.
- **Magic Sculpt:** Automatically generate 3D models from two 2D images (Front/Side intersection).
- **Export:** Generates optimized `.OBJ` files with texture atlases, ready for Game Engines (Godot, Unity, Unreal).
- **Turntable:** Built-in GIF recorder that automatically spins the model.
- **Safe Interface:** Dedicated Launcher and input safety features (prevents accidental painting while scrolling).

## 🎹 Controls & Shortcuts

| Key | Function |
| :--- | :--- |
| **B** | Pencil (Brush) |
| **G** | Paint Bucket (Gradient/Fill) |
| **E** | Eraser |
| **I** | Color Picker |
| **M** | Mirror X Axis (Symmetry) |
| **K** | Set Pivot Point |
| **.** / **,** | Move Slice Up/Down |
| **1, 2, 3** | Change Editing Axis (X, Y, Z) |
| **V + Arrows** | Move the entire Model |
| **R** | Auto-Rotate Camera |
| **Ctrl + S** | Save Project (.json) |
| **S** | Export Object (.obj) |

## 🛠️ How to run from source
If you prefer running the Python script instead of the standalone executable:

```bash
# 1. Install dependencies
pip install pygame pillow

# 2. Run the engine
python CyberMolder.py
