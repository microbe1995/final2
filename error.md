https://reactflow.dev/api-reference




https://reactflow.dev/learn/customization/custom-nodes

https://reactflow.dev/learn/customization/handles


https://reactflow.dev/learn/customization/custom-edges

https://reactflow.dev/learn/customization/utility-classes

위 링크는react flow 라이브러리의 공식홈페이지야
여기를 매우 상세히 참고해서 지금 일어나는 연결 문제를 해결해줘



Custom Nodes
A powerful feature of React Flow is the ability to create custom nodes. This gives you the flexibility to render anything you want within your nodes. We generally recommend creating your own custom nodes rather than relying on built-in ones. With custom nodes, you can add as many source and target handles as you like—or even embed form inputs, charts, and other interactive elements.

In this section, we’ll walk through creating a custom node featuring an input field that updates text elsewhere in your application. For further examples, we recommend checking out our Custom Node Example.

import React, { useState, useEffect, useCallback } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
  Controls,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';

import ColorSelectorNode from './ColorSelectorNode';

const initBgColor = '#c9f1dd';

const snapGrid = [20, 20];
const nodeTypes = {
  selectorNode: ColorSelectorNode,
};

const defaultViewport = { x: 0, y: 0, zoom: 1.5 };

const CustomNodeFlow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [bgColor, setBgColor] = useState(initBgColor);

  useEffect(() => {
    const onChange = (event) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id !== '2') {
            return node;
          }

          const color = event.target.value;

          setBgColor(color);

          return {
            ...node,
            data: {
              ...node.data,
              color,
            },
          };
        }),
      );
    };

    setNodes([
      {
        id: '1',
        type: 'input',
        data: { label: 'An input node' },
        position: { x: 0, y: 50 },
        sourcePosition: 'right',
      },
      {
        id: '2',
        type: 'selectorNode',
        data: { onChange: onChange, color: initBgColor },
        position: { x: 300, y: 50 },
      },
      {
        id: '3',
        type: 'output',
        data: { label: 'Output A' },
        position: { x: 650, y: 25 },
        targetPosition: 'left',
      },
      {
        id: '4',
        type: 'output',
        data: { label: 'Output B' },
        position: { x: 650, y: 100 },
        targetPosition: 'left',
      },
    ]);

    setEdges([
      {
        id: 'e1-2',
        source: '1',
        target: '2',
        animated: true,
      },
      {
        id: 'e2a-3',
        source: '2',
        target: '3',
        animated: true,
      },
      {
        id: 'e2b-4',
        source: '2',
        target: '4',
        animated: true,
      },
    ]);
  }, []);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [],
  );
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      style={{ background: bgColor }}
      nodeTypes={nodeTypes}
      snapToGrid={true}
      snapGrid={snapGrid}
      defaultViewport={defaultViewport}
      fitView
      attributionPosition="bottom-left"
    >
      <MiniMap
        nodeStrokeColor={(n) => {
          if (n.type === 'input') return '#0041d0';
          if (n.type === 'selectorNode') return bgColor;
          if (n.type === 'output') return '#ff0072';
        }}
        nodeColor={(n) => {
          if (n.type === 'selectorNode') return bgColor;
          return '#fff';
        }}
      />
      <Controls />
    </ReactFlow>
  );
};

export default CustomNodeFlow;


import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

export default memo(({ data, isConnectable }) => {
  return (
    <>
      <Handle
        type="target"
        position={Position.Left}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={isConnectable}
      />
      <div>
        Custom Color Picker Node: <strong>{data.color}</strong>
      </div>
      <input
        className="nodrag"
        type="color"
        onChange={data.onChange}
        defaultValue={data.color}
      />
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
      />
    </>
  );
});


/* xyflow theme files. Delete these to start from our base */

.react-flow {
  --xy-background-color: #f7f9fb;
  /* Custom Variables */
  --xy-theme-selected: #f57dbd;
  --xy-theme-hover: #c5c5c5;
  --xy-theme-edge-hover: black;
  --xy-theme-color-focus: #e8e8e8;

  /* Built-in Variables see https://reactflow.dev/learn/customization/theming */
  --xy-node-border-default: 1px solid #ededed;

  --xy-node-boxshadow-default:
    0px 3.54px 4.55px 0px #00000005, 0px 3.54px 4.55px 0px #0000000d,
    0px 0.51px 1.01px 0px #0000001a;

  --xy-node-border-radius-default: 8px;

  --xy-handle-background-color-default: #ffffff;
  --xy-handle-border-color-default: #aaaaaa;

  --xy-edge-label-color-default: #505050;
}

