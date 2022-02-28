import napari
import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QComboBox, QTableView, QVBoxLayout, QWidget

from .table_models import DataTableModel


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

        # create the table widget
        self.table = QTableView()

        # Create a combobox for selecting layers
        self.layer_combo_box = QComboBox(self)
        self.selected_layer = None
        self.layer_combo_box.currentIndexChanged.connect(
            self.on_layer_selection
        )  # noqa
        self.initialize_layer_combobox()

        self.viewer.layers.events.inserted.connect(self.on_add_layer)
        self.viewer.layers.events.removed.connect(self.on_remove_layer)

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.layer_combo_box)
        self.vbox_layout.addWidget(self.table)

        self.setLayout(self.vbox_layout)

    def initialize_layer_combobox(self):
        """Populates the combobox with all layers that have data"""
        points_layers_names = [
            layer.name
            for layer in self.viewer.layers
            # if hasattr(layer, "data")
            if self._is_points_layer(layer)  # noqa
        ]

        print(f"points_layers_names: {points_layers_names}")

        if len(points_layers_names) > 0:
            self.layer_combo_box.addItems(points_layers_names)

            if self.selected_layer is None:
                self.selected_layer = points_layers_names[0]
            index = self.layer_combo_box.findText(
                self.selected_layer, Qt.MatchExactly
            )  # noqa
            self.layer_combo_box.setCurrentIndex(index)

    def on_add_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is added to the viewer LayerList.
        """
        layer_name = event.value.name
        print(f"adding layer {layer_name}")
        layer = self.viewer.layers[layer_name]
        # if hasattr(layer, "data"):
        if self._is_points_layer(layer):
            print("updating combo box")
            self.layer_combo_box.addItem(layer_name)

    def on_remove_layer(self, event):
        """Callback function that updates the layer list combobox
        when a layer is removed from the viewer LayerList.
        """
        layer_name = event.value.name
        print(f"removing layer {layer_name}")

        index = self.layer_combo_box.findText(layer_name, Qt.MatchExactly)
        # findText returns -1 if the item isn't in the ComboBox
        # if it is in the ComboBox, remove it
        if index != -1:
            print("updating combo box")
            self.layer_combo_box.removeItem(index)

            # get the new layer selection
            index = self.layer_combo_box.currentIndex()
            layer_name = self.layer_combo_box.itemText(index)
            if layer_name != self.selected_layer:
                self.selected_layer = layer_name

    def on_layer_selection(self, index: int):
        """Callback function that updates the table when a
        new layer is selected in the combobox.
        """
        if index != -1:
            layer_name = self.layer_combo_box.itemText(index)
            selected_layer = self.viewer.layers[layer_name]
            print(f"selected_layer.data: {selected_layer.data}")
            # if hasattr(selected_layer, "data"):
            if self._is_points_layer(selected_layer):
                self.table_model = DataTableModel(selected_layer.data)
                self.table.setModel(self.table_model)

                # connect the events
                if self.selected_layer is not None:
                    self._disconnect_layer_events(self.selected_layer)
                self._connect_layer_events(layer_name)
                # self.table_model.dataChanged.connect(self._on_cell_edit)
                self.selected_layer = layer_name
            else:
                print("no properties")
        else:
            self.table_model = DataTableModel(np.ndarray())
            self.table.setModel(self.table_model)

    def update_table(self, event):
        """Callback function that updates the table when the
        selected layer properties are updated. This is connected
        to the layer.events.properties event.
        """
        selected_layer = self.viewer.layers[self.selected_layer]
        self.table_model = DataTableModel(selected_layer.data)
        self.table.setModel(self.table_model)
        # self.table_model.dataChanged.connect(self._on_cell_edit)

    def _connect_layer_events(self, layer_name: str):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer_name : str
            The name of the layer to connect the update_table
            method to.
        """
        layer = self.viewer.layers[layer_name]
        layer.events.properties.connect(self.update_table)

    def _disconnect_layer_events(self, layer_name: str):
        """Connect the selected layer's properties events to
        table the update function.

        Parameters
        ----------
        layer_name : str
            The name of the layer to disconnect the update_table
            from
        """
        layer = self.viewer.layers[layer_name]
        layer.events.data.disconnect(self.update_table)

    def _is_points_layer(self, layer):
        return layer.data.shape[1] == 3

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
