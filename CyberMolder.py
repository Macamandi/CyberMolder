import sys
import copy
import json
import os 
import math
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser 

# Tenta importar bibliotecas externas
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import pygame

# --- SISTEMA DE TRADUÇÃO (I18N) ---
CURRENT_LANG = "EN" 

TRANSLATIONS = {
    "EN": {
        "launcher_title": "CYBER MOLDER v1.0",
        "btn_free": "🖌️ FREE SCULPT",
        "btn_magic": "🪄 AUTO SCULPT (MAGIC)",
        "btn_load": "📂 LOAD PROJECT",
        "contacts": "CONTACT & SOCIALS:",
        "footer": "CyberMolder Engine - 2026",
        "err_pil": "Pillow library not found.\nRun: pip install pillow",
        "err_fatal": "Fatal Error",
        "warn_no_voxels": "No voxels generated. Check image transparency.",
        "msg_saved": "Project Saved.",
        "msg_loaded": "Project Loaded.",
        "msg_exported": "Exported to OBJ.",
        "win_title": "CyberMolder v1.0 - The Voxel Engine",
        "slice": "SLICE",
        "palette": "PALETTE",
        "rec_start": "RECORDING STARTED...",
        "rec_stop": "RECORDING STOPPED.",
        "tip_pencil": "Pencil Tool (B)",
        "tip_bucket": "Bucket Fill (G)",
        "tip_eraser": "Eraser (E)",
        "tip_picker": "Color Picker (I)",
        "tip_mirror": "Mirror X Axis (M)",
        "tip_pivot": "Set Pivot Point (K)",
        "tip_rec": "Record Turntable (R)",
        "tip_clear": "Clear Current Slice",
        "help_title": "KEYBOARD CONTROLS",
        "help_close": "Press [H] to Close",
        "h_file": "FILES",
        "h_tool": "TOOLS",
        "h_nav": "NAVIGATE",
        "h_edit": "EDIT",
        "h_extra": "EXTRA",
        "d_file": "Ctrl+S (Save) | Ctrl+O (Load) | S (Export OBJ)",
        "d_tool": "B (Pencil) | G (Bucket) | E (Eraser) | I (Picker)",
        "d_nav": "Shift+Arrows (Rotate) | Shift+Scroll (Zoom) | R-Click (Pan)",
        "d_edit": "V+Arrows (Move) | . , (Slice) | 1 2 3 (Axis) | M (Mirror)",
        "d_extra": "R (Record/Rotate) | K (Set Pivot)",
        "sel_front": "Select FRONT Image",
        "sel_side": "Select SIDE Image",
        "processing": "Processing Sculpting..."
    },
    "PT": {
        "launcher_title": "CYBER MOLDER v1.0",
        "btn_free": "🖌️ ESCULTURA LIVRE",
        "btn_magic": "🪄 ESCULTURA MÁGICA",
        "btn_load": "📂 CARREGAR PROJETO",
        "contacts": "CONTATO E REDES:",
        "footer": "CyberMolder Engine - 2026",
        "err_pil": "Biblioteca Pillow não encontrada.\nRode: pip install pillow",
        "err_fatal": "Erro Fatal",
        "warn_no_voxels": "Nenhum voxel gerado. Verifique a transparência.",
        "msg_saved": "Projeto Salvo.",
        "msg_loaded": "Projeto Carregado.",
        "msg_exported": "Exportado para OBJ.",
        "win_title": "CyberMolder v1.0 - A Engine Voxel",
        "slice": "FATIA",
        "palette": "PALETA",
        "rec_start": "GRAVAÇÃO INICIADA...",
        "rec_stop": "GRAVAÇÃO PARADA.",
        "tip_pencil": "Lápis (B)",
        "tip_bucket": "Balde de Tinta (G)",
        "tip_eraser": "Borracha (E)",
        "tip_picker": "Conta-Gotas (I)",
        "tip_mirror": "Espelhar X (M)",
        "tip_pivot": "Definir Pivô (K)",
        "tip_rec": "Gravar Giro (R)",
        "tip_clear": "Limpar Fatia Atual",
        "help_title": "COMANDOS E ATALHOS",
        "help_close": "Pressione [H] para Fechar",
        "h_file": "ARQUIVOS",
        "h_tool": "FERRAMENTAS",
        "h_nav": "NAVEGAÇÃO",
        "h_edit": "EDIÇÃO",
        "h_extra": "EXTRAS",
        "d_file": "Ctrl+S (Salvar) | Ctrl+O (Abrir) | S (Exportar OBJ)",
        "d_tool": "B (Lápis) | G (Balde) | E (Borracha) | I (Conta-Gotas)",
        "d_nav": "Shift+Seta (Girar) | Shift+Scroll (Zoom) | Click Direito (Pan)",
        "d_edit": "V+Setas (Mover) | . , (Fatia) | 1 2 3 (Eixo) | M (Espelho)",
        "d_extra": "R (Gravar GIF / Girar) | K (Definir Pivô)",
        "sel_front": "Selecione Imagem de FRENTE",
        "sel_side": "Selecione Imagem de LADO",
        "processing": "Processando Escultura..."
    }
}

def T(key): return TRANSLATIONS[CURRENT_LANG].get(key, key)

# --- CONFIGURAÇÃO GLOBAL ---
INIT_WIDTH = 1280#1200
INIT_HEIGHT = 720#800
GRID_SIZE = 32      
CELL_SIZE = 18      
VOXEL_ISO_SIZE = 18 

# PALETA DB32
DB32 = [
    (0, 0, 0),       (34, 32, 52),    (69, 40, 60),    (102, 57, 49),
    (143, 86, 59),   (223, 113, 38),  (217, 160, 102), (238, 195, 154),
    (251, 242, 54),  (153, 229, 80),  (106, 190, 48),  (55, 148, 110),
    (75, 105, 47),   (82, 75, 36),    (50, 60, 57),    (63, 63, 116),
    (48, 96, 130),   (91, 110, 225),  (99, 155, 255),  (95, 205, 228),
    (203, 219, 252), (255, 255, 255), (155, 173, 183), (132, 126, 135),
    (105, 106, 106), (89, 86, 82),    (118, 66, 138),  (172, 50, 50),
    (217, 87, 99),   (215, 123, 186), (143, 151, 74),  (138, 111, 48)
]