.react-flow.dark {
  --xy-node-boxshadow-default:
    0px 3.54px 4.55px 0px rgba(255, 255, 255, 0.05),
    /* light shadow */ 0px 3.54px 4.55px 0px rgba(255, 255, 255, 0.13),
    /* medium shadow */ 0px 0.51px 1.01px 0px rgba(255, 255, 255, 0.2); /* smallest shadow */
  --xy-theme-color-focus: #535353;
}

/* Customizing Default Theming */

.react-flow__node {
  box-shadow: var(--xy-node-boxshadow-default);
  border-radius: var(--xy-node-border-radius-default);
  background-color: var(--xy-node-background-color-default);
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 10px;
  font-size: 12px;
  flex-direction: column;
  border: var(--xy-node-border-default);
  color: var(--xy-node-color, var(--xy-node-color-default));
}

.react-flow__node.selectable:focus {
  box-shadow: 0px 0px 0px 4px var(--xy-theme-color-focus);
  border-color: #d9d9d9;
}

.react-flow__node.selectable:focus:active {
  box-shadow: var(--xy-node-boxshadow-default);
}

.react-flow__node.selectable:hover,
.react-flow__node.draggable:hover {
  border-color: var(--xy-theme-hover);
}

.react-flow__node.selectable.selected {
  border-color: var(--xy-theme-selected);
  box-shadow: var(--xy-node-boxshadow-default);
}

.react-flow__node-group {
  background-color: rgba(207, 182, 255, 0.4);
  border-color: #9e86ed;
}

.react-flow__edge.selectable:hover .react-flow__edge-path,
.react-flow__edge.selectable.selected .react-flow__edge-path {
  stroke: var(--xy-theme-edge-hover);
}

.react-flow__handle {
  background-color: var(--xy-handle-background-color-default);
}

.react-flow__handle.connectionindicator:hover {
  pointer-events: all;
  border-color: var(--xy-theme-edge-hover);
  background-color: white;
}

.react-flow__handle.connectionindicator:focus,
.react-flow__handle.connectingfrom,
.react-flow__handle.connectingto {
  border-color: var(--xy-theme-edge-hover);
}

.react-flow__node-resizer {
  border-radius: 0;
  border: none;
}

.react-flow__resize-control.handle {
  background-color: #ffffff;
  border-color: #9e86ed;
  border-radius: 0;
  width: 5px;
  height: 5px;
}

/* 
  Custom Example CSS  - This CSS is to improve the example experience.
  You can remove it if you want to use the default styles.

  New Theme Classes:
    .xy-theme__button   - Styles for buttons.
    .xy-theme__input    - Styles for text inputs.
    .xy-theme__checkbox - Styles for checkboxes.
    .xy-theme__select   - Styles for dropdown selects.
    .xy-theme__label    - Styles for labels.
  
  Use these classes to apply consistent theming across your components.
*/

:root {
  --color-primary: #ff0073;
  --color-background: #fefefe;
  --color-hover-bg: #f6f6f6;
  --color-disabled: #76797e;
}

.xy-theme__button-group {
  display: flex;
  align-items: center;

  .xy-theme__button:first-child {
    border-radius: 100px 0 0 100px;
  }

  .xy-theme__button:last-child {
    border-radius: 0 100px 100px 0;
    margin: 0;
  }
}

/* Custom Button Styling */
.xy-theme__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.5rem;
  padding: 0 1rem;
  border-radius: 100px;
  border: 1px solid var(--color-primary);
  background-color: var(--color-background);
  color: var(--color-primary);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
  box-shadow: var(--xy-node-boxshadow-default);
  cursor: pointer;
}

.xy-theme__button.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.xy-theme__button.active:hover,
.xy-theme__button.active:active {
  background-color: var(--color-primary);
  opacity: 0.9;
}

.xy-theme__button:hover {
  background-color: var(--xy-controls-button-background-color-hover-default);
}

.xy-theme__button:active {
  background-color: var(--color-hover-bg);
}

