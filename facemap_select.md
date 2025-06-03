# FacemapSelect Blender Add-on

**Author:** Michel Anders (varkenvarken)  
**Blender Version:** 4.4.0+  
**Category:** Mesh  
**Repository:** [GitHub](https://github.com/varkenvarken/blenderaddons)

----

## Installation

1.  Download the Python script (`facemap_select.py`) from [https://raw.githubusercontent.com/varkenvarken/blenderaddons/refs/heads/master/facemap_select.py](https://raw.githubusercontent.com/varkenvarken/blenderaddons/refs/heads/master/facemap_select.py).
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click the `Install from disk ...` button (down arrow at the top right),
4. Select the downloaded file, and enable the add-on.

## Usage

### 1. Accessing the Panel

- Go to the **Properties Editor**.
- Select the **Mesh Data** tab (triangle icon).
- Find the **face Maps** panel.

### 2. Creating an Face Map

1. Enter **Edit Mode** (`Tab` key).
2. Select the faces you want to include in the new map.
3. In the **Face Maps** panel, click the **Add (+)** button.
4. A new face map is created, storing the selection as a boolean attribute.

### 3. Assigning or Removing Faces

- Select faces in Edit Mode.
- In the **Face Maps** panel, select the desired face map.
- Click **Assign** to add selected faces to the map.
- Click **Remove** to remove selected faces from the map.

### 4. Selecting or Deselecting Edges by Map

- With a face map active, click **Select** to select all faces in the map.
- Click **Deselect** to deselect all faces in the map.
- Hold **Shift** while clicking **Select** to replace the current selection with the map.

### 5. Deleting an Edge Map

- Select the face map in the list.
- Click the **Remove (-)** button to delete it.


## Notes

- Face maps are stored as boolean custom attributes on the mesh, under the "FACE" domain.
- Only boolean face maps are shown and managed by this add-on (They will show up in the Attributes panel as well)

## License

This add-on is licensed under the GNU General Public License v2 or later.

## Feedback

For any issues or suggestions, please raise an issue or create a PR