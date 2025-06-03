# EdgemapSelect Blender Add-on

**Author:** Michel Anders (varkenvarken)  
**Blender Version:** 4.4.0+  
**Category:** Mesh  
**Repository:** [GitHub](https://github.com/varkenvarken/blenderaddons)

---

## Overview

**EdgemapSelect** is a Blender add-on that allows you to create, manage, and use boolean edge maps on mesh objects. With this tool, you can easily select or deselect edges based on custom edge maps, assign or remove edges from maps, and manage multiple edge maps per mesh.

---

## Features

- **Create Edge Maps:** Generate a new boolean edge map from the current edge selection.
- **Assign/Remove Edges:** Add or remove selected edges to/from the active edge map.
- **Select/Deselect by Map:** Select or deselect edges based on the active edge map.
- **Delete Edge Maps:** Remove unwanted edge maps from your mesh.
- **UI Integration:** Access all features from the Mesh Data Properties panel.

---

## Installation

1. Download the `edgemap_select.py` file from [https://raw.githubusercontent.com/varkenvarken/blenderaddons/refs/heads/master/edgemap_select.py](https://raw.githubusercontent.com/varkenvarken/blenderaddons/refs/heads/master/edgemap_select.py).
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click the `Install from disk ...` button (down arrow at the top right),
4. Select the downloaded file, and enable the add-on.

---

## Usage

### 1. Accessing the Panel

- Go to the **Properties Editor**.
- Select the **Mesh Data** tab (triangle icon).
- Find the **Edge Maps** panel.

### 2. Creating an Edge Map

1. Enter **Edit Mode** (`Tab` key).
2. Select the edges you want to include in the new map.
3. In the **Edge Maps** panel, click the **Add (+)** button.
4. A new edge map is created, storing the selection as a boolean attribute.

### 3. Assigning or Removing Edges

- Select edges in Edit Mode.
- In the **Edge Maps** panel, select the desired edge map.
- Click **Assign** to add selected edges to the map.
- Click **Remove** to remove selected edges from the map.

### 4. Selecting or Deselecting Edges by Map

- With an edge map active, click **Select** to select all edges in the map.
- Click **Deselect** to deselect all edges in the map.
- Hold **Shift** while clicking **Select** to replace the current selection with the map.

### 5. Deleting an Edge Map

- Select the edge map in the list.
- Click the **Remove (-)** button to delete it.


## Notes

- Edge maps are stored as boolean custom attributes on the mesh, under the "EDGE" domain.
- Only boolean edge maps are shown and managed by this add-on (They will show up in the Attributes panel as well).

## License

This add-on is licensed under the GNU General Public License v2 or later.

## Feedback

For any issues or suggestions, please raise an issue or create a PR