.xy-theme__button:disabled {
  color: var(--color-disabled);
  opacity: 0.8;
  cursor: not-allowed;
  border: 1px solid var(--color-disabled);
}

.xy-theme__button > span {
  margin-right: 0.2rem;
}

/* Add gap between adjacent buttons */
.xy-theme__button + .xy-theme__button {
  margin-left: 0.3rem;
}

/* Example Input Styling */
.xy-theme__input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: 7px;
  background-color: var(--color-background);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
  font-size: 1rem;
  color: inherit;
}

.xy-theme__input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(255, 0, 115, 0.3);
}

/* Specific Checkbox Styling */
.xy-theme__checkbox {
  appearance: none;
  -webkit-appearance: none;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 7px;
  border: 2px solid var(--color-primary);
  background-color: var(--color-background);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
  cursor: pointer;
  display: inline-block;
  vertical-align: middle;
  margin-right: 0.5rem;
}

.xy-theme__checkbox:checked {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.xy-theme__checkbox:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 0, 115, 0.3);
}

/* Dropdown Styling */
.xy-theme__select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: 50px;
  background-color: var(--color-background);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease;
  font-size: 1rem;
  color: inherit;
  margin-right: 0.5rem;
  box-shadow: var(--xy-node-boxshadow-default);
}

.xy-theme__select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(255, 0, 115, 0.3);
}

.xy-theme__label {
  margin-top: 10px;
  margin-bottom: 3px;
  display: inline-block;
}


@import url('./xy-theme.css');

html,
body {
  margin: 0;
  font-family: sans-serif;
  box-sizing: border-box;
}

#app {
  width: 100vw;
  height: 100vh;
}


Handles
Handles are the connection points on nodes in React Flow. Our built-in nodes include one source and one target handle, but you can customize your nodes with as many different handles as you need.

Creating a node with handles
To create a custom node with handles, you can use the <Handle /> component provided by React Flow. This component allows you to define source and target handles for your custom nodes. Here’s an example of how to implement a custom node with two handles:

import { Handle } from '@xyflow/react';
 
export function CustomNode() {
  return (
    <div className="custom-node">
      <div>Custom Node Content</div>
      <Handle type="source" position="top" />
      <Handle type="target" position="bottom" />
    </div>
  );
}

Using multiple handles
If you want to use multiple source or target handles in your custom node, you need to specify each handle with a unique id. This allows React Flow to differentiate between the handles when connecting edges.

  <Handle type="target" position="top" />
  <Handle type="source" position="right" id="a" />
  <Handle type="source" position="bottom" id="b" />

  To connect an edge to a specific handle of a node, use the properties sourceHandle (for the edge’s starting point) and targetHandle (for the edge’s ending point). By defining sourceHandle or targetHandle with the appropriate handle id, you instruct React Flow to attach the edge to that specific handle, ensuring that connections are made where you intend.


const initialEdges = [
  { id: 'n1-n2', source: 'n1', sourceHandle: 'a', target: 'n2' },
  { id: 'n1-n3', source: 'n1', sourceHandle: 'b', target: 'n3' },
];
In this case, the source node is n1 for both handles but the handle ids are different. One comes from handle id a and the other one from b. Both edges also have different target nodes:

Custom handles
You can create your own custom handles by wrapping the <Handle /> component. This example shows a custom handle that only allows connections when the connection source matches a given id.


import { Handle, Position } from '@xyflow/react';
 
export function TargetHandleWithValidation({ position, source }) {
  return (
    <Handle
      type="target"
      position={position}
      isValidConnection={(connection) => connection.source === source}
      onConnect={(params) => console.log('handle onConnect', params)}
      style={{ background: '#fff' }}
    />
  );
}

Typeless handles
If you want to create a handle that does not have a specific type (source or target), you can set connectionMode to Loose in the <ReactFlow /> component. This allows the handle to be used for both incoming and outgoing connections.

Dynamic handles
If you are programmatically changing the position or number of handles in your custom node, you need to update the node internals with the useUpdateNodeInternals hook.

Custom handle styles
Since the handle is a div, you can use CSS to style it or pass a style prop to customize a Handle. You can see this in the Add Node On Edge Drop and Simple Floating Edges examples.

Styling handles when connecting
The handle receives the additional class names connecting when the connection line is above the handle and valid if the connection is valid. You can find an example which uses these classes here.

