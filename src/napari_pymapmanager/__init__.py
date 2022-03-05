try:
    from ._version import version as __version__

    # from ._reader import napari_get_reader
except ImportError:
    __version__ = "unknown"
