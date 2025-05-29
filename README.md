RackPlanner App

RackPlanner is a simple desktop application built with Tkinter that allows you to visually plan and organize your server rack components. You can add pre-defined components, create your own custom components, arrange them in a virtual rack, and save/load your configurations.
Features

    Customizable Rack Size: Set the height of your rack in U units.

    Pre-defined Components: A selection of common networking, server, storage, power, management, and cooling components.

    Custom Component Definition: Create your own components with custom names, U-sizes, and colors.

    Drag-and-Drop Placement: Easily drag and drop components onto the rack.

    Collision Detection: The app prevents you from placing components in occupied or out-of-bounds U-slots.

    Real-time U-slot Tracking: See how many U-slots are used and unused.

    Save/Load Rack Configurations: Save your entire rack layout to a JSON file and load it later.

    Save/Load Custom Components: Export and import your custom-defined components separately.

    Undo/Redo Functionality: Revert or reapply changes to your rack layout.

    Export to Image: Save your rack diagram as a PNG image.

Installation

    Prerequisites:

        Python 3.x installed on your system.

        Pillow library: This is required for the "Export to Image" functionality.

    Install Pillow:
    Open your terminal or command prompt and run:

    pip install Pillow

    Download the Application:
    Save the rackplanner.py file to your desired location.

How to Run

Navigate to the directory where you saved rackplanner.py in your terminal or command prompt, and run:

python rackplanner.py

How to Use
1. Adjusting Rack Size

    On the right-hand side, use the "Rack Size" dropdown to select your desired rack height (in U units).

    If reducing the rack size would cut off existing components, you will be prompted for confirmation.

2. Adding Components

    From Palette:

        On the left-hand side, you'll see a "Components" palette organized by categories (Networking, Servers, Storage, etc.).

        Click on any component in the palette. It will automatically be placed in the first available U-slot from the bottom of the rack.

    Defining Custom Components:

        Click the "Define Custom Component" button on the right.

        Enter a name for your component.

        Enter its U-size (e.g., 1 for a 1U device, 2 for a 2U device).

        Choose a color for your custom component using the color picker.

        Your new custom component will appear under the "Custom" category in the palette and can be placed like other components.

3. Moving Components

    Click and drag an existing component on the rack.

    A "ghost" outline will appear, showing the potential new position.

    The highlight color will indicate if the drop zone is valid (green) or invalid (red).

    Release the mouse button to drop the component. If the drop is invalid, the component will return to its original position.

4. Deleting Components

    Right-click on any component placed on the rack.

    A confirmation dialog will appear. Click "Yes" to delete the component.

5. Managing Rack Configurations

    Save Rack: Click "Save Rack" to save your current rack layout (including placed components and custom components) to a JSON file.

    Load Rack: Click "Load Rack" to load a previously saved rack configuration from a JSON file. This will replace your current rack layout.

6. Managing Custom Components Separately

    Save Custom Components: Click "Save Custom Components" to export only your custom-defined components to a JSON file. This is useful for sharing or backing up your custom parts without saving the entire rack layout.

    Load Custom Components: Click "Load Custom Components" to import custom components from a JSON file. These components will be added to your "Custom" category in the palette, allowing you to use them in your current or future rack designs.

7. Undo/Redo

    Undo: Click the "Undo" button to revert the last action.

    Redo: Click the "Redo" button to reapply an undone action.

8. Exporting as Image

    Click "Export to Image" to save a PNG image of your current rack diagram. This captures only the canvas area.

Troubleshooting

    "Failed to export image" error: Ensure you have the Pillow library installed (pip install Pillow). On Linux/macOS, you might also need system-level screenshot utilities (e.g., scrot on Linux, screencapture on macOS).

    Invalid JSON file on load: Ensure the JSON file you are trying to load was created by the RackPlanner app and is not corrupted.

    Components not fitting: If you reduce the rack size, components that no longer fit will be automatically removed. You will receive a warning.