Hiding handles
If you need to hide a handle for some reason, you must use visibility: hidden or opacity: 0 instead of display: none. This is important because React Flow needs to calculate the dimensions of the handle to work properly and using display: none will report a width and height of 0!

Custom Edges
Like custom nodes, parts of a custom edge in React Flow are just React components. That means you can render anything you want along an edge! This guide shows you how to implement a custom edge with some additional controls. For a comprehensive reference of props available for custom edges, see the Edge reference.

A basic custom edge
An edge isn’t much use to us if it doesn’t render a path between two connected nodes. These paths are always SVG-based and are typically rendered using the <BaseEdge /> component. To calculate the actual SVG path to render, React Flow comes with some handy utility functions:

getBezierPath
getSimpleBezierPath
getSmoothStepPath
getStraightPath
To kickstart our custom edge, we’ll just render a straight path between the source and target.

import { BaseEdge, getStraightPath } from '@xyflow/react';
 
export function CustomEdge({ id, sourceX, sourceY, targetX, targetY }) {
  const [edgePath] = getStraightPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  });
 
  return (
    <>
      <BaseEdge id={id} path={edgePath} />
    </>
  );
}

Create the component
We start by creating a new React component called CustomEdge. Then we render the <BaseEdge /> component with the calculated path. This gives us a straight edge that behaves the same as the built-in default edge version "straight".

Create edgeTypes
Outside of our component, we define an edgeTypes object. We name our new edge type "custom-edge" and assign the CustomEdge component we just created to it.


const edgeTypes = {
  'custom-edge': CustomEdge,
};
Pass the edgeTypes prop
To use it, we also need to update the edgeTypes prop on the <ReactFlow /> component.


export function Flow() {
  return <ReactFlow edgeTypes={edgeTypes} />;
}
Use the new edge type
After defining the edgeTypes object, we can use our new custom edge by setting the type field of an edge to "custom-edge".


const initialEdges = [
  {
    id: 'e1',
    source: 'n1',
    target: 'n2',
    type: 'custom-edge',
  },
];

Custom SVG edge paths
As discussed previously, if you want to make a custom edge in React Flow, you have to use either of the four path creation functions discussed above (e.g getBezierPath). However if you want to make some other path shape like a Sinusoidal edge or some other edge type then you will have to make the edge path yourself.

The edge path we get from functions like getBezierPath is just a path string which we pass into the path prop of the <BaseEdge /> component. It contains the necessary information needed in order to draw that path, like where it should start from, where it should curve, where it should end, etc. A simple straight path string between two points (x1, y1) to (x2, y2) would look like:


M x1 y1 L x2 y2
An SVG path is a concatenated list of commands like M, L, Q, etc, along with their values. Some of these commands are listed below, along with their supported values.

M x1 y1 is the Move To command which moves the current point to the x1, y1 coordinate.
L x1 y1 is the Line To command which draws a line from the current point to x1, y1 coordinate.
Q x1 y1 x2 y2 is the Quadratic Bezier Curve command which draws a bezier curve from the current point to the x2, y2 coordinate. x1, y1 is the control point of the curve which determines the curviness of the curve.
Whenever we want to start a path for our custom edge, we use the M command to move our current point to sourceX, sourceY which we get as props in the custom edge component. Then based on the shape we want, we will use other commands like L(to make lines), Q(to make curves) and then finally end our path at targetX, targetY which we get as props in the custom edge component.

If you want to learn more about SVG paths, you can check out SVG-Path-Editor . You can paste any SVG path there and analyze individual path commands via an intuitive UI.

Here is an example with two types of custom edge paths, a Step edge and a Sinusoidal edge. You should look at the Step edge first to get your hands dirty with custom SVG paths since it’s simple, and then look at how the Sinusoidal edge is made. After going through this example, you will have the necessary knowledge to make custom SVG paths for your custom edges.


Utility Classes
React Flow provides several built-in utility CSS classes to help you fine-tune how interactions work within your custom elements.

nodrag
Adding the class nodrag to an element ensures that interacting with it doesn’t trigger a drag. This is particularly useful for elements like buttons or inputs that should not initiate a drag operation when clicked.

