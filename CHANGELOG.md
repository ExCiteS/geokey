# GeoKey Changelog

## Version 0.8

- Requirements are updated, most notably to Django 1.8
- Search has been improved. Search index is now more flexible, it ignores order of terms searched.
- Removes `/api/projects/:project_id/get-in-touch` endpoint. Also, notifications settings are now completely removed from GeoKey, therefore `contact_admins` method is no longer available on the Project model.

## Version 0.7.2

- Bug fixes:
    - [#283](https://github.com/ExCiteS/geokey/issues/283) When deleting a review comment, the corresponding observation is only updated, when the status changes as well.
    - [#289](https://github.com/ExCiteS/geokey/issues/289) Adds error messages to user registration formats
    - [#290](https://github.com/ExCiteS/geokey/issues/290) Catches integrity errors when updating user profiles
- Further improvements to user authentication forms.

## Version 0.7.1

- Updates requirements to Django 1.7.10

## Version 0.7

- Adds `core.mixins`, that provide mixins for shared functionality, e.g. creating where clauses for user groups and subsets.
- Removes `/api/projects/:project_id/contributions/search` endpoint. Searching for contributions can now be implemented via `/api/projects/:project_id/contributions/search={query}`

- The following files have been moved or renamed:
    - `geokey/static/admin.usergroup.data.js` > `geokey/static/admin.filters.data.js`
    - `geokey/templates/users/data_fields_rules.html` > `geokey/templates/snippets/data_fields_rules.html`
    - `geokey/users/templatetags/tags.py` > `geokey/users/templatetags/filter_tags.py`

- Redesign of navigation elements
- Fixes performance issues with counting number of files and comments per observation. Values are stored with the observation and updated each time either comment or file is added or removed.
- Implements editing of lookup values
- Bug fixes:
    - [#279](https://github.com/ExCiteS/geokey/issues/279) Fixes validation of date fields; times before 10 a.m. used to cause an error.

## Version 0.6

- Separation of contribution serialiser into parser, serialiser and renderer. This enables rendering of geographic data into formats other than GeoJSON.
- Adds KML renderer for geopagice data
- Adds ENABLE_VIDEO flag in settings. If you do not plan to support video uploads set this to `false`.
- Adds number of comments and files to contributions serialisation.
- Removed data groupings; access to data is now regulated via filters attached to user groups.
- Fixes various bugs:

    - Fixed #253: If a file is upload, that is not an image or video the file will be shown as not found
    - Fixed #254: Redirect to originally requested page after logging in is working again
    - Fixed #255: Sets contribution status to ‘active' when response to a comment is changed from open to 'resolved'

#### This version requires additional packages:

To install run:

    ```
    sudo apt-get install binutils libproj-dev gdal-bin python-gdal
    ```

... and for virtual env also run these commands:

    ```
    sudo apt-get install libgdal-dev
    export C_INCLUDE_PATH=/usr/include/gdal
    export CPLUS_INCLUDE_PATH=/usr/include/gdal

    pip install gdal==1.9.0  # important to install the correct bindings for installed gdal, check with gdal-config --version
    ```
