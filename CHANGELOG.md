# GeoKey Changelog

## Version 0.6

- Introduced KML Renderer, requires additional packages.

    To install run:

    ```
    sudo apt-get install binutils libproj-dev gdal-bin python-gdal gdal-bin
    ```

    For virtual env:

    ```
    sudo apt-get install libgdal-dev
    export C_INCLUDE_PATH=/usr/include/gdal
    export CPLUS_INCLUDE_PATH=/usr/include/gdal

    pip install gdal==1.9.0  # important to install the correct bindings for installed gdal, check with gdal-config --version
    ```
