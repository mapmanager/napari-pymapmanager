
import numpy as np
import napari
import tifffile

from _widget import QtPropertiesTable

def run():
    """
        - create a napari viewer
        - populate with an image, and two layers
        - run our plugin
    """
    print('run()')

    #
    # # open a napari viwer
    viewer = napari.Viewer()

    # add a tif image layer
    tifPath = '/media/cudmore/data/richard/rr30a/naked-tif/rr30a_s0_ch2.tif'    
    image = tifffile.imread(tifPath)
    print('image is', image.shape, image.dtype)


    #print(viewer.dims.indices)
    print('viewer.dims.point:', viewer.dims.point)
    print('viewer.dims.order:', viewer.dims.order)

    imageLayer = viewer.add_image(image, colormap='green', blending='additive')

    # make 2x point layer with some fake points
    zSlice = 0
    points1 = np.array([[zSlice, 100, 100], [zSlice, 200, 200], [zSlice, 300, 300], [zSlice, 400, 400]])
    pointsLayer1 = viewer.add_points(points1, 
                        size=30, face_color='green', name='My Points 1')
    pointsLayer1.mode = 'select'


    points2 = np.array([[zSlice, 420, 420], [zSlice, 500, 500], [zSlice, 600, 600], [zSlice, 600, 600]])
    pointsLayer2 = viewer.add_points(points2, 
                        size=30, face_color='magenta', name='My Points 2')
    #pointsLayer2.mode = 'select'

    # change the layer point symbol using an alias
    pointsLayer2.symbol = '+'

    # change the layer point out_of_slice_display status
    pointsLayer2.out_of_slice_display = True

    #aMyInterface = myInterface(viewer, pointsLayer)

    # run our plugin (not sure how to do this)
    myPlugin = QtPropertiesTable(viewer)
    #myPlugin.show()  # TODO: shows outside napari ???
    viewer.window.add_dock_widget(myPlugin)

    #
    # enter an event loop to receive user input
    napari.run()

if __name__ == '__main__':
    run()
