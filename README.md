# pro-tools
Custom Python tools for esri ArcGIS Pro software.

## Contents

- [Backup AGOL Services Tool](#AGOL-Services-Tool)
- [APRX Data Lister Tool](#APRX-Data-Lister-Tool)
- [Export GeoPackage Tool](#APRX-Data-Lister-Tool)
- [Geoprocessing Metadata Stripper Tool](#Geoprocessing-Metadata-Stripper-Tool)
- [Zip Featureclasses for AppStream](#Zip-Featureclasses-for-AppStream)

## Backup AGOL Services Tool

### Purpose
Package an ArcGIS Online or Portal feature service as a zipped file geodatabase with a time stamp and username in the filename. It can also export as a shp or geojson file. The file is temporarily staged on the user's AGOL contents but is removed once downloaded. 

### To Use
Enter one more Item ID's into the input parameters of the toolbox. The URL of your service in AGOL will look something like this <br>
https://nps.maps.arcgis.com/home/item.html?id=b115ada92f0c4b7cb91ee166a6165ca2

Use the item ID (b115ada92f0c4b7cb91ee166a6165ca2) of the feature service as input. Each service entered will have its own zip file generated in the output folder. <br>
![Backup Tool Screenshot](img/backup_tool_screenshot.png?raw=true "Backup Tool Screenshot")

You must be signed into AGOL (or Portal) through Pro to have access to the Item IDs entered into the tool. 

If you regularly enter the same item IDs and output folder, you can enter them as defaults.  To do that, right click on the tool in the Catalog Pane in Pro and go to the tool Properties. Under the Parameters section, enter item IDs separated by a semicolon with no spaces in between. Paste in the catalog path into the Output Folder default. <br>

Example default parameters:<br>
![Default params screenshot](img/backup_defaults.png?raw=true "Backup Tool Defaults")

Example tool output messages:<br>
![Messages screenshot](img/backup_output_messages.png?raw=true "Backup Tool Defaults")

Example tool file output:<br>
![File output](img/backup_output_files.png?raw=true "Backup Tool File Output")


<hr>

## APRX Data Lister Tool

### Purpose
Walk all maps in an ArcGIS Pro .aprx file and export to csv the layer names, layer data sources, projection, and other useful info about all layers in all maps. Since the exact file path of layers in ArcGIS Pro project is not always apparent or easy to view in the context of the entire map frame, this tool is useful for inspecting an .aprx file with a wide range of data sources.

### To Use
Open tool in ArcGIS Pro. Drag and drop aprx from windows file explorer.  Output needs full path plus ".csv" extension. <br>

Example screenshot of input parameters: <br>
<img src="img/aprx_lister_screenshot.JPG" width="300">


Example screenshot of tool running with output messages:<br>
<img src="img/aprx_lister_messages.JPG" width="400">

Example csv output. This allows for inspection of broken links or where layers point to data on disk:<br>
<img src="img/aprx_lister_output.JPG">

<hr>

## Export GeoPackage Tool

### Purpose
Exports one or more featureclasses or shapefiles as a [GeoPackage](https://www.esri.com/arcgis-blog/products/product/data-management/how-to-use-ogc-geopackages-in-arcgis-pro/) file format using the same name as the input featureclass or shapefile.

### To Use
Open tool in ArcGIS Pro. Drag and drop features from catalog window. Accepts multiple files. Toggle export metadata option if needed.

<hr>

## Geoprocessing Metadata Stripper Tool

### Purpose
Esri defaults to keeping geoprocessing metadata with the file even when exported, which may have sensitive data like file paths and other geoprocessing items. This tool strips geoprocessing metadata from one or more featureclass or shapefiles. Removes GPHISTORY as described in the deleteContent section of the [online reference](https://pro.arcgis.com/en/pro-app/latest/arcpy/metadata/metadata-class.htm). Optionally deletes THUMBNAIL, and ENCLOSED_FILES.

### To Use
Open tool in ArcGIS Pro. Drag and drop features from catalog window. Accepts multiple files. Toggle thumbnail and enclosed files options if needed. <br>

Example GP Strip tool interface:<br>
<img src="img/strip_gp_metadata.png" width="300">

Example GP Strip tool output:<br>
<img src="img/strip_gp_metadata_results.png" width="300">

## Zip Featureclasses for AppStream
### Purpose
Zip one or more featureclasses into a time-stamped zip file that contains a geodatabase.  Makes it easy to package up data for transfer to AppStream, since that can only be typically done through the web interface.

### To Use
Open tool in ArcGIS Pro. Drag and drop features from catalog window. Accepts multiple files. Specify an output folder.  Output folder will look something like  `AppStream_Staging_2023_08_14_17_28_53.gdb.zip`<br>