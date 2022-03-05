import traceback

import napari
import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QTableView, QVBoxLayout, QWidget

import logging
from myLogger import get_logger
#logger = get_logger(__name__)
logger = get_logger('myLogger', level=logging.DEBUG)

#from .table_models import DataTableModel
from table_models import DataTableModel

# this is different for git commit -p

class QtPropertiesTable(QWidget):
    """The QWdiget containing the properties table and
    a combobox for selecting a layer

    Parameters
    ----------
    viewer : napari.viewer.Viewer
        The parent napari viewer

    Attributes
    ----------


    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()

        self.viewer = viewer

        #self.layer = None
        #""" the selected layer"""

        # create the table widget
        self.table = QTableView()

        # Create a combobox for selecting layers
        self.layer_combo_box = QComboBox(self)
        
        self.selected_layer = None
        """napari.layers.points.points.Points"""
        
        self.layer_combo_box.currentIndexChanged.connect(
            self.on_layer_selection
        )  # noqa
        self.initialize_layer_combobox()

        self.viewer.layers.events.inserted.connect(self.on_add_layer)
        self.viewer.layers.events.removed.connect(self.on_remove_layer)
        self.viewer.layers.selection.events.changed.connect(
            self.on_select_layer
        )  # noqa

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.layer_combo_box)
        self.vbox_layout.addWidget(self.table)

        self.setLayout(self.vbox_layout)

    def initialize_layer_combobox(self):
        """Populates the combobox with all layers that have data"""
        points_layers = [
            layer
            for layer in self.viewer.layers
            if self._is_points_layer(layer)  # noqa
        ]

        if len(points_layers) > 0:
            for pointLayer in points_layers:
                self.layer_combo_box.addItem(pointLayer.name)

            # select the first point layer
            if self.selected_layer is None:
                self.selected_layer = points_layers[0]

            index = self.layer_combo_box.findText(
                self.selected_layer.name, Qt.MatchExactly
            )  # noqa

            self.layer_combo_box.setCurrentIndex(index)

    def on_add_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is added to the viewer LayerList.
        """
        logger.info(f"{type(event)} {event}")
        layer_name = event.value.name
        layer = self.viewer.layers[layer_name]
        # if hasattr(layer, "data"):
        if self._is_points_layer(layer):
            print("  updating combo box")
            self.layer_combo_box.addItem(layer_name)

    def on_select_layer(self, event):
        """
        We just need to check type and move forward
        
        Args:
            event (multiple types): not described in napari documentation
            see: https://napari.org/docs/dev/guides/events_reference.html
            
        """
        logger.warning(f'Event type: {type(event)} type is: {event.type}')
        activeLayer = self.viewer.layers.selection.active
        print(f'  viewer.layers.selection.active: {type(activeLayer)} {activeLayer}')
        #print(f'  event.data: {event.data}')
        print(f'  event.source: {event.source}')
        print(f"  event.added: {event.added}")  # sometimes a dict ???
        print(f'{traceback.print_stack()}')

        # return if event.added is empty
        if not event.added:
            print(f'  no event.added ... returning')
            return
        
        # get first element of set event.added
        #for item in event.added:
        #    print('xxx', item)
        layer = next(iter(event.added))

        print(f'  layer: {layer}')

        if self._is_points_layer(layer):
            self.table_model = DataTableModel(layer.data)
            self.table.setModel(self.table_model)

            # connect the events
            if self.selected_layer is not None:
                self._disconnect_layer_events(self.selected_layer)
            self._connect_layer_events(layer)
            # self.table_model.dataChanged.connect(self._on_cell_edit)
            self.selected_layer = layer

            # select in combo box
            index = self.layer_combo_box.findText(layer.name, Qt.MatchExactly)
            if index != -1:
                self.layer_combo_box.setCurrentIndex(index)
            else:
                logger.error(f'did not find layer name "{layer.name}" in combo box with xxx')

    def on_layer_selection(self, index: int):
        """Callback function that updates the table when a
        new layer is selected in the combobox.
        """
        logger.warning(f'index: {index}')
        if index != -1:
            layer_name = self.layer_combo_box.itemText(index)
            selected_layer = self.viewer.layers[layer_name]
            print(f"  selected_layer: {type(selected_layer)} {selected_layer}")
            print(f"  selected_layer.data: {selected_layer.data}")
            # if hasattr(selected_layer, "data"):
            if self._is_points_layer(selected_layer):
                self.table_model = DataTableModel(selected_layer.data)
                self.table.setModel(self.table_model)

                # connect the events
                if self.selected_layer is not None:
                    self._disconnect_layer_events(self.selected_layer)
                self._connect_layer_events(selected_layer)
                # self.table_model.dataChanged.connect(self._on_cell_edit)
                self.selected_layer = selected_layer
            #else:
            #    print("no properties")
        else:
            self.table_model = DataTableModel(np.ndarray([]))
            self.table.setModel(self.table_model)

    def on_remove_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is removed from the viewer LayerList.
        """
        logger.warning('')
        print(f'  {type(event)}')
        print(f'  event.value: {event.value}')
        print(f'  removing layer name: {event.value.name}')

        layer_name = event.value.name
        index = self.layer_combo_box.findText(layer_name, Qt.MatchExactly)
        # findText returns -1 if the item isn't in the ComboBox
        # if it is in the ComboBox, remove it
        if index != -1:
            print("  updating combo box")
            self.layer_combo_box.removeItem(index)

            # get the new layer selection
            index = self.layer_combo_box.currentIndex()
            combo_box_layer_name = self.layer_combo_box.itemText(index)  # can be ''
            if combo_box_layer_name and combo_box_layer_name != self.selected_layer.name:
                #self.selected_layer = layer_name
                self.selected_layer = self.viewer.layers[combo_box_layer_name]

    def update_table(self, event):
        """Callback function that updates the table when the
        selected layer properties are updated. This is connected
        to the layer.events.properties event.
        """
        logger.warning(f'event type: {type(event)}')
        selected_layer = self.viewer.layers[self.selected_layer]
        self.table_model = DataTableModel(selected_layer.data)
        self.table.setModel(self.table_model)
        # self.table_model.dataChanged.connect(self._on_cell_edit)

    def _connect_layer_events(self, layer):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer_name : str
            The name of the layer to connect the update_table
            method to.
        """
        #layer = self.viewer.layers[layer_name]
        layer.events.properties.connect(self.update_table)

    '''
    def _connect_layer_events_for_layer(self, layer):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer : napari layer
            The layer to connect the update_table method to.
        """
        layer.events.properties.connect(self.update_table)
    '''

    def _disconnect_layer_events(self, layer):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer : napari layer
            The layer to disconnect the update_table
        """
        layer.events.data.disconnect(self.update_table)

    '''
    def _disconnect_layer_events_for_layer(self, layer):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer : napari layer
            The layer to disconnect the update_table from
        """
        layer.events.data.disconnect(self.update_table)
    '''

    def _is_points_layer(self, layer):
        """
        Determine if a layer is a point layer
        
        Args:
            layer (union(xxx,yyy,zzz):
                - sometimes a set?
        """

        isPointsLayer = isinstance(layer, napari.layers.points.points.Points)
        #isShapeLayer = isinstance(layer, napari.layers.points.points.Points)
        #isImageLayer = isinstance(layer, napari.layers.image.image.Image)
        
        '''
        # this works
        if not isPointsLayer:
            logger.warning(f'expecting layer of type "napari.layers.points.points.Points"')
            logger.warning(f'  got layer type of {type(layer)}')
            logger.warning(f'  with print value: {layer}')
            logger.warning(f'  traceback is:')
            print(f'{traceback.print_stack()}')
        '''

        # we can't assume a points layer has shape[1] == 3
        #return layer.data.shape[1] == 3
        return isPointsLayer

    # def _on_cell_edit(self, event):
    #     """Update the connected layer's properties when a cell
    #     has been edited"""
    #     if self.selected_layer is not None:
    #         layer = self.viewer.layers[self.selected_layer]
    #         with layer.events.properties.blocker():
    #             layer.properties = self.table_model._data
    #             if type(layer).__name__ in ['Points', 'Shapes']:
    #                 # force a color refresh
    #                 layer.refresh_colors()