Nodes have a drag class name in place by default. However, this class name can affect the behaviour of the event listeners inside your custom nodes. To prevent unexpected behaviours, add a nodrag class name to elements with an event listener. This prevents the default drag behavior as well as the default node selection behavior when elements with this class are clicked.


export default function CustomNode(props: NodeProps) {
  return (
    <div>
      <input className="nodrag" type="range" min={0} max={100} />
    </div>
  );
}

nopan
If an element in the canvas does not stop mouse events from propagating, clicking and dragging that element will pan the viewport. Adding the “nopan” class prevents this behavior and this prop allows you to change the name of that class.


export default function CustomNode(props: NodeProps) {
  return (
    <div className="nopan">
      <p>fixed content...</p>
    </div>
  );
}

nowheel
If your custom element contains scrollable content, you can apply the nowheel class. This disables the canvas’ default pan behavior when you scroll inside your custom node, ensuring that only the content scrolls instead of moving the entire canvas.


export default function CustomNode(props: NodeProps) {
  return (
    <div className="nowheel" style={{ overflow: 'auto' }}>
      <p>Scrollable content...</p>
    </div>
  );
}

Applying these utility classes helps you control interaction on a granular level. You can customize these class names inside React Flow’s style props.


Theming
React Flow has been built with deep customization in mind. Many of our users fully transform the look and feel of React Flow to match their own brand or design system. This guide will introduce you to the different ways you can customize React Flow’s appearance.

Default styles
React Flow’s default styles are enough to get going with the built-in nodes. They provide some sensible defaults for styles like padding, border radius, and animated edges. You can see what they look like below:

import React, { useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Position,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';


const nodeDefaults = {
  sourcePosition: Position.Right,
  targetPosition: Position.Left,
};

const initialNodes = [
  {
    id: '1',
    position: { x: 0, y: 150 },
    data: { label: 'default style 1' },
    ...nodeDefaults,
  },
  {
    id: '2',
    position: { x: 250, y: 0 },
    data: { label: 'default style 2' },
    ...nodeDefaults,
  },
  {
    id: '3',
    position: { x: 250, y: 150 },
    data: { label: 'default style 3' },
    ...nodeDefaults,
  },
  {
    id: '4',
    position: { x: 250, y: 300 },
    data: { label: 'default style 4' },
    ...nodeDefaults,
  },
];

const initialEdges = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    animated: true,
  },
  {
    id: 'e1-3',
    source: '1',
    target: '3',
  },
  {
    id: 'e1-4',
    source: '1',
    target: '4',
  },
];

const Flow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params) => setEdges((els) => addEdge(params, els)),
    [],
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
    >
      <Background />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
};

export default Flow;


html,
body {
  margin: 0;
  font-family: sans-serif;
}

#app {
  width: 100vw;
  height: 100vh;
}


import { createRoot } from 'react-dom/client';
import App from './App';

import './index.css';

const container = document.querySelector('#app');
const root = createRoot(container);

root.render(<App />);

You’ll typically load these default styles by importing them in you App.jsx file or other entry point:


import '@xyflow/react/dist/style.css';
Without dipping into custom nodes and edges, there are three ways you can style React Flow’s basic look:

Passing inline styles through style props
Overriding the built-in classes with custom CSS
Overriding the CSS variables React Flow uses
Built in dark and light mode

Built in dark and light mode
You can choose one of the built-in color modes by using the colorMode prop (‘dark’, ‘light’ or ‘system’) as seen in the dark mode example.


import ReactFlow from '@xyflow/react';
 
export default function Flow() {
  return <ReactFlow colorMode="dark" nodes={[...]} edges={[...]} />
}
When you use the colorMode prop, React Flow adds a class to the root element (.react-flow) that you can use to style your flow based on the color mode:


.dark .react-flow__node {
  background: #777;
  color: white;
}
 
.light .react-flow__node {
  background: white;
  color: #111;
}
Customizing with style props
The easiest way to start customizing the look and feel of your flows is to use the style prop found on many of React Flow’s components to inline your own CSS.


import ReactFlow from '@xyflow/react'
 
const styles = {
  background: 'red',
  width: '100%',
  height: 300,
};
 
export default function Flow() {
  return <ReactFlow style={styles} nodes={[...]} edges={[...]} />
}
CSS variables
If you don’t want to replace the default styles entirely but just want to tweak the overall look and feel, you can override some of the CSS variables we use throughout the library. For an example of how to use these CSS variables, check out our Feature Overview example.

