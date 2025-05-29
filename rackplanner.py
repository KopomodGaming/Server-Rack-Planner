#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog, colorchooser
import json
from PIL import ImageGrab, Image

U_HEIGHT = 40
DEFAULT_U = 12
RACK_WIDTH_PX = 280
RACK_LEFT_MARGIN = 30
RACK_RIGHT_MARGIN = RACK_LEFT_MARGIN + RACK_WIDTH_PX
PALETTE_WIDTH_PX = 200

class RackPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RackPlanner")
        self.root.configure(bg='#2e2e2e')
        
        self.rack_height = DEFAULT_U
        self.rack_items = [None] * self.rack_height
        self.placed_components_data = []

        self._dragging_component = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_highlight_rects = []
        self._ghost_rect_id = None
        self._ghost_text_id = None

        self._history = []
        self._history_index = -1

        self.component_categories = {
            "Networking": {
                "UDM Pro": {"size": 1, "color": "#FFC107"},
                "Router": {"size": 1, "color": "#FFC107"},
                "Firewall": {"size": 1, "color": "#FFC107"},
                "Managed Switch": {"size": 1, "color": "#FFC107"},
                "PoE Switch": {"size": 1, "color": "#FFC107"},
                "Media Converter": {"size": 1, "color": "#FFC107"},
                "Modem/ONT": {"size": 1, "color": "#FFC107"}
            },
            "Servers": {
                "1U Server": {"size": 1, "color": "#4CAF50"},
                "2U Server": {"size": 2, "color": "#4CAF50"},
                "3U Server": {"size": 3, "color": "#4CAF50"},
                "4U Server": {"size": 4, "color": "#4CAF50"},
                "Rackmount Workstation": {"size": 4, "color": "#4CAF50"},
                "Mini PC/NUC": {"size": 1, "color": "#4CAF50"}
            },
            "Storage": {
                "Disk Shelf": {"size": 3, "color": "#9E9E9E"},
                "NAS Appliance": {"size": 2, "color": "#9E9E9E"},
                "Tape Drive": {"size": 1, "color": "#9E9E9E"},
                "HDD Enclosure": {"size": 2, "color": "#9E9E9E"}
            },
            "Power": {
                "Power Strip": {"size": 1, "color": "#F44336"},
                "UPS": {"size": 2, "color": "#F44336"},
                "PDU": {"size": 1, "color": "#F44336"},
                "ATS": {"size": 1, "color": "#F44336"}
            },
            "Management & Accessories": {
                "Patch Panel": {"size": 1, "color": "#8BC34A"},
                "KVM Switch": {"size": 1, "color": "#8BC34A"},
                "Cable Management": {"size": 1, "color": "#8BC34A"},
                "2U Shelf": {"size": 2, "color": "#8BC34A"},
                "Rackmount Monitor/KVM Drawer": {"size": 1, "color": "#8BC34A"}
            },
            "Cooling": {
                "Rackmount Fan Unit": {"size": 1, "color": "#00BCD4"}
            },
            "Filler": {
                "Brush Panel": {"size": 1, "color": "#2196F3"},
                "Blanking Panel": {"size": 1, "color": "#2196F3"},
                "Ventilated Panel": {"size": 1, "color": "#2196F3"}
            },
            "Custom": {}
        }

        self.setup_ui()
        self._draw_rack_and_components()
        self._record_current_state()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2e2e2e')
        main_frame.pack(fill=tk.BOTH, expand=True)

        palette_frame = tk.Frame(main_frame, bg='#3c3c3c', width=PALETTE_WIDTH_PX)
        palette_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        palette_label = tk.Label(palette_frame, text="Components", bg='#3c3c3c', fg='white', font=('Arial', 10, 'bold'))
        palette_label.pack(pady=5)

        self.palette_scrollbar = tk.Scrollbar(palette_frame, orient="vertical")
        self.palette_scrollbar.pack(side="right", fill="y")

        self.palette_canvas = tk.Canvas(palette_frame, bg='#3c3c3c', highlightthickness=0, yscrollcommand=self.palette_scrollbar.set)
        self.palette_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.palette_scrollbar.config(command=self.palette_canvas.yview)
        
        self.palette_inner_frame = tk.Frame(self.palette_canvas, bg='#3c3c3c')
        self.palette_canvas.create_window((0, 0), window=self.palette_inner_frame, anchor="nw")
        self.palette_inner_frame.bind("<Configure>", lambda e: self.palette_canvas.configure(scrollregion = self.palette_canvas.bbox("all")))

        self.palette_canvas.bind("<Button-4>", self._on_palette_mousewheel)
        self.palette_canvas.bind("<Button-5>", self._on_palette_mousewheel)
        self.palette_canvas.bind("<MouseWheel>", self._on_palette_mousewheel)


        self.canvas = tk.Canvas(main_frame, width=320, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
        
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._drop)

        controls = tk.Frame(main_frame, bg='#2e2e2e')
        controls.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)

        tk.Label(controls, text="Rack Size:", bg='#2e2e2e', fg='white').pack(anchor='w')
        self.rack_size_var = tk.IntVar(value=DEFAULT_U)
        size_options = [4, 6, 9, 12, 16, 19, 24, 32, 42]
        self.rack_size_menu = ttk.Combobox(controls, textvariable=self.rack_size_var, values=size_options, state='readonly')
        self.rack_size_menu.pack(fill=tk.X, pady=(0, 10))
        self.rack_size_menu.bind("<<ComboboxSelected>>", self.change_rack_size)

        tk.Button(controls, text="Define Custom Component", command=self.add_custom_component, bg='#2196f3', fg='white').pack(fill=tk.X, pady=5)
        
        tk.Button(controls, text="Save Custom Components", command=self.save_custom_components, bg='#4CAF50', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(controls, text="Load Custom Components", command=self.load_custom_components, bg='#4CAF50', fg='white').pack(fill=tk.X, pady=2)

        tk.Frame(controls, height=5, bg='#2e2e2e').pack()

        tk.Button(controls, text="Clear Rack", command=self.clear_rack, bg='#f44336', fg='white').pack(fill=tk.X, pady=5)
        
        undo_redo_frame = tk.Frame(controls, bg='#2e2e2e')
        undo_redo_frame.pack(fill=tk.X, pady=5)
        self.undo_btn = tk.Button(undo_redo_frame, text="Undo", command=self.undo, bg='#607D8B', fg='white')
        self.undo_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
        self.redo_btn = tk.Button(undo_redo_frame, text="Redo", command=self.redo, bg='#607D8B', fg='white')
        self.redo_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2,0))

        tk.Frame(controls, height=5, bg='#2e2e2e').pack()

        tk.Button(controls, text="Save Rack", command=self.save_rack_config, bg='#ff9800', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Load Rack", command=self.load_rack_config, bg='#ff9800', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Export to Image", command=self.export_canvas_as_image, bg='#009688', fg='white').pack(fill=tk.X, pady=5)


        tk.Frame(controls, height=10, bg='#2e2e2e').pack()

        self.used_u_label = tk.Label(controls, text="Used U: 0", bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        self.unused_u_label = tk.Label(controls, text="Unused U: 0", bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        self.used_u_label.pack(anchor='w', pady=(5, 0))
        self.unused_u_label.pack(anchor='w', pady=(0, 5))

        self.update_palette()
        self._update_undo_redo_buttons()

    def _draw_rack_and_components(self):
        self.canvas.delete("all")
        self.rack_items = [None] * self.rack_height

        self.canvas.config(height=U_HEIGHT * self.rack_height)

        self.canvas.create_rectangle(
            RACK_LEFT_MARGIN, 0, RACK_RIGHT_MARGIN, self.rack_height * U_HEIGHT,
            fill='#282828', outline='#555555', width=2
        )

        for i in range(self.rack_height):
            y = i * U_HEIGHT
            self.canvas.create_line(RACK_LEFT_MARGIN, y, RACK_RIGHT_MARGIN, y, fill='#666666', width=1)
            self.canvas.create_text(2, y + U_HEIGHT // 2, anchor='w', fill='white', text=f"{self.rack_height - i}U")
        
        self.canvas.create_line(RACK_LEFT_MARGIN, self.rack_height * U_HEIGHT, RACK_RIGHT_MARGIN, self.rack_height * U_HEIGHT, fill='#666666', width=1)

        self.canvas.create_line(RACK_LEFT_MARGIN, 0, RACK_LEFT_MARGIN, self.rack_height * U_HEIGHT, fill='#555555', width=2)
        self.canvas.create_line(RACK_RIGHT_MARGIN, 0, RACK_RIGHT_MARGIN, self.rack_height * U_HEIGHT, fill='#555555', width=2)

        for comp_data in self.placed_components_data:
            self._render_single_component(comp_data)
        
        self._sync_rack_items()
        self.update_u_display()

    def _render_single_component(self, comp_data):
        start_index_0_based_top = self.rack_height - (comp_data['start_u_slot'] + comp_data['size_u'] - 1)

        y1 = start_index_0_based_top * U_HEIGHT
        y2 = y1 + comp_data['size_u'] * U_HEIGHT
        
        color_hex = comp_data.get('color', 'skyblue')
        if len(color_hex) == 7:
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
        else:
            r, g, b = 135, 206, 235

        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = 'white' if luminance < 0.5 else 'black'

        rect = self.canvas.create_rectangle(RACK_LEFT_MARGIN, y1, RACK_RIGHT_MARGIN, y2, 
                                            fill=comp_data.get('color', 'skyblue'), outline='#333333', width=2, tags="component_item")
        text = self.canvas.create_text(RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, (y1 + y2) // 2, 
                                        fill=text_color, font=('Arial', 10, 'bold'), text=comp_data['name'], tags="component_item")

        comp_data['rect_id'] = rect
        comp_data['text_id'] = text

        self.canvas.tag_bind(rect, '<Button-3>', lambda e, data=comp_data: self.delete_component_on_click(e, data))
        self.canvas.tag_bind(text, '<Button-3>', lambda e, data=comp_data: self.delete_component_on_click(e, data))
        

    def _sync_rack_items(self):
        self.rack_items = [None] * self.rack_height
        for comp_data in self.placed_components_data:
            start_index_0_based_top = self.rack_height - (comp_data['start_u_slot'] + comp_data['size_u'] - 1)
            for i in range(start_index_0_based_top, start_index_0_based_top + comp_data['size_u']):
                if 0 <= i < self.rack_height:
                    self.rack_items[i] = comp_data['name']

    def _record_current_state(self):
        current_state = {
            'rack_height': self.rack_height,
            'placed_components': [
                {'name': comp['name'], 'start_u_slot': comp['start_u_slot'], 'size_u': comp['size_u'], 'color': comp.get('color', 'skyblue')}
                for comp in self.placed_components_data
            ]
        }
        
        self._history = self._history[:self._history_index + 1]
        self._history.append(current_state)
        self._history_index = len(self._history) - 1
        self._update_undo_redo_buttons()

    def _load_state_from_history(self, state_data):
        self.rack_height = state_data['rack_height']
        self.rack_size_var.set(self.rack_height)
        self.placed_components_data = []
        
        for comp_data in state_data['placed_components']:
            self.placed_components_data.append(comp_data.copy())

        self._draw_rack_and_components()
        self._update_undo_redo_buttons()

    def _update_undo_redo_buttons(self):
        self.undo_btn.config(state=tk.NORMAL if self._history_index > 0 else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if self._history_index < len(self._history) - 1 else tk.DISABLED)

    def undo(self):
        if self._history_index > 0:
            self._history_index -= 1
            self._load_state_from_history(self._history[self._history_index])

    def redo(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._load_state_from_history(self._history[self._history_index])

    def change_rack_size(self, event=None):
        new_height = self.rack_size_var.get()
        if new_height < self.rack_height:
            highest_u_used = 0
            for item in self.placed_components_data:
                highest_u_used = max(highest_u_used, item['start_u_slot'] + item['size_u'] - 1)
            
            if highest_u_used > new_height:
                if not messagebox.askyesno("Warning", "Reducing rack size will cut off placed components. Are you sure?"):
                    self.rack_size_var.set(self.rack_height)
                    return

        self.rack_height = new_height
        
        new_placed_components_data = []
        removed_count = 0
        for comp_data in list(self.placed_components_data):
            if comp_data['start_u_slot'] + comp_data['size_u'] - 1 <= self.rack_height:
                new_placed_components_data.append(comp_data)
            else:
                removed_count += 1
                messagebox.showwarning("Component Removed", f"Component '{comp_data['name']}' was removed because it no longer fits in the {self.rack_height}U rack.")
        self.placed_components_data = new_placed_components_data

        self._draw_rack_and_components()
        self._record_current_state()


    def get_component_info(self, component_name):
        for category_name, category_items in self.component_categories.items():
            if component_name in category_items:
                return category_items[component_name]
        return None

    def is_slot_available(self, start_u_slot, size_u):
        start_index_0_based_top = self.rack_height - (start_u_slot + size_u - 1)
        end_index_0_based_top = start_index_0_based_top + size_u

        if start_index_0_based_top < 0 or end_index_0_based_top > self.rack_height:
            return False

        for i in range(start_index_0_based_top, end_index_0_based_top):
            if self.rack_items[i] is not None:
                return False
        return True

    def add_component_manual(self):
        messagebox.showinfo("Info", "Please click components in the 'Components' palette on the left to place them.")
        
    def delete_component_on_click(self, event, component_data):
        if messagebox.askyesno("Delete Component", f"Are you sure you want to delete '{component_data['name']}' at {component_data['start_u_slot']}U?"):
            self._delete_component_logic(component_data)

    def _delete_component_logic(self, component_data):
        self.canvas.delete(component_data['rect_id'])
        self.canvas.delete(component_data['text_id'])

        self.placed_components_data.remove(component_data)
        
        self._sync_rack_items()
        self.update_u_display()
        self._record_current_state()

    def rename_component_on_click(self, event, component_data):
        new_name = simpledialog.askstring("Rename Component", "Enter new name:", initialvalue=component_data['name'])
        if new_name and new_name != component_data['name']:
            component_data['name'] = new_name
            self.canvas.itemconfig(component_data['text_id'], text=new_name)
            self._sync_rack_items()
            self._record_current_state()


    def clear_rack(self):
        if messagebox.askyesno("Clear Rack", "Are you sure you want to clear the entire rack?"):
            self.placed_components_data = []
            self._draw_rack_and_components()
            self._record_current_state()

    def update_u_display(self):
        used_u = 0
        occupied_slots = set()
        for comp in self.placed_components_data:
            start_index_0_based_top = self.rack_height - (comp['start_u_slot'] + comp['size_u'] - 1)
            for i in range(start_index_0_based_top, start_index_0_based_top + comp['size_u']):
                if 0 <= i < self.rack_height:
                    occupied_slots.add(i)
        
        used_u = len(occupied_slots)
        unused_u = self.rack_height - used_u

        self.used_u_label.config(text=f"Used U: {used_u}")
        self.unused_u_label.config(text=f"Unused U: {unused_u}")

    def add_custom_component(self):
        name = simpledialog.askstring("Custom Component", "Enter component name:")
        if not name:
            return

        size = simpledialog.askinteger("Custom Component", "Enter U size for component:", minvalue=1, maxvalue=self.rack_height)
        if not size:
            return
        
        color_code = colorchooser.askcolor(title="Choose Component Color")[1]
        if not color_code:
            color_code = 'skyblue'

        self.component_categories["Custom"][name] = {"size": size, "color": color_code}
        self.update_palette()
        
        messagebox.showinfo("Success", f"Custom component '{name}' ({size}U) added to 'Custom' category.")

    def _place_component_from_palette(self, comp_name, comp_size, comp_color):
        placed = False
        for start_u_slot in range(1, self.rack_height - comp_size + 2):
            if self.is_slot_available(start_u_slot, comp_size):
                new_comp_data = {
                    'name': comp_name,
                    'start_u_slot': start_u_slot,
                    'size_u': comp_size,
                    'color': comp_color
                }
                self.placed_components_data.append(new_comp_data)
                self._render_single_component(new_comp_data)
                self._sync_rack_items()
                self.update_u_display()
                self._record_current_state()
                placed = True
                break
        
        if not placed:
            messagebox.showerror("No Space", f"Cannot place '{comp_name}' ({comp_size}U). No available contiguous space in the rack.")


    def update_palette(self):
        for widget in self.palette_inner_frame.winfo_children():
            widget.destroy()

        for category_name, category_items in self.component_categories.items():
            ttk.Label(self.palette_inner_frame, text=f"-- {category_name} --") \
                .pack(fill=tk.X, pady=(5,2))
            
            for comp_name, comp_info in category_items.items():
                comp_size = comp_info['size']
                comp_color = comp_info['color']
                
                palette_item_frame = tk.Frame(self.palette_inner_frame, bd=1, relief="solid", bg=comp_color)
                palette_item_frame.pack(fill=tk.X, padx=5, pady=2)
                
                palette_label = tk.Label(palette_item_frame, text=f"{comp_name} ({comp_size}U)", 
                                         bg=comp_color, fg='black', font=('Arial', 9))
                palette_label.pack(side=tk.LEFT, padx=5, pady=2)

                palette_item_frame.bind("<Button-1>", lambda e, name=comp_name, size=comp_size, color=comp_color: 
                                        self._place_component_from_palette(name, size, color))
                palette_label.bind("<Button-1>", lambda e, name=comp_name, size=comp_size, color=comp_color: 
                                   self._place_component_from_palette(name, size, color))

        self.palette_inner_frame.update_idletasks()
        self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all"))


    def save_rack_config(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                title="Save Rack Configuration")
        if not file_path:
            return

        save_data = {
            "rack_height": self.rack_height,
            "placed_components": [
                {'name': comp['name'], 'start_u_slot': comp['start_u_slot'], 'size_u': comp['size_u'], 'color': comp.get('color', 'skyblue')}
                for comp in self.placed_components_data
            ],
            "custom_components": self.component_categories["Custom"]
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            messagebox.showinfo("Save Success", "Rack configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")

    def load_rack_config(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                              filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                              title="Load Rack Configuration")
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)

            self.rack_height = loaded_data.get("rack_height", DEFAULT_U)
            self.rack_size_var.set(self.rack_height)
            
            self.component_categories["Custom"] = loaded_data.get("custom_components", {})
            self.update_palette()

            loaded_components_with_color = []
            for comp in loaded_data.get("placed_components", []):
                if 'color' not in comp:
                    comp_info = self.get_component_info(comp['name'])
                    comp['color'] = comp_info.get('color', 'skyblue') if comp_info else 'skyblue'
                loaded_components_with_color.append(comp)

            self.placed_components_data = loaded_components_with_color
            self._draw_rack_and_components()
            
            self._record_current_state()
            messagebox.showinfo("Load Success", "Rack configuration loaded successfully!")

        except FileNotFoundError:
            messagebox.showerror("Load Error", "File not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Invalid JSON file.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load configuration: {e}")

    def save_custom_components(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                title="Save Custom Components")
        if not file_path:
            return

        try:
            with open(file_path, 'w') as f:
                json.dump(self.component_categories["Custom"], f, indent=4)
            messagebox.showinfo("Save Success", "Custom components saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save custom components: {e}")

    def load_custom_components(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                              filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                              title="Load Custom Components")
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                loaded_custom_data = json.load(f)
            
            if isinstance(loaded_custom_data, dict):
                for name, info in loaded_custom_data.items():
                    if not (isinstance(info, dict) and 'size' in info and 'color' in info):
                        raise ValueError("Invalid format for custom component data.")
                self.component_categories["Custom"].update(loaded_custom_data)
                self.update_palette()
                messagebox.showinfo("Load Success", "Custom components loaded successfully!")
            else:
                raise ValueError("Loaded data is not in the expected dictionary format.")

        except FileNotFoundError:
            messagebox.showerror("Load Error", "File not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Invalid JSON file. Please ensure it contains valid custom component data.")
        except ValueError as e:
            messagebox.showerror("Load Error", f"Invalid custom components file format: {e}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load custom components: {e}")

    def export_canvas_as_image(self):
        self.canvas.update_idletasks() 

        x=self.root.winfo_x()+self.canvas.winfo_x()
        y=self.root.winfo_y()+self.canvas.winfo_y()
        x1=x+self.canvas.winfo_width()
        y1=y+self.canvas.winfo_height()

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                                title="Export Rack Diagram as Image")
        if not file_path:
            return
        
        try:
            ImageGrab.grab(bbox=(x, y, x1, y1)).save(file_path)
            messagebox.showinfo("Export Success", f"Rack diagram exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export image. Make sure Pillow is installed (pip install Pillow) and necessary screenshot utilities are available on Linux/macOS. Error: {e}")

    def _start_drag(self, event):
        self._dragging_component = None
        self._clear_highlights()
        self._clear_ghost()

        if event.widget == self.canvas:
            closest_item_ids = self.canvas.find_closest(event.x, event.y)
            if not closest_item_ids:
                return

            clicked_item_id = closest_item_ids[0]

            for comp_data in self.placed_components_data:
                if comp_data['rect_id'] == clicked_item_id or comp_data['text_id'] == clicked_item_id:
                    self._dragging_component = comp_data
                    
                    start_index_0_based_top = self.rack_height - (self._dragging_component['start_u_slot'] + self._dragging_component['size_u'] - 1)
                    for i in range(start_index_0_based_top, start_index_0_based_top + self._dragging_component['size_u']):
                        if 0 <= i < self.rack_height:
                            self.rack_items[i] = None
                    self.canvas.itemconfig(self._dragging_component['rect_id'], state='hidden')
                    self.canvas.itemconfig(self._dragging_component['text_id'], state='hidden')

                    original_coords = self.canvas.coords(comp_data['rect_id'])
                    x1_orig, y1_orig, x2_orig, y2_orig = original_coords

                    ghost_fill_color = self._dragging_component['color']
                    ghost_outline_color = 'gray'
                    ghost_text_color = 'black'

                    self._ghost_rect_id = self.canvas.create_rectangle(
                        x1_orig, y1_orig, x2_orig, y2_orig,
                        fill=ghost_fill_color, outline=ghost_outline_color, stipple='gray50', tags="ghost_item",
                        width=2
                    )
                    self._ghost_text_id = self.canvas.create_text(
                        (x1_orig + x2_orig) / 2, (y1_orig + y2_orig) / 2,
                        fill=ghost_text_color, font=('Arial', 10, 'bold'), text=self._dragging_component['name'], tags="ghost_item"
                    )
                    self.canvas.tag_raise(self._ghost_rect_id)
                    self.canvas.tag_raise(self._ghost_text_id)
                    break
        
        if self._dragging_component:
            self._drag_start_x = event.x 
            self._drag_start_y = event.y


    def _drag_motion(self, event):
        if self._dragging_component:
            self._clear_highlights()

            target_u_index_0_based_top = int(event.y / U_HEIGHT)
            
            size_u = self._dragging_component['size_u']

            potential_start_u_slot = self.rack_height - (target_u_index_0_based_top + size_u - 1)

            potential_start_u_slot = max(1, potential_start_u_slot)
            potential_start_u_slot = min(potential_start_u_slot, self.rack_height - size_u + 1)
            
            is_valid_drop = self.is_slot_available(potential_start_u_slot, size_u)

            snapped_top_y_0_based_top = self.rack_height - (potential_start_u_slot + size_u - 1)
            snapped_ghost_y1 = snapped_top_y_0_based_top * U_HEIGHT
            snapped_ghost_y2 = snapped_ghost_y1 + size_u * U_HEIGHT
            snapped_ghost_center_y = (snapped_ghost_y1 + snapped_ghost_y2) // 2

            self.canvas.coords(self._ghost_rect_id, 
                                RACK_LEFT_MARGIN, snapped_ghost_y1, 
                                RACK_RIGHT_MARGIN, snapped_ghost_y2) 
            self.canvas.coords(self._ghost_text_id, 
                                RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, snapped_ghost_center_y)


            self._highlight_slots(potential_start_u_slot, size_u, is_valid_drop)

    def _drop(self, event):
        if self._dragging_component:
            if self._ghost_rect_id is None:
                if self._dragging_component:
                    self.canvas.itemconfig(self._dragging_component['rect_id'], state='normal')
                    self.canvas.itemconfig(self._dragging_component['text_id'], state='normal')
                    self._sync_rack_items()
                self._dragging_component = None
                self._clear_highlights()
                self._clear_ghost()
                return

            ghost_rect_coords = self.canvas.coords(self._ghost_rect_id)
            final_ghost_top_y = ghost_rect_coords[1]
            
            size_u = self._dragging_component['size_u']

            final_u_index_0_based_top = int(final_ghost_top_y / U_HEIGHT)
            target_start_u_slot = self.rack_height - (final_u_index_0_based_top + size_u - 1)

            target_start_u_slot = max(1, target_start_u_slot)
            target_start_u_slot = min(target_start_u_slot, self.rack_height - size_u + 1)

            is_valid_drop = self.is_slot_available(target_start_u_slot, size_u)

            self._clear_highlights()
            self._clear_ghost() 

            if is_valid_drop:
                self._dragging_component['start_u_slot'] = target_start_u_slot

                start_index_new_0_based_top = self.rack_height - (target_start_u_slot + size_u - 1)
                y1_new = start_index_new_0_based_top * U_HEIGHT
                y2_new = y1_new + size_u * U_HEIGHT

                self.canvas.coords(self._dragging_component['rect_id'], RACK_LEFT_MARGIN, y1_new, RACK_RIGHT_MARGIN, y2_new)
                self.canvas.coords(self._dragging_component['text_id'], RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, (y1_new + y2_new) // 2)

                self._sync_rack_items()
                self.update_u_display()
                self.canvas.itemconfig(self._dragging_component['rect_id'], state='normal')
                self.canvas.itemconfig(self._dragging_component['text_id'], state='normal')
                self._record_current_state()

            else:
                messagebox.showerror("Invalid Drop", "Cannot place component here. Slots are occupied or out of bounds.")
                
                original_start_u_slot = self._dragging_component['start_u_slot']
                original_size_u = self._dragging_component['size_u']
                original_start_index_0_based_top = self.rack_height - (original_start_u_slot + original_size_u - 1)
                
                original_y1 = original_start_index_0_based_top * U_HEIGHT
                original_y2 = original_y1 + original_size_u * U_HEIGHT
                self.canvas.coords(self._dragging_component['rect_id'], RACK_LEFT_MARGIN, original_y1, RACK_RIGHT_MARGIN, original_y2)
                self.canvas.itemconfig(self._dragging_component['rect_id'], state='normal')
                self.canvas.coords(self._dragging_component['text_id'], RACK_LEFT_MARGIN + RACK_WIDTH_PX // 2, (original_y1 + original_y2) // 2)
                self.canvas.itemconfig(self._dragging_component['text_id'], state='normal')
                
                self._sync_rack_items()

            self._dragging_component = None
            self.update_u_display()

    def _highlight_slots(self, start_u_slot, size_u, is_valid):
        self._clear_highlights()

        color = '#A5D6A7' if is_valid else '#EF9A9A'
        
        start_index_0_based_top = self.rack_height - (start_u_slot + size_u - 1)
        end_index_0_based_top = start_index_0_based_top + size_u

        start_index_0_based_top = max(0, start_index_0_based_top)
        end_index_0_based_top = min(self.rack_height, end_index_0_based_top)

        for i in range(start_index_0_based_top, end_index_0_based_top):
            y1 = i * U_HEIGHT
            y2 = y1 + U_HEIGHT
            rect_id = self.canvas.create_rectangle(RACK_LEFT_MARGIN, y1, RACK_RIGHT_MARGIN, y2, 
                                                   fill=color, stipple='gray50', outline=color,
                                                   tags="highlight_rect") 
            self._drag_highlight_rects.append(rect_id)
        if self._ghost_rect_id:
             self.canvas.tag_raise(self._ghost_rect_id)
             self.canvas.tag_raise(self._ghost_text_id)

    def _clear_highlights(self):
        for rect_id in self._drag_highlight_rects:
            self.canvas.delete(rect_id)
        self._drag_highlight_rects = []

    def _clear_ghost(self):
        if self._ghost_rect_id:
            self.canvas.delete(self._ghost_rect_id)
            self._ghost_rect_id = None
        if self._ghost_text_id:
            self.canvas.delete(self._ghost_text_id)
            self._ghost_text_id = None

    def _on_palette_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.palette_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.palette_canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = RackPlannerApp(root)
    root.mainloop()
