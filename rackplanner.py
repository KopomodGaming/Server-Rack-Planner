#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

U_HEIGHT = 40
DEFAULT_U = 12

class RackPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RackPlanner")
        self.root.configure(bg='#2e2e2e')
        self.rack_height = DEFAULT_U
        self.rack_items = [None] * self.rack_height

        self.component_categories = {
            "Networking": {
                "UDM Pro": 1,
                "Switch": 1,
                "Patch Panel": 1,
                "Router": 1,
                "Firewall": 1,
                "KVM Switch": 1,
                "Media Converter": 1
            },
            "Hardware": {
                "1U Server": 1,
                "2U Server": 2,
                "3U Server": 3,
                "4U Server": 4,
                "2U Shelf": 2,
                "Disk Shelf": 3,
                "Rackmount Workstation": 4,
                "Tape Drive": 1,
                "NAS Appliance": 2
            },
            "Power": {
                "Power Strip": 1,
                "UPS": 2,
                "PDU": 1,
                "ATS": 1
            },
            "Filler": {
                "Brush Panel": 1,
                "Blanking Panel": 1,
                "Cable Management": 1,
                "Ventilated Panel": 1
            }
        }

        self.setup_ui()
        self.draw_rack()
        self.update_u_display()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2e2e2e')
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, width=320, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        controls = tk.Frame(main_frame, bg='#2e2e2e')
        controls.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH)

        tk.Label(controls, text="Rack Size:", bg='#2e2e2e', fg='white').pack(anchor='w')
        self.rack_size_var = tk.IntVar(value=DEFAULT_U)
        size_options = [4, 6, 9, 12, 16, 19, 24, 32, 42]
        self.rack_size_menu = ttk.Combobox(controls, textvariable=self.rack_size_var, values=size_options, state='readonly')
        self.rack_size_menu.pack(fill=tk.X, pady=(0, 10))
        self.rack_size_menu.bind("<<ComboboxSelected>>", self.change_rack_size)

        tk.Label(controls, text="Select Category:", bg='#2e2e2e', fg='white').pack(anchor='w')
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(controls, textvariable=self.category_var, state='readonly')
        self.category_menu['values'] = list(self.component_categories.keys())
        self.category_menu.bind("<<ComboboxSelected>>", self.update_component_menu)
        self.category_menu.pack(fill=tk.X, pady=(0, 10))

        tk.Label(controls, text="Select Component:", bg='#2e2e2e', fg='white').pack(anchor='w')
        self.component_var = tk.StringVar()
        self.component_menu = ttk.Combobox(controls, textvariable=self.component_var, state='readonly')
        self.component_menu.pack(fill=tk.X, pady=(0, 10))

        tk.Button(controls, text="Add to Rack", command=self.add_component, bg='#4caf50', fg='white').pack(fill=tk.X, pady=5)
        tk.Button(controls, text="Clear Rack", command=self.clear_rack, bg='#f44336', fg='white').pack(fill=tk.X, pady=5)

        tk.Frame(controls, height=10, bg='#2e2e2e').pack() # Spacer

        self.used_u_label = tk.Label(controls, text="Used U: 0", bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        self.used_u_label.pack(anchor='w', pady=(5, 0))

        self.unused_u_label = tk.Label(controls, text="Unused U: 0", bg='#2e2e2e', fg='white', font=('Arial', 10, 'bold'))
        self.unused_u_label.pack(anchor='w', pady=(0, 5))


    def draw_rack(self):
        self.canvas.delete("all")
        self.rack_items = [None] * self.rack_height
        self.canvas.config(height=U_HEIGHT * self.rack_height)

        for i in range(self.rack_height):
            y = i * U_HEIGHT
            self.canvas.create_rectangle(30, y, 310, y + U_HEIGHT, outline='white')
            self.canvas.create_text(5, y + U_HEIGHT // 2, anchor='w', fill='white', text=f"{self.rack_height - i}U")

        self.update_u_display()

    def change_rack_size(self, event=None):
        self.rack_height = self.rack_size_var.get()
        self.draw_rack()

    def update_component_menu(self, event=None):
        category = self.category_var.get()
        if category in self.component_categories:
            components = list(self.component_categories[category].keys())
            self.component_menu['values'] = components
            if components:
                self.component_var.set(components[0])

    def add_component(self):
        component = self.component_var.get()
        if not component:
            messagebox.showerror("Error", "Select a component first.")
            return

        size = self.get_component_size(component)
        try:
            slot_input = simpledialog.askstring("Slot Selection", f"Enter starting U slot (1-{self.rack_height}):")
            if slot_input is None:
                return
            slot = int(slot_input)
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a number.")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

        if not slot or slot < 1 or slot > self.rack_height:
            messagebox.showerror("Error", "Invalid U slot.")
            return

        start_index = self.rack_height - slot
        
        if start_index < 0 or start_index + size > self.rack_height:
            messagebox.showerror("Error", "Component does not fit in rack at the selected slot.")
            return

        if any(self.rack_items[i] is not None for i in range(start_index, start_index + size)):
            messagebox.showerror("Error", "Slot(s) already occupied.")
            return

        for i in range(size):
            self.rack_items[start_index + i] = component
        
        y1 = start_index * U_HEIGHT
        y2 = y1 + size * U_HEIGHT
        rect = self.canvas.create_rectangle(30, y1, 310, y2, fill='skyblue', outline='white')
        text = self.canvas.create_text(170, (y1 + y2) // 2, fill='black', font=('Arial', 10, 'bold'), text=component)

        def rename_component(event, item=text):
            new_name = simpledialog.askstring("Rename Component", "Enter new name:")
            if new_name:
                self.canvas.itemconfig(item, text=new_name)

        self.canvas.tag_bind(text, '<Double-1>', rename_component)
        self.canvas.tag_bind(rect, '<Double-1>', rename_component)

        self.update_u_display()

    def get_component_size(self, component):
        for category in self.component_categories.values():
            if component in category:
                return category[component]
        return 1

    def clear_rack(self):
        self.draw_rack()
        self.update_u_display()

    def update_u_display(self):
        """Calculates and updates the display of used and unused U slots."""
        used_u = 0
        for item in self.rack_items:
            if item is not None:
                used_u += 1
        
        unused_u = self.rack_height - used_u

        self.used_u_label.config(text=f"Used U: {used_u}")
        self.unused_u_label.config(text=f"Unused U: {unused_u}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RackPlannerApp(root)
    root.mainloop()