These variables are mostly self-explanatory. Below is a table of all the variables you might want to tweak and their default values for reference:
Variable name	Default
--xy-edge-stroke-default	#b1b1b7
--xy-edge-stroke-width-default	1
--xy-edge-stroke-selected-default	#555
--xy-connectionline-stroke-default	#b1b1b7
--xy-connectionline-stroke-width-default	1
--xy-attribution-background-color-default	rgba(255, 255, 255, 0.5)
--xy-minimap-background-color-default	#fff
--xy-background-pattern-dots-color-default	#91919a
--xy-background-pattern-line-color-default	#eee
--xy-background-pattern-cross-color-default	#e2e2e2
--xy-node-color-default	inherit
--xy-node-border-default	1px solid #1a192b
--xy-node-background-color-default	#fff
--xy-node-group-background-color-default	rgba(240, 240, 240, 0.25)
--xy-node-boxshadow-hover-default	0 1px 4px 1px rgba(0, 0, 0, 0.08)
--xy-node-boxshadow-selected-default	0 0 0 0.5px #1a192b
--xy-handle-background-color-default	#1a192b
--xy-handle-border-color-default	#fff
--xy-selection-background-color-default	rgba(0, 89, 220, 0.08)
--xy-selection-border-default	1px dotted rgba(0, 89, 220, 0.8)
--xy-controls-button-background-color-default	#fefefe
--xy-controls-button-background-color-hover-default	#f4f4f4
--xy-controls-button-color-default	inherit
--xy-controls-button-color-hover-default	inherit
--xy-controls-button-border-color-default	#eee
--xy-controls-box-shadow-default	0 0 2px 1px rgba(0, 0, 0, 0.08)
--xy-resize-background-color-default	#3367d9
These variables are used to define the defaults for the various elements of React Flow. This means they can still be overridden by inline styles or custom classes on a per-element basis. If you want to override these variables, you can do so by adding:


.react-flow {
  --xy-node-background-color-default: #ff5050;
}

Overriding built-in classes
Some consider heavy use of inline styles to be an anti-pattern. In that case, you can override the built-in classes that React Flow uses with your own CSS. There are many classes attached to all sorts of elements in React Flow, but the ones you’ll likely want to override are listed below:

Class name	Description
.react-flow	The outermost container
.react-flow__renderer	The inner container
.react-flow__zoompane	Zoom & pan pane
.react-flow__selectionpane	Selection pane
.react-flow__selection	User selection
.react-flow__edges	The element containing all edges in the flow
.react-flow__edge	Applied to each Edge in the flow
.react-flow__edge.selected	Added to an Edge when selected
.react-flow__edge.animated	Added to an Edge when its animated prop is true
.react-flow__edge.updating	Added to an Edge while it gets updated via onReconnect
.react-flow__edge-path	The SVG <path /> element of an Edge
.react-flow__edge-text	The SVG <text /> element of an Edge label
.react-flow__edge-textbg	The SVG <text /> element behind an Edge label
.react-flow__connection	Applied to the current connection line
.react-flow__connection-path	The SVG <path /> of a connection line
.react-flow__nodes	The element containing all nodes in the flow
.react-flow__node	Applied to each Node in the flow
.react-flow__node.selected	Added to a Node when selected.
.react-flow__node-default	Added when Node type is "default"
.react-flow__node-input	Added when Node type is "input"
.react-flow__node-output	Added when Node type is "output"
.react-flow__nodesselection	Nodes selection
.react-flow__nodesselection-rect	Nodes selection rect
.react-flow__handle	Applied to each <Handle /> component
.react-flow__handle-top	Applied when a handle’s Position is set to "top"
.react-flow__handle-right	Applied when a handle’s Position is set to "right"
.react-flow__handle-bottom	Applied when a handle’s Position is set to "bottom"
.react-flow__handle-left	Applied when a handle’s Position is set to "left"
.connectingfrom	Added to a Handle when a connection line is above a handle.
.connectingto	Added to a Handle when a connection line is above a handle.
.valid	Added to a Handle when a connection line is above and the connection is valid
.react-flow__background	Applied to the <Background /> component
.react-flow__minimap	Applied to the <MiniMap /> component
.react-flow__controls	Applied to the <Controls /> component