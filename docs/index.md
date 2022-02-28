# Welcome to Node Expose

Node Expose gives you a simple way of exposing the properties of any node or group of nodes in the N menu of the 3D Viewport or Node Editor by framing your node(s). This means you can modify your material or geometry node setup without having to switch back and forth between the node editor and 3D Viewport. Using Node Expose is also a good way of indicating which parameters of a material or node setup can be tweaked safely and which should be left alone.

## Usage
Node Expose works with Material (Shader), Geometry, Compositor and Texture Nodes. For this example we'll use the shader node editor, but the same principle applies for the other node editors.

1. In the Blender startup file, select the default cube and switch to Shading mode.
2. Add a frame node ( **Shift A** > **Layout** > **Frame** )
3. Drag and drop the Principled BSDF Node inside the frame so that if you move the frame the BSDF node moves with it.
4. Select the Frame you have just added and in the N menu ( Right hand Menu ) Select the **Node** tab.
5. In the Expose Nodes panel click **Expose Frame**
6. You will now have a new tab, **Node Expose** in the N menu of the Node Editor, and the N Menu of the 3D Viewport where you can see the properties of the BSDF node.
7. Dragging and dropping more nodes into the frame will also expose them in this panel.
