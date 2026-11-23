# Energy Diagram Canvas Feature

## Overview

The Energy Diagram Canvas is a new feature that allows users to visualize and create energy system diagrams for different sites in their projects. It provides an interactive drag-and-drop interface for modeling energy systems with commodities, processes, storage, and transmission elements.

## Features

### 1. Interactive Map

- **Sites Display**: Shows all project sites on an interactive map using OpenStreetMap
- **Site Selection**: Click on any site marker to select it and open the energy diagram canvas
- **Transmission Visualization**: Displays transmission lines between sites as dotted orange lines

### 2. Energy System Canvas

- **Site Boundary**: Each site is represented by a dashed boundary box
- **Drag & Drop**: All elements can be dragged and repositioned on the canvas
- **Real-time Updates**: Changes are reflected immediately in the diagram

### 3. Element Types

#### Commodities (Blue Vertical Lines)

- Represent energy carriers (electricity, heat, gas, etc.)
- Displayed as vertical blue lines with labels
- Can be connected to processes and storage

#### Processes (Green Boxes)

- Represent energy conversion or transformation processes
- Displayed as horizontal green boxes
- Can have input and output connections to commodities
- Width can be adjusted in the properties panel

#### Storage (Purple Cylinders)

- Represent energy storage systems
- Displayed as purple cylindrical shapes
- Connected to commodities for storage/retrieval

#### Transmission (Orange Dotted Lines)

- Represent energy transmission between sites
- Displayed as dotted orange lines with arrows
- Show connections between different site commodities

### 4. Interactive Features

#### Adding Elements

- Use the toolbar buttons to add new commodities, processes, storage, or transmission elements
- New elements are automatically positioned and can be moved

#### Editing Elements

- Click on any element to select it
- Use the properties panel to edit element names and properties
- Process width can be adjusted for better visualization

#### Creating Connections

- Click and drag from one element to another to create connections
- Connection preview is shown while dragging
- Connections are automatically generated based on process input/output relationships

#### Deleting Elements

- Select an element and use the delete button to remove it
- All associated connections are automatically updated

### 5. Data Integration

- **Real Data**: Uses actual project data from the backend
- **Automatic Layout**: Elements are positioned based on existing site configuration
- **Live Updates**: Changes in the main configuration are reflected in the diagram

### 6. Export & Save

- **JSON Export**: Save diagram configuration as a downloadable JSON file
- **Configuration Persistence**: Diagram layout and connections are preserved
- **Backup**: Export diagrams for backup or sharing purposes

## Usage Instructions

### Accessing the Feature

1. Navigate to any project
2. Click on the "Energy Diagram" tab in the sidebar
3. The map will display all project sites

### Creating a Diagram

1. Click on a site marker on the map
2. Click "Open Energy Diagram" in the popup
3. The canvas will open with existing site elements
4. Use the toolbar to add new elements
5. Drag elements to reposition them
6. Create connections by dragging between elements

### Customizing the Diagram

1. Select any element to edit its properties
2. Use the properties panel to modify names and dimensions
3. Delete unwanted elements using the delete button
4. Reset the canvas to restore the original layout

### Saving Your Work

1. Click the "Save" button to export the diagram
2. A JSON file will be downloaded with your configuration
3. The file can be imported later or shared with team members

## Technical Details

### Frontend Technologies

- **Vue 3**: Component framework
- **Leaflet**: Interactive mapping
- **SVG**: Vector graphics for diagram elements
- **Tailwind CSS**: Styling and layout

### Data Structure

The diagram data is stored in a structured format:

```json
{
  "commodities": [...],
  "processes": [...],
  "storage": [...],
  "transmissions": [...],
  "connections": [...]
}
```

### Backend Integration

- Fetches real data from Django backend APIs
- Supports all existing energy system models
- Maintains data consistency with main application

## Future Enhancements

- **Backend Persistence**: Save diagrams to database
- **Collaborative Editing**: Real-time collaboration features
- **Advanced Layout**: Automatic layout algorithms
- **Simulation Integration**: Connect to energy simulation results
- **Export Formats**: PNG, SVG, PDF export options
- **Templates**: Pre-built diagram templates for common systems

## Troubleshooting

### Common Issues

1. **Elements not appearing**: Check if the site has commodities, processes, or storage configured
2. **Map not loading**: Ensure internet connection for OpenStreetMap tiles
3. **Drag and drop not working**: Make sure JavaScript is enabled and no console errors

### Performance Tips

- Limit the number of elements on large diagrams
- Use the reset button if the canvas becomes unresponsive
- Export and save work regularly

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.