# --- CORES UI ---
COLOR_BG = (20, 20, 30)
COLOR_GRID_BG = (15, 15, 20)
COLOR_GRID_LINE = (40, 40, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_BUTTON = (60, 60, 80)
COLOR_BUTTON_HOVER = (80, 80, 100)
COLOR_BUTTON_SELECTED = (100, 255, 128)
COLOR_BUTTON_REC = (255, 50, 50) 
COLOR_PIPETTE = (255, 200, 0)
COLOR_OVERLAY = (0, 0, 0, 230) 
COLOR_HELP_TITLE = (100, 255, 128)
COLOR_HELP_CAT = (255, 200, 0)

AXIS_X_COLOR = (255, 50, 50)   
AXIS_Y_COLOR = (50, 200, 50)   
AXIS_Z_COLOR = (50, 100, 255)  
COLOR_SLICE_FRAME = (0, 255, 255) 
COLOR_GHOST_CURSOR = (255, 255, 0)
COLOR_PIVOT = (255, 0, 255)

# --- 1. O LAUNCHER (TKINTER) ---
class VoxelLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CyberMolder Launcher")
        self.root.geometry("400x520") # Altura ajustada para caber os links
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        # --- BLOCO DE ÍCONE (TKINTER) ---
        try:
            # Tenta carregar o ícone. Se falhar, segue a vida.
            icon = tk.PhotoImage(file="Icone.png")
            self.root.iconphoto(False, icon)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o ícone do Launcher: {e}")
        
        # Centraliza
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (400/2)
        y = (screen_height/2) - (520/2)
        self.root.geometry('+%d+%d' % (x, y))

        self.result_data = None 
        self.start_app = False  
        self.create_widgets()

    def create_widgets(self):
        for widget in self.root.winfo_children(): widget.destroy()

        # Language Selector
        frame_lang = tk.Frame(self.root, bg="#1e1e1e")
        frame_lang.pack(anchor="ne", padx=10, pady=5)
        tk.Button(frame_lang, text="🇧🇷 PT", bg="#333", fg="white", bd=0, command=lambda: self.set_lang("PT")).pack(side="left", padx=2)
        tk.Button(frame_lang, text="🇺🇸 EN", bg="#333", fg="white", bd=0, command=lambda: self.set_lang("EN")).pack(side="left", padx=2)

        # Título
        lbl_title = tk.Label(self.root, text=T("launcher_title"), font=("Courier", 20, "bold"), bg="#1e1e1e", fg="#00ff88")
        lbl_title.pack(pady=20)

        btn_style = {"font": ("Helvetica", 12, "bold"), "width": 28, "pady": 10, "bd": 0, "cursor": "hand2"}
        
        tk.Button(self.root, text=T("btn_free"), bg="#333", fg="white", **btn_style, command=self.mode_free).pack(pady=5)
        tk.Button(self.root, text=T("btn_magic"), bg="#552288", fg="white", **btn_style, command=self.mode_magic).pack(pady=5)
        tk.Button(self.root, text=T("btn_load"), bg="#225588", fg="white", **btn_style, command=self.mode_load).pack(pady=5)

        # Seção de Contatos (Links Clicáveis)
        frame_contact = tk.Frame(self.root, bg="#1e1e1e")
        frame_contact.pack(pady=20)
        
        tk.Label(frame_contact, text=T("contacts"), font=("Helvetica", 9, "bold"), bg="#1e1e1e", fg="#aaa").pack(pady=(0, 5))

        links = [
            ("📧 samuel.ssg96@gmail.com", "mailto:samuel.ssg96@gmail.com"),
            ("🐙 GitHub: /Macamandi", "https://github.com/Macamandi"),
            ("📺 Youtube: @macamandi0", "https://www.youtube.com/@macamandi0"),
            ("✖️ Twitter/X: @Macamandi_dev", "https://x.com/Macamandi_dev")
        ]

        for text, url in links:
            lbl = tk.Label(frame_contact, text=text, font=("Helvetica", 9), bg="#1e1e1e", fg="#4da6ff", cursor="hand2")
            lbl.pack()
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        tk.Label(self.root, text=T("footer"), bg="#1e1e1e", fg="#555").pack(side="bottom", pady=10)

    def set_lang(self, lang):
        global CURRENT_LANG
        CURRENT_LANG = lang
        self.create_widgets() 

    def run(self):
        self.root.mainloop()
        return self.start_app, self.result_data

    def mode_free(self):
        self.result_data = {} 
        self.start_app = True
        self.root.destroy()

    def mode_load(self):
        filepath = filedialog.askopenfilename(title=T("btn_load"), filetypes=[("Voxel Project", "*.json")])
        if filepath:
            try:
                with open(filepath, 'r') as f: data = json.load(f)
                voxels = {}
                pivot = tuple(data.get("pivot", (GRID_SIZE//2, GRID_SIZE//2, 0)))
                for v in data.get("data", []): 
                    voxels[(v['x'], v['y'], v['z'])] = (v['r'], v['g'], v['b'])
                self.result_data = {"voxels": voxels, "pivot": pivot}
                self.start_app = True
                self.root.destroy()
            except Exception as e:
                messagebox.showerror(T("err_fatal"), f"{e}")

    def mode_magic(self):
        if not HAS_PIL:
            messagebox.showerror(T("err_fatal"), T("err_pil"))
            return

        front_path = filedialog.askopenfilename(title=T("sel_front"), filetypes=[("Imagens", "*.png *.jpg")])
        if not front_path: return

        side_path = filedialog.askopenfilename(title=T("sel_side"), filetypes=[("Imagens", "*.png *.jpg")])
        if not side_path: return

        try:
            img_f = Image.open(front_path).convert("RGBA").resize((GRID_SIZE, GRID_SIZE), Image.Resampling.NEAREST)
            img_s = Image.open(side_path).convert("RGBA").resize((GRID_SIZE, GRID_SIZE), Image.Resampling.NEAREST)
            pix_f = img_f.load()
            pix_s = img_s.load()
            
            voxels = {}
            for z in range(GRID_SIZE): 
                img_y = GRID_SIZE - 1 - z
                for x in range(GRID_SIZE): 
                    pf = pix_f[x, img_y]
                    if pf[3] < 50: continue 
                    for y in range(GRID_SIZE): 
                        ps = pix_s[y, img_y] 
                        if ps[3] < 50: continue 
                        voxels[(x, y, z)] = (pf[0], pf[1], pf[2])
            
            if not voxels:
                messagebox.showwarning("Aviso", T("warn_no_voxels"))
                return

            self.result_data = {"voxels": voxels}
            self.start_app = True
            self.root.destroy()

        except Exception as e:
            messagebox.showerror(T("err_fatal"), f"{e}")


# --- 2. O APLICATIVO (PYGAME) ---

class VoxelModel:
    def __init__(self, initial_data=None):
        self.voxels = {} 
        self.history = [] 
        self.mirror_x = False
        self.pivot = (GRID_SIZE//2, GRID_SIZE//2, 0)
        
        if initial_data:
            if isinstance(initial_data, dict):
                self.voxels = initial_data.get("voxels", {})
                if "pivot" in initial_data: self.pivot = initial_data["pivot"]
            else:
                self.voxels = initial_data 

    def save_state(self):
        if len(self.history) > 20: self.history.pop(0)
        self.history.append((copy.deepcopy(self.voxels), self.pivot))

    def undo(self):
        if self.history: 
            data = self.history.pop()
            if isinstance(data, tuple): self.voxels, self.pivot = data
            else: self.voxels = data

    def set_voxel(self, x, y, z, color=None):
        def _set_single(vx, vy, vz, vcolor):
            if vcolor: self.voxels[(vx, vy, vz)] = vcolor
            else:
                if (vx, vy, vz) in self.voxels: del self.voxels[(vx, vy, vz)]
        _set_single(x, y, z, color)
        if self.mirror_x:
            mirror_pos_x = GRID_SIZE - 1 - x
            if mirror_pos_x != x: _set_single(mirror_pos_x, y, z, color)

    def get_voxel(self, x, y, z): return self.voxels.get((x, y, z))

    def move_model(self, dx, dy, dz):
        new_voxels = {}
        for (x, y, z), color in self.voxels.items():
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and 0 <= nz < GRID_SIZE: 
                 new_voxels[(nx, ny, nz)] = color
        self.voxels = new_voxels

    def clone_slice(self, axis, source_idx, dest_idx):
        self.save_state()
        to_clone = {}
        keys_to_remove = []
        for (x, y, z), color in self.voxels.items():
            coord = z if axis == 'Z' else (x if axis == 'X' else y)
            if coord == source_idx: to_clone[(x,y,z)] = color
            elif coord == dest_idx: keys_to_remove.append((x,y,z))
        for k in keys_to_remove: del self.voxels[k]
        for (x, y, z), color in to_clone.items():
            nx, ny, nz = x, y, z
            if axis == 'Z': nz = dest_idx
            elif axis == 'X': nx = dest_idx
            elif axis == 'Y': ny = dest_idx
            self.voxels[(nx, ny, nz)] = color

    def bucket_fill(self, u, v, axis, layer_idx, new_color):
        def to_3d_internal(au, av):
            inv_v = (GRID_SIZE - 1 - av)
            if axis == 'Z': return (au, av, layer_idx)
            if axis == 'X': return (layer_idx, au, inv_v)
            if axis == 'Y': return (au, layer_idx, inv_v)
            return (0,0,0)
        start_pos = to_3d_internal(u, v)
        target_color = self.voxels.get(start_pos) 
        if target_color == new_color: return
        queue = [(u, v)]
        processed = set() 
        while queue:
            cu, cv = queue.pop(0)
            if (cu, cv) in processed: continue
            processed.add((cu, cv))
            curr_3d = to_3d_internal(cu, cv)
            self.set_voxel(curr_3d[0], curr_3d[1], curr_3d[2], new_color)
            neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for du, dv in neighbors:
                nu, nv = cu + du, cv + dv
                if 0 <= nu < GRID_SIZE and 0 <= nv < GRID_SIZE:
                    next_3d = to_3d_internal(nu, nv)
                    neighbor_val = self.voxels.get(next_3d)
                    if neighbor_val == target_color: queue.append((nu, nv))

    # --- IO SYSTEM ---
    def save_project_json(self, filename):
        try:
            serializable_voxels = []
            for (x, y, z), color in self.voxels.items():
                serializable_voxels.append({ "x": x, "y": y, "z": z, "r": color[0], "g": color[1], "b": color[2] })
            data = { "version": "1.0", "data": serializable_voxels, "pivot": self.pivot }
            with open(filename, 'w') as f: json.dump(data, f)
            print(f"[SYSTEM] {T('msg_saved')}")
        except Exception as e: print(f"[ERROR] {e}")

    def load_project_json(self, filename, merge=False):
        try:
            with open(filename, 'r') as f: data = json.load(f)
            if not merge: 
                self.voxels = {}
                self.history = []
                self.pivot = tuple(data.get("pivot", (GRID_SIZE//2, GRID_SIZE//2, 0)))
            for v in data.get("data", []): 
                self.voxels[(v['x'], v['y'], v['z'])] = (v['r'], v['g'], v['b'])
            print(f"[SYSTEM] {T('msg_loaded')}")
        except Exception as e: print(f"[ERROR] {e}")

    def export_textured_obj(self, filename="VoxelProject.obj"):
        print(f"[SYSTEM] Baking...")
        unique_colors = sorted(list(set(self.voxels.values())))
        color_to_uv_index = {color: i for i, color in enumerate(unique_colors)}
        
        try:
            palette_width = max(1, len(unique_colors))
            palette_surface = pygame.Surface((palette_width, 1))
            for i, color in enumerate(unique_colors): palette_surface.set_at((i, 0), color)
            base_name = os.path.splitext(filename)[0]
            png_filename = base_name + ".png"
            pygame.image.save(palette_surface, png_filename)
        except Exception as e: print(f"[ERROR] Texture fail: {e}"); return

        try:
            with open(filename, 'w') as f:
                f.write(f"# CyberMolder v1.0\nmtllib {os.path.basename(base_name)}.mtl\no VoxelObject\n")
                f.write("vn 0 1 0\nvn 0 -1 0\nvn 1 0 0\nvn -1 0 0\nvn 0 0 -1\nvn 0 0 1\n") 
                for i in range(len(unique_colors)): f.write(f"vt {(i + 0.5)/len(unique_colors):.4f} 0.5\n") 

                vert_count = 1; px, py, pz = self.pivot
                faces = []
                for (x,y,z), color in self.voxels.items():
                    for i, (nx, ny, nz) in enumerate([(0,0,1), (0,0,-1), (1,0,0), (-1,0,0), (0,1,0), (0,-1,0)]):
                        if (x+nx, y+ny, z+nz) not in self.voxels: faces.append( {'pos': (x,y,z), 'dir': i, 'color': color} )
                
                faces_by_dir = [ {} for _ in range(6) ]
                for f_data in faces:
                    idx = f_data['dir']; p = f_data['pos']
                    key = p[2] if idx in [0,1] else (p[0] if idx in [2,3] else p[1])
                    if key not in faces_by_dir[idx]: faces_by_dir[idx][key] = []
                    faces_by_dir[idx][key].append(f_data)

                for dir_idx in range(6):
                    vn_idx = dir_idx + 1
                    for layer_key in faces_by_dir[dir_idx]:
                        layer_faces = faces_by_dir[dir_idx][layer_key]
                        if dir_idx in [0,1]: layer_faces.sort(key=lambda f: (f['pos'][1], f['pos'][0]))
                        if dir_idx in [2,3]: layer_faces.sort(key=lambda f: (f['pos'][2], f['pos'][1]))
                        if dir_idx in [4,5]: layer_faces.sort(key=lambda f: (f['pos'][2], f['pos'][0]))
                        
                        i = 0
                        while i < len(layer_faces):
                            current = layer_faces[i]; width = 1; j = i + 1
                            while j < len(layer_faces):
                                next_f = layer_faces[j]
                                if next_f['color'] != current['color']: break
                                p_curr = current['pos']; p_next = next_f['pos']; is_adj = False
                                if dir_idx in [0,1]: is_adj = (p_next[1] == p_curr[1] and p_next[0] == p_curr[0] + width)
                                elif dir_idx in [2,3]: is_adj = (p_next[2] == p_curr[2] and p_next[1] == p_curr[1] + width)
                                elif dir_idx in [4,5]: is_adj = (p_next[2] == p_curr[2] and p_next[0] == p_curr[0] + width)
                                if is_adj: width += 1; j += 1
                                else: break
                            
                            bx, by, bz = current['pos']; bx -= px; by -= py; bz -= pz
                            quad = []
                            if dir_idx == 0: quad = [(bx, by+1, bz+1), (bx+width, by+1, bz+1), (bx+width, by, bz+1), (bx, by, bz+1)]
                            elif dir_idx == 1: quad = [(bx, by, bz), (bx+width, by, bz), (bx+width, by+1, bz), (bx, by+1, bz)]
                            elif dir_idx == 2: quad = [(bx+1, by+width, bz), (bx+1, by+width, bz+1), (bx+1, by, bz+1), (bx+1, by, bz)]
                            elif dir_idx == 3: quad = [(bx, by, bz), (bx, by, bz+1), (bx, by+width, bz+1), (bx, by+width, bz)]
                            elif dir_idx == 4: quad = [(bx, by+1, bz), (bx+width, by+1, bz), (bx+width, by+1, bz+1), (bx, by+1, bz+1)]
                            elif dir_idx == 5: quad = [(bx+width, by, bz), (bx, by, bz), (bx, by, bz+1), (bx+width, by, bz+1)]

                            for v in quad: f.write(f"v {v[0]:.4f} {v[2]:.4f} {-v[1]:.4f}\n")
                            vt = color_to_uv_index[current['color']] + 1
                            f.write(f"f {vert_count}/{vt}/{vn_idx} {vert_count+1}/{vt}/{vn_idx} {vert_count+2}/{vt}/{vn_idx} {vert_count+3}/{vt}/{vn_idx}\n")
                            vert_count += 4; i += width
            print(f"[SYSTEM] {T('msg_exported')}")
        except Exception as e: print(f"[ERROR] {e}")

# --- UI ELEMENTS ---

class Button:
    def __init__(self, x, y, w, h, text, action, tooltip="", color_display=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.tooltip = tooltip
        self.color_display = color_display
        self.hover = False
        self.selected = False

    def draw(self, screen, font):
        if self.color_display:
            pygame.draw.rect(screen, self.color_display, self.rect)
            border_col = (255,255,255) if self.selected or self.hover else (0,0,0)
            thick = 3 if self.selected else 1
            pygame.draw.rect(screen, border_col, self.rect, thick)
        else:
            if self.text == "REC": bg_color = COLOR_BUTTON_REC if self.selected else (COLOR_BUTTON_HOVER if self.hover else COLOR_BUTTON)
            else: bg_color = COLOR_BUTTON_HOVER if self.hover else COLOR_BUTTON
            
            if self.selected and self.text != "REC": bg_color = COLOR_BUTTON_SELECTED
            
            pygame.draw.rect(screen, bg_color, self.rect)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 1) 
            txt_color = (0,0,0) if self.selected and self.text != "REC" else COLOR_TEXT
            txt_surf = font.render(self.text, True, txt_color)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            screen.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos): self.hover = self.rect.collidepoint(mouse_pos); return self.hover
    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos): self.action(); return True
        return False

# --- MAIN APP ---

class VoxelStudioApp:
    def __init__(self, initial_data=None):
        # NOTE: Criação de janelas de sistema é delegada ao Launcher ou funções específicas
        # para evitar conflito de loop no Linux
       
        # --- BLOCO DE ÍCONE (PYGAME) ---
        try:
            icon_surf = pygame.image.load("Icone.png")
            pygame.display.set_icon(icon_surf)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o ícone do Editor: {e}")
        # -------------------------------
       
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        pygame.init()
        pygame.font.init()
        
       
        
        self.width = INIT_WIDTH
        self.height = INIT_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        pygame.display.set_caption(T("win_title"))
        self.clock = pygame.time.Clock()
        
        # --- SAFE FONTS ---
        def get_safe_font(size, bold=True):
            fonts = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans", "FreeSans"]
            for f in fonts:
                if pygame.font.match_font(f):
                    return pygame.font.SysFont(f, size, bold)
            return pygame.font.SysFont(None, size, bold)

        self.font = get_safe_font(11)
        self.title_font = get_safe_font(20)
        self.help_font = get_safe_font(14, bold=False)
        
        self.model = VoxelModel(initial_data)
        self.current_slice = 15 
        self.edit_axis = 'Z'   
        self.tool = "PENCIL" 
        self.current_color = DB32[6]
        self.show_grid = True 
        self.view_angle = 0 
        self.show_help = False
        self.hover_text = ""
        self.view_scale = 0.8 
        self.pan_x = 0
        self.pan_y = 0
        
        self.is_recording = False
        self.record_angle = 0
        self.record_frames = 60 
        self.frame_counter = 0
        self.auto_rotate = False 
        
        self.grid_offset_x = 130 
        self.grid_offset_y = 100
        self.center_3d_x = self.width * 0.7 
        self.center_3d_y = self.height * 0.5 
        
        self.buttons = []
        self.color_buttons = []
        self.recalc_layout() 

    def recalc_layout(self):
        self.buttons = []
        self.color_buttons = []
        self.center_3d_x = self.width * 0.7
        self.center_3d_y = self.height * 0.5
        ctrl_y = 50
        bx = 130
        
        self.btn_axis_x = Button(bx, ctrl_y, 40, 30, "X", lambda: self.set_axis('X'))
        self.btn_axis_y = Button(bx+45, ctrl_y, 40, 30, "Y", lambda: self.set_axis('Y'))
        self.btn_axis_z = Button(bx+90, ctrl_y, 40, 30, "Z", lambda: self.set_axis('Z'))
        self.btn_layer_up = Button(bx+150, ctrl_y, 70, 30, "SLICE+", self.slice_up)
        self.btn_layer_dn = Button(bx+225, ctrl_y, 70, 30, "SLICE-", self.slice_down)
        self.btn_clone    = Button(bx+300, ctrl_y, 60, 30, "CLONE", self.clone_slice_action)
        
        self.btn_pencil = Button(bx+380, ctrl_y, 60, 30, "PENCIL", lambda: self.set_tool("PENCIL"), T("tip_pencil"))
        self.btn_bucket = Button(bx+445, ctrl_y, 60, 30, "BUCKET", lambda: self.set_tool("BUCKET"), T("tip_bucket"))
        self.btn_eraser = Button(bx+510, ctrl_y, 60, 30, "ERASER", lambda: self.set_tool("ERASER"), T("tip_eraser"))
        self.btn_pipette = Button(bx+575, ctrl_y, 60, 30, "PICKER", lambda: self.set_tool("PIPETTE"), T("tip_picker")) 
        self.btn_mirror = Button(bx+640, ctrl_y, 60, 30, "SYMM X", self.toggle_mirror, T("tip_mirror"))
        self.btn_pivot = Button(bx+705, ctrl_y, 60, 30, "PIVOT", lambda: self.set_tool("PIVOT"), T("tip_pivot"))
        
        self.btn_rec = Button(bx+770, ctrl_y, 50, 30, "REC", self.toggle_recording, T("tip_rec"))
        self.btn_clear  = Button(bx+825, ctrl_y, 60, 30, "CLEAR", self.clear_slice, T("tip_clear"))
        
        self.btn_help = Button(self.width - 120, ctrl_y, 100, 30, "HELP", self.toggle_help)

        self.buttons.extend([self.btn_axis_x, self.btn_axis_y, self.btn_axis_z,
                             self.btn_layer_up, self.btn_layer_dn, self.btn_clone,
                             self.btn_pencil, self.btn_bucket, self.btn_eraser, self.btn_pipette,
                             self.btn_mirror, self.btn_pivot, self.btn_rec, self.btn_clear, self.btn_help])
        
        self.set_axis(self.edit_axis)
        self.set_tool(self.tool)
        self.btn_mirror.selected = self.model.mirror_x
        self.btn_help.selected = self.show_help

        palette_start_x = 20
        palette_start_y = 100
        swatch_size = 25
        gap = 5
        for i, color in enumerate(DB32):
            col = i % 2; row = i // 2
            x = palette_start_x + (col * (swatch_size + gap))
            y = palette_start_y + (row * (swatch_size + gap))
            btn = Button(x, y, swatch_size, swatch_size, "", lambda c=color: self.set_color(c), color_display=color)
            if color == self.current_color: btn.selected = True
            self.color_buttons.append(btn)
        self.buttons.extend(self.color_buttons)

    def wait_for_release(self):
        pygame.event.pump()
        pygame.time.wait(200) 
        pygame.event.clear()

    def action_save_json(self):
        self.tk_root.attributes('-topmost', True)
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Voxel Project", "*.json")])
        self.wait_for_release()
        if filepath: self.model.save_project_json(filepath)

    def action_load_json(self):
        self.tk_root.attributes('-topmost', True)
        filepath = filedialog.askopenfilename(filetypes=[("Voxel Project", "*.json")])
        self.wait_for_release()
        if filepath: self.model.load_project_json(filepath)

    def action_export_obj(self):
        self.tk_root.attributes('-topmost', True)
        filepath = filedialog.asksaveasfilename(defaultextension=".obj", filetypes=[("Wavefront OBJ", "*.obj")])
        self.wait_for_release()
        if filepath: self.model.export_textured_obj(filepath)

    def toggle_help(self): self.show_help = not self.show_help; self.btn_help.selected = self.show_help
    def toggle_mirror(self): self.model.mirror_x = not self.model.mirror_x; self.btn_mirror.selected = self.model.mirror_x
    def set_axis(self, axis): self.edit_axis = axis; self.btn_axis_x.selected=(axis=='X'); self.btn_axis_y.selected=(axis=='Y'); self.btn_axis_z.selected=(axis=='Z')
    def set_tool(self, tool_name):
        self.tool = tool_name
        self.btn_pencil.selected=(tool_name=="PENCIL"); self.btn_eraser.selected=(tool_name=="ERASER")
        self.btn_bucket.selected=(tool_name=="BUCKET"); self.btn_pipette.selected=(tool_name=="PIPETTE"); self.btn_pivot.selected=(tool_name=="PIVOT")

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.frame_counter = 0
            self.btn_rec.selected = True
            self.btn_rec.text = "STOP"
            if not os.path.exists("Renders"): os.makedirs("Renders")
            print(T("rec_start"))
        else:
            self.is_recording = False
            self.btn_rec.selected = False
            self.btn_rec.text = "REC"
            print(T("rec_stop"))

    def set_color(self, color): self.current_color=color; (self.set_tool("PENCIL") if self.tool in ["ERASER","PIPETTE","PIVOT"] else None); self.recalc_layout()
    def slice_up(self): self.current_slice = min(GRID_SIZE-1, self.current_slice+1)
    def slice_down(self): self.current_slice = max(0, self.current_slice-1)
    def clone_slice_action(self): 
        if self.current_slice < GRID_SIZE-1: self.model.clone_slice(self.edit_axis, self.current_slice, self.current_slice+1); self.slice_up()
    def clear_slice(self): self.model.save_state(); [self.model.voxels.pop(k) for k in list(self.model.voxels) if (k[2] if self.edit_axis=='Z' else (k[0] if self.edit_axis=='X' else k[1])) == self.current_slice]
    def rotate_view(self, direction): self.view_angle = (self.view_angle + direction) % 4
    def map_2d_to_3d(self, u, v):
        if self.edit_axis == 'Z': return (u, v, self.current_slice)
        inv_v = (GRID_SIZE - 1 - v)
        if self.edit_axis == 'X': return (self.current_slice, u, inv_v) 
        if self.edit_axis == 'Y': return (u, self.current_slice, inv_v) 
        return (0,0,0)

    def handle_input(self):
        if self.is_recording:
            pygame.event.pump(); return

        mouse_pos = pygame.mouse.get_pos(); mouse_pressed = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed(); mods = pygame.key.get_mods(); is_move_mode = keys[pygame.K_v]

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: self.width=event.w; self.height=event.h; self.screen=pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE); self.recalc_layout()
            if event.type == pygame.MOUSEWHEEL:
                if mods & pygame.KMOD_SHIFT: self.view_scale = max(0.2, min(5.0, self.view_scale + event.y * 0.1))
                else: (self.slice_up() if event.y > 0 else self.slice_down())

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not any(b.check_click(mouse_pos) for b in self.buttons) and not self.show_help:
                    gu, gv = self.get_grid_coords(mouse_pos)
                    if gu is not None:
                        tx, ty, tz = self.map_2d_to_3d(gu, gv)
                        if self.tool == "PIVOT": self.model.pivot = (tx, ty, tz); self.set_tool("PENCIL") 
                        elif self.tool == "PIPETTE" or (mods & pygame.KMOD_ALT):
                            c = self.model.get_voxel(tx, ty, tz)
                            if c: self.set_color(c)
                        elif not is_move_mode:
                            if event.button == 1:
                                if self.tool == "BUCKET": self.model.save_state(); self.model.bucket_fill(gu, gv, self.edit_axis, self.current_slice, self.current_color)
                                elif self.tool in ["PENCIL", "ERASER"]: self.model.save_state(); self.model.set_voxel(tx, ty, tz, self.current_color if self.tool=="PENCIL" else None)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and (mods & pygame.KMOD_CTRL): self.model.undo()
                if event.key == pygame.K_PERIOD: self.slice_up()
                if event.key == pygame.K_COMMA: self.slice_down()
                if event.key == pygame.K_1: self.set_axis('X')
                if event.key == pygame.K_2: self.set_axis('Y')
                if event.key == pygame.K_3: self.set_axis('Z')
                if event.key == pygame.K_b: self.set_tool("PENCIL")
                if event.key == pygame.K_g: self.set_tool("BUCKET")
                if event.key == pygame.K_e: self.set_tool("ERASER")
                if event.key == pygame.K_i: self.set_tool("PIPETTE")
                if event.key == pygame.K_k: self.set_tool("PIVOT") 
                if event.key == pygame.K_m: self.toggle_mirror() 
                if event.key == pygame.K_h: self.toggle_help() 
                if event.key == pygame.K_r: self.auto_rotate = not self.auto_rotate 
                if event.key == pygame.K_s: (self.action_save_json() if mods & pygame.KMOD_CTRL else self.action_export_obj())
                if event.key == pygame.K_o and (mods & pygame.KMOD_CTRL): self.action_load_json()
                if event.key == pygame.K_TAB: self.show_grid = not self.show_grid
                if mods & pygame.KMOD_SHIFT: self.rotate_view(-1 if event.key == pygame.K_LEFT else (1 if event.key == pygame.K_RIGHT else 0))
                
                if keys[pygame.K_v]:
                    dx, dy, dz = 0, 0, 0
                    if self.edit_axis == 'Z': dx = -1 if event.key==pygame.K_LEFT else (1 if event.key==pygame.K_RIGHT else 0); dy = -1 if event.key==pygame.K_UP else (1 if event.key==pygame.K_DOWN else 0)
                    elif self.edit_axis == 'X': dy = -1 if event.key==pygame.K_LEFT else (1 if event.key==pygame.K_RIGHT else 0); dz = 1 if event.key==pygame.K_UP else (-1 if event.key==pygame.K_DOWN else 0)
                    elif self.edit_axis == 'Y': dx = -1 if event.key==pygame.K_LEFT else (1 if event.key==pygame.K_RIGHT else 0); dz = 1 if event.key==pygame.K_UP else (-1 if event.key==pygame.K_DOWN else 0)
                    if dx or dy or dz: self.model.move_model(dx, dy, dz)

        if mouse_pressed[2]: self.pan_x += pygame.mouse.get_rel()[0]; self.pan_y += pygame.mouse.get_rel()[1]
        else: pygame.mouse.get_rel() 

        if mouse_pressed[0] and not self.show_help: 
            gu, gv = self.get_grid_coords(mouse_pos)
            if gu is not None and self.tool not in ["BUCKET", "PIPETTE", "PIVOT"] and not is_move_mode:
                if not any(b.rect.collidepoint(mouse_pos) for b in self.buttons):
                    self.model.set_voxel(*self.map_2d_to_3d(gu, gv), self.current_color if self.tool == "PENCIL" else None)
        
        self.hover_text = next((b.tooltip for b in self.buttons if b.check_hover(mouse_pos)), "")

    def get_grid_coords(self, mouse_pos):
        if (self.grid_offset_x <= mouse_pos[0] < self.grid_offset_x + GRID_SIZE*CELL_SIZE and
            self.grid_offset_y <= mouse_pos[1] < self.grid_offset_y + GRID_SIZE*CELL_SIZE):
            return (mouse_pos[0] - self.grid_offset_x) // CELL_SIZE, (mouse_pos[1] - self.grid_offset_y) // CELL_SIZE
        return None, None

    def draw_help_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA); overlay.fill(COLOR_OVERLAY); self.screen.blit(overlay, (0,0))
        box_w, box_h = 700, 500
        box_x, box_y = (self.width - box_w)//2, (self.height - box_h)//2
        pygame.draw.rect(self.screen, (30, 30, 40), (box_x, box_y, box_w, box_h)); pygame.draw.rect(self.screen, (100, 255, 128), (box_x, box_y, box_w, box_h), 3)
        
        title_surf = self.title_font.render(T("help_title"), True, COLOR_HELP_TITLE)
        self.screen.blit(title_surf, (box_x + (box_w - title_surf.get_width())//2, box_y + 20))

        cats = [
            (T("h_file"), T("d_file")),
            (T("h_tool"), T("d_tool")),
            (T("h_nav"), T("d_nav")),
            (T("h_edit"), T("d_edit")),
            (T("h_extra"), T("d_extra"))
        ]
        
        y_off = 80
        for cat, desc in cats:
            self.screen.blit(self.font.render(cat, True, COLOR_HELP_CAT), (box_x + 40, box_y + y_off))
            self.screen.blit(self.help_font.render(desc, True, (255, 255, 255)), (box_x + 40, box_y + y_off + 25))
            y_off += 70

        close_surf = self.font.render(T("help_close"), True, (150, 150, 150))
        self.screen.blit(close_surf, (box_x + (box_w - close_surf.get_width())//2, box_y + box_h - 30))

    def draw_2d_editor(self):
        area_w = GRID_SIZE * CELL_SIZE
        pygame.draw.rect(self.screen, COLOR_GRID_BG, (self.grid_offset_x, self.grid_offset_y, area_w, area_w))
        px, py, pz = self.model.pivot; p_u, p_v = -1, -1; is_pivot_visible = False
        if self.edit_axis == 'Z' and pz == self.current_slice: p_u, p_v = px, py; is_pivot_visible = True
        if self.edit_axis == 'X' and px == self.current_slice: p_u, p_v = py, GRID_SIZE-1-pz; is_pivot_visible = True
        if self.edit_axis == 'Y' and py == self.current_slice: p_u, p_v = px, GRID_SIZE-1-pz; is_pivot_visible = True
        if is_pivot_visible:
            pr = (self.grid_offset_x + p_u*CELL_SIZE, self.grid_offset_y + p_v*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.line(self.screen, COLOR_PIVOT, (pr[0], pr[1]), (pr[0]+CELL_SIZE, pr[1]+CELL_SIZE), 3)
            pygame.draw.line(self.screen, COLOR_PIVOT, (pr[0]+CELL_SIZE, pr[1]), (pr[0], pr[1]+CELL_SIZE), 3)
        if self.model.mirror_x and self.edit_axis in ['Z', 'Y']:
            mid = self.grid_offset_x + (GRID_SIZE/2)*CELL_SIZE
            pygame.draw.line(self.screen, (255, 100, 100), (mid, self.grid_offset_y), (mid, self.grid_offset_y+area_w), 2)
        if self.current_slice > 0: 
            for v in range(GRID_SIZE):
                for u in range(GRID_SIZE):
                    prev = self.current_slice - 1; inv_v = GRID_SIZE - 1 - v
                    pos = (u,v,prev) if self.edit_axis=='Z' else ((prev,u,inv_v) if self.edit_axis=='X' else (u,prev,inv_v))
                    if pos in self.model.voxels: pygame.draw.rect(self.screen, (40,40,50), (self.grid_offset_x+u*CELL_SIZE, self.grid_offset_y+v*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for v in range(GRID_SIZE): 
            for u in range(GRID_SIZE):
                pos = self.map_2d_to_3d(u,v)
                if pos in self.model.voxels:
                    pygame.draw.rect(self.screen, self.model.voxels[pos], (self.grid_offset_x+u*CELL_SIZE, self.grid_offset_y+v*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, (255,255,255), (self.grid_offset_x+u*CELL_SIZE, self.grid_offset_y+v*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                elif self.show_grid: pygame.draw.rect(self.screen, COLOR_GRID_LINE, (self.grid_offset_x+u*CELL_SIZE, self.grid_offset_y+v*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
        border_col = AXIS_X_COLOR if self.edit_axis == 'X' else (AXIS_Y_COLOR if self.edit_axis == 'Y' else AXIS_Z_COLOR)
        pygame.draw.rect(self.screen, border_col, (self.grid_offset_x-2, self.grid_offset_y-2, area_w+4, area_w+4), 2)
        info = self.font.render(f"{T('slice')}: {self.current_slice}", True, COLOR_TEXT)
        self.screen.blit(info, (self.grid_offset_x, self.grid_offset_y - 20))
        if not self.show_help and not self.is_recording:
            mx, my = pygame.mouse.get_pos(); gu, gv = self.get_grid_coords((mx, my))
            if gu is not None:
                rect = (self.grid_offset_x+gu*CELL_SIZE, self.grid_offset_y+gv*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                col = COLOR_PIVOT if self.tool == "PIVOT" else (self.current_color if self.tool != "ERASER" else (255,0,0))
                pygame.draw.rect(self.screen, col, rect, 2)
                if self.model.mirror_x and self.edit_axis in ['Z','Y']:
                    mu = GRID_SIZE-1-gu
                    if mu!=gu: pygame.draw.rect(self.screen, (255,255,255), (self.grid_offset_x+mu*CELL_SIZE, self.grid_offset_y+gv*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def project_iso(self, x, y, z, cx, cy):
        center = GRID_SIZE / 2
        dx = x - center; dy = y - center
        if self.is_recording or self.auto_rotate:
            angle = (self.frame_counter / self.record_frames) * 2 * math.pi if self.is_recording else pygame.time.get_ticks() * 0.001
            rx = dx * math.cos(angle) - dy * math.sin(angle)
            ry = dx * math.sin(angle) + dy * math.cos(angle)
            rx += center; ry += center
        else:
            rx, ry = x, y
            if self.view_angle == 1: rx, ry = y, GRID_SIZE - 1 - x
            elif self.view_angle == 2: rx, ry = GRID_SIZE - 1 - x, GRID_SIZE - 1 - y
            elif self.view_angle == 3: rx, ry = GRID_SIZE - 1 - y, x
        current_size = VOXEL_ISO_SIZE * self.view_scale
        iso_x = (rx - ry) * current_size
        iso_y = (rx + ry) * (current_size / 2) - (z * current_size)
        return (cx + iso_x + self.pan_x, cy + iso_y + self.pan_y)

    def draw_3d_preview(self):
        cx, cy = self.center_3d_x, self.center_3d_y
        current_size = VOXEL_ISO_SIZE * self.view_scale
        render_list = []
        for pos, color in self.model.voxels.items():
            if self.is_recording or self.auto_rotate:
                center = GRID_SIZE / 2
                dx, dy = pos[0] - center, pos[1] - center
                angle = (self.frame_counter / self.record_frames) * 2 * math.pi if self.is_recording else pygame.time.get_ticks() * 0.001
                rx = dx * math.cos(angle) - dy * math.sin(angle)
                ry = dx * math.sin(angle) + dy * math.cos(angle)
                depth = rx + ry + pos[2] 
            else:
                rx, ry = pos[0], pos[1]
                if self.view_angle == 1: rx, ry = pos[1], GRID_SIZE - 1 - pos[0]
                elif self.view_angle == 2: rx, ry = GRID_SIZE - 1 - pos[0], GRID_SIZE - 1 - pos[1]
                elif self.view_angle == 3: rx, ry = GRID_SIZE - 1 - pos[1], pos[0]
                depth = rx + ry + pos[2]
            render_list.append((pos, color, depth))
        
        render_list.sort(key=lambda i: i[2])

        for pos, color, _ in render_list:
            isActive = not (self.is_recording or self.auto_rotate) and ((self.edit_axis=='Z' and pos[2]==self.current_slice) or (self.edit_axis=='X' and pos[0]==self.current_slice) or (self.edit_axis=='Y' and pos[1]==self.current_slice))
            sx, sy = self.project_iso(*pos, cx, cy)
            p_top = [(sx, sy-current_size), (sx+current_size, sy-current_size*0.5), (sx, sy), (sx-current_size, sy-current_size*0.5)]
            p_right = [(sx+current_size, sy-current_size*0.5), (sx+current_size, sy+current_size*0.5), (sx, sy+current_size), (sx, sy)]
            p_left = [(sx, sy), (sx, sy+current_size), (sx-current_size, sy+current_size*0.5), (sx-current_size, sy-current_size*0.5)]
            pygame.draw.polygon(self.screen, color, p_top)
            pygame.draw.polygon(self.screen, (max(0,color[0]-30), max(0,color[1]-30), max(0,color[2]-30)), p_right)
            pygame.draw.polygon(self.screen, (max(0,color[0]-60), max(0,color[1]-60), max(0,color[2]-60)), p_left)
            if (self.show_grid or isActive) and not self.is_recording:
                bc = (255,255,255) if isActive else (0,0,0)
                pygame.draw.polygon(self.screen, bc, p_top, 1); pygame.draw.polygon(self.screen, bc, p_right, 1); pygame.draw.polygon(self.screen, bc, p_left, 1)

        px, py, pz = self.model.pivot
        sx, sy = self.project_iso(px, py, pz, cx, cy)
        pygame.draw.line(self.screen, COLOR_PIVOT, (sx-10, sy), (sx+10, sy), 3)
        pygame.draw.line(self.screen, COLOR_PIVOT, (sx, sy-10), (sx, sy+10), 3)

        if self.show_grid and not self.is_recording:
            c1,c2,c3,c4 = (0,0,0),(0,0,0),(0,0,0),(0,0,0)
            sl = self.current_slice
            if self.edit_axis=='Z': c1=(0,0,sl); c2=(GRID_SIZE,0,sl); c3=(GRID_SIZE,GRID_SIZE,sl); c4=(0,GRID_SIZE,sl)
            elif self.edit_axis=='X': c1=(sl,0,0); c2=(sl,GRID_SIZE,0); c3=(sl,GRID_SIZE,GRID_SIZE); c4=(sl,0,GRID_SIZE)
            elif self.edit_axis=='Y': c1=(0,sl,0); c2=(GRID_SIZE,sl,0); c3=(GRID_SIZE,sl,GRID_SIZE); c4=(0,sl,GRID_SIZE)
            pygame.draw.lines(self.screen, COLOR_SLICE_FRAME, True, [self.project_iso(*p, cx, cy) for p in [c1,c2,c3,c4]], 2)

        if not self.show_help and not self.is_recording:
            mx, my = pygame.mouse.get_pos(); gu, gv = self.get_grid_coords((mx, my))
            if gu is not None:
                tx, ty, tz = self.map_2d_to_3d(gu, gv)
                self.draw_cursor_3d(tx, ty, tz, cx, cy, current_size)
                if self.model.mirror_x:
                    mx_pos = GRID_SIZE - 1 - tx
                    if mx_pos != tx: self.draw_cursor_3d(mx_pos, ty, tz, cx, cy, current_size, True)

        self.draw_gizmo(cx - 200 + self.pan_x, cy + 200 + self.pan_y)

    def draw_gizmo(self, center_x, center_y):
        if center_x < -500 or center_x > self.width + 500: return
        def iso_proj(x, y, z):
            if self.is_recording or self.auto_rotate:
                angle = (self.frame_counter / self.record_frames) * 2 * math.pi if self.is_recording else pygame.time.get_ticks() * 0.001
                rx = x * math.cos(angle) - y * math.sin(angle); ry = x * math.sin(angle) + y * math.cos(angle)
            else:
                rx, ry = x, y
                if self.view_angle == 1: rx, ry = y, -x
                elif self.view_angle == 2: rx, ry = -x, -y
                elif self.view_angle == 3: rx, ry = -y, x
            px = (rx - ry) * 0.8; py = (rx + ry) * 0.4 - z * 0.8
            return (center_x + px * 40, center_y + py * 40)
        origin = (center_x, center_y)
        pygame.draw.line(self.screen, AXIS_X_COLOR, origin, iso_proj(1,0,0), 3)
        pygame.draw.line(self.screen, AXIS_Y_COLOR, origin, iso_proj(0,1,0), 3)
        pygame.draw.line(self.screen, AXIS_Z_COLOR, origin, iso_proj(0,0,1), 3)
        self.screen.blit(self.font.render("X",1,AXIS_X_COLOR), iso_proj(1.2,0,0))
        self.screen.blit(self.font.render("Y",1,AXIS_Y_COLOR), iso_proj(0,1.2,0))
        self.screen.blit(self.font.render("Z",1,AXIS_Z_COLOR), iso_proj(0,0,1.2))

    def draw_cursor_3d(self, x, y, z, cx, cy, current_size, is_mirror=False):
        sx, sy = self.project_iso(x, y, z, cx, cy)
        col = COLOR_GHOST_CURSOR if not is_mirror else (255, 255, 255)
        p_top = [(sx, sy - current_size), (sx + current_size, sy - current_size * 0.5), (sx, sy), (sx - current_size, sy - current_size * 0.5)]
        p_bot = [(p[0], p[1] + current_size) for p in p_top]
        pygame.draw.lines(self.screen, col, True, p_top, 2)
        pygame.draw.lines(self.screen, col, True, p_bot, 1)
        for i in range(4): pygame.draw.line(self.screen, col, p_top[i], p_bot[i], 1)

    def draw(self):
        self.screen.fill(COLOR_BG)
        title = self.title_font.render(T("win_title"), True, (100, 255, 128))
        self.screen.blit(title, (20, 10))
        self.draw_2d_editor(); self.draw_3d_preview()
        for btn in self.buttons: btn.draw(self.screen, self.font)
        self.screen.blit(self.font.render(T("palette"), True, (150,150,150)), (20, 80))
        if self.hover_text: self.screen.blit(self.font.render(f"TIP: {self.hover_text}", True, (255,200,0)), (80, self.height-30))
        if self.show_help: self.draw_help_overlay()
        if self.is_recording:
            pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, self.width, self.height), 5)
            rec_text = self.title_font.render(f"RECORDING FRAME {self.frame_counter}/{self.record_frames}", True, (255, 0, 0))
            self.screen.blit(rec_text, (self.width//2 - 150, self.height - 50))
            filename = f"Renders/frame_{self.frame_counter:03d}.png"
            pygame.image.save(self.screen, filename)
            self.frame_counter += 1
            if self.frame_counter >= self.record_frames: self.toggle_recording()
        pygame.display.flip()

if __name__ == "__main__":
    launcher = VoxelLauncher()
    start_game, initial_data = launcher.run()

    if start_game:
        app = VoxelStudioApp(initial_data)
        while True:
            app.handle_input()
            app.draw()
            app.clock.tick(60)
