# -*- coding: utf-8 -*-"""Custom tools for esri ArcGIS Pro GIS software.https://github.com/rrudolph/pro-tools"""import arcpyfrom arcpy import metadata as mdfrom os import listdirfrom os.path import isfile, joinimport zipfilefrom pathlib import Pathfrom datetime import datetimeimport reimport subprocessfrom arcgis.gis import GISimport timeimport csv### Custom universal functionsdef msg(msg):    print(msg)    arcpy.AddMessage(msg)def get_alias_name(in_fc):    fc_alias = arcpy.Describe(in_fc).aliasName    if fc_alias:        return fc_alias    else:        return arcpy.Describe(in_fc).namedef strip_non_alphanum(string: str) -> re.sub:    """Remove any number of non alphanumeric characters and replace with an underscore"""    return re.sub('[^0-9a-zA-Z]+', '_', string)def zip_ws(path, zip_):    files = [f for f in listdir(path) if isfile(join(path, f))]    for file in files:        if not file.endswith('.lock'):            msg(f"Zipping {file}...")            try:                zip_.write(join(path, file), arcname=file)            except Exception as e:                msg(f"    Error adding {file}: {e}")### Main toolboxclass Toolbox(object):    def __init__(self):        """Define the toolbox (the name of the toolbox is the name of the        .pyt file)."""        self.label = "Toolbox"        self.alias = "toolbox"        # List of tool classes associated with this toolbox        self.tools = [ZipFeatureclass,            StripGPMetadata,            ExportMetadataGeopackage,            BackupService,            APRXDataLister,            PrintBoundingBox            ]class ZipFeatureclass(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "Zip Featureclass"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="Featureclass(s)",        name="fc",        datatype="DEFeatureClass",        parameterType="Required",        direction="Input",        multiValue=True)        param1 = arcpy.Parameter(        displayName="Output Directory",        name="out_dir",        datatype="DEFolder",        parameterType="Required",        direction="Input")        param2 = arcpy.Parameter(        displayName="Also remove geoprocessing history?",        name="rem_gp_hist",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        params = [param0, param1, param2]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        ## Set input vars        fcs = parameters[0].values        out_dir = parameters[1].valueAsText        remove_gp_hist = parameters[2].value        msg(f"fcs: {fcs}")        msg(f"out_dir: {out_dir}")        ## Time vars        now = datetime.now()        date_time = now.strftime("%Y_%m_%d_%H_%M_%S")                    ## Derived vars        ws_gdb_name = f"AppStream_Staging_{date_time}.gdb"        db = join(out_dir, ws_gdb_name)        out_zip = join(out_dir, f"{ws_gdb_name}.zip")        msg("Making db")        arcpy.management.CreateFileGDB(out_dir, ws_gdb_name, "CURRENT")        for fc in fcs:            fc_name = arcpy.Describe(fc).name            msg(f"fc name is {fc_name}")            out_fc = join(db, strip_non_alphanum(fc_name))            msg(f"Copying {fc} to {out_fc}")            arcpy.management.CopyFeatures(fc, out_fc, '', None, None, None)            if remove_gp_hist:                tgt_item_md = md.Metadata(out_fc)                # Delete all geoprocessing history from the item's metadata                if not tgt_item_md.isReadOnly:                    msg(f"  -Removing geoprocessing history")                    tgt_item_md.deleteContent('GPHISTORY')                    tgt_item_md.save()        msg("Zipping")        with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:            zip_ws(db, zip_file)        msg("Deleting db")        arcpy.management.Delete(db)        msg("Done")        return    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnclass StripGPMetadata(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "Strip GP Metadata"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="Featureclass(s)",        name="fcs",        datatype="DEFeatureClass",        parameterType="Required",        direction="Input",        multiValue=True)        param1 = arcpy.Parameter(        displayName="Remove enclosed files?",        name="rem_files",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param2 = arcpy.Parameter(        displayName="Remove thumbnail?",        name="rem_thumb",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        params = [param0, param1, param2]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        ## Set input vars        fcs = parameters[0].values        rem_files = parameters[1].value        rem_thumb = parameters[2].value        msg(f"fcs: {fcs}")        msg(f"rem_files: {rem_files}")        msg(f"rem_thumb: {rem_thumb}")        for fc in fcs:                msg(f"[+] Processing {fc}")            tgt_item_md = md.Metadata(fc)            # Delete all geoprocessing history from the item's metadata            if not tgt_item_md.isReadOnly:                msg(f"  -Removing geoprocessing history")                tgt_item_md.deleteContent('GPHISTORY')                if rem_thumb:                    msg(f"  -Removing thumbnail")                    tgt_item_md.deleteContent('THUMBNAIL')                if rem_files:                    msg(f"  -Removing enclosed files")                    tgt_item_md.deleteContent('ENCLOSED_FILES')                tgt_item_md.save()            else:                arcpy.AddWarning(f"[-] Metadata not altered. FC is read only")        msg("Done")    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnclass ExportMetadataGeopackage(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "Export Metadata or GeoPackage"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="Featureclass(s)",        name="fcs",        datatype="DEFeatureClass",        parameterType="Required",        direction="Input",        multiValue=True)        param1 = arcpy.Parameter(        displayName="Output Directory",        name="out_dir",        datatype="DEWorkspace",        parameterType="Required",        direction="Input")        param2 = arcpy.Parameter(        displayName="Export ISO19115_3 Metadata?",        name="export_iso",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param3 = arcpy.Parameter(        displayName="Export FGDC_CSDGM Metadata?",        name="export_fgdc",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param4 = arcpy.Parameter(        displayName="Convert FGDC to HTML?",        name="export_html",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param5 = arcpy.Parameter(        displayName="Export GeoPackage?",        name="export_geopackage",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param6 = arcpy.Parameter(        displayName="Export Shapefile?",        name="export_shapefile",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param7 = arcpy.Parameter(        displayName="Strip Whitespace from Filename?",        name="export_whitespace",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param7.value = True        params = [param0, param1, param2, param3, param4, param5, param6, param7]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        def generate_html(xml_file: str) -> None:            """            Convert FGDC xml metadata to html using the USGS mp tool.            https://geology.usgs.gov/tools/metadata/tools/doc/mp.html            """            out_html = xml_file.replace(".xml", ".html")            current_folder = Path(__file__).parent            current_folder = str(current_folder).replace("\\", "/")            cmd = f'"{current_folder}/tools/mp.exe" "{xml_file}" -h "{out_html}"'            returned_value = subprocess.call(cmd, shell=True)        def generate_xml(in_fc: str, metadata_type: str, strip_whitespace: bool) -> None:            """Export an xml file for the input featureclass with the specified metadata style"""            if metadata_type.upper() not in ["FGDC_CSDGM", "ISO19115_3", "ISO19139", "ISO19139_GML32"]:                raise ValueError(f"Metadata type '{metadata_type}' may be supported but is currently not a valid argument for this function.")            src_item_md = md.Metadata(in_fc)            fc_alias = get_alias_name(in_fc)            if strip_whitespace:                out_file = join(out_dir, f"{strip_non_alphanum(fc_alias)}_{metadata_type}.xml")            else:                out_file = join(out_dir, f"{fc_alias}_{metadata_type}.xml")            src_item_md.exportMetadata(out_file, metadata_type, 'REMOVE_ALL_SENSITIVE_INFO')            if metadata_type == 'FGDC_CSDGM':                if export_html:                    msg("Converting to html")                    generate_html(out_file)        def export_geopackage(in_fc):            fc_alias = strip_non_alphanum(get_alias_name(in_fc))            geopackage_name = f"{fc_alias}.gpkg"            msg("Making geopackage")            arcpy.management.CreateSQLiteDatabase(                out_database_name=join(out_dir, geopackage_name),                spatial_type="GEOPACKAGE"            )            msg("Exporting features")            arcpy.conversion.ExportFeatures(                in_features=fc,                out_features=join(out_dir, geopackage_name, fc_alias),                where_clause="",                use_field_alias_as_name="NOT_USE_ALIAS",                field_mapping=None,                sort_field=None            )        def export_shapefile(in_fc):            fc_alias = strip_non_alphanum(get_alias_name(in_fc))            shapfile_name = f"{fc_alias}.shp"            msg("Exporting shapfile")            arcpy.conversion.ExportFeatures(                in_features=fc,                out_features=join(out_dir, shapfile_name),                where_clause="",                use_field_alias_as_name="NOT_USE_ALIAS",                field_mapping=None,                sort_field=None            )        ## Set input vars        fcs = parameters[0].values        out_dir = parameters[1].valueAsText        export_iso = parameters[2].value        export_fgdc = parameters[3].value        export_html = parameters[4].value        export_geopackage_bool = parameters[5].value        export_shapefile_bool = parameters[6].value        strip_whitespace = parameters[7].value        msg(f"fcs: {fcs}")        msg(f"out_dir: {out_dir}")        msg(f"export_iso: {export_iso}")        msg(f"export_fgdc: {export_fgdc}")        msg(f"export_html: {export_html}")        msg(f"export_geopackage_bool: {export_geopackage_bool}")        msg(f"export_shapefile_bool: {export_shapefile_bool}")        msg(f"strip_whitespace: {strip_whitespace}")                for fc in fcs:            msg(f"fc: {fc}")            fc = arcpy.Describe(fc).catalogPath            msg(f"fc catalog path: {fc}")            if export_fgdc:                generate_xml(fc, "FGDC_CSDGM", strip_whitespace)            if export_iso:                generate_xml(fc, "ISO19115_3", strip_whitespace)            if export_geopackage_bool:                export_geopackage(fc)            if export_shapefile_bool:                export_shapefile(fc)    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnclass BackupService(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "Backup AGOL or Portal Service"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="Item IDs",        name="itemIDs",        datatype="GPString",        parameterType="Required",        direction="Input",        multiValue=True)        param1 = arcpy.Parameter(        displayName="Output Folder",        name="out_dir",        datatype="DEWorkspace",        parameterType="Optional",        direction="Input")        param2 = arcpy.Parameter(        displayName="Make Timestamp Folder",        name="make_datestamp",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        param3 = arcpy.Parameter(        displayName="Export Format",        name="export_type",        datatype="GPString",        parameterType="Required",        direction="Input")        param3.value = "File Geodatabase (Includes Attachments)"        param3.filter.type = "ValueList"        params = [param0, param1, param2, param3]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        parameters[3].filter.list = [            "File Geodatabase (Includes Attachments)",            "Shapefile (No attachments)",            "GeoJson (No attachments)",        ]        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        def get_export_type(val):            switcher = {            'File Geodatabase (Includes Attachments)': 'File Geodatabase',            'Shapefile (No attachments)'             : 'Shapefile',            'GeoJson (No attachments)'               : 'GeoJson'}            return switcher.get(val, False)         msg(f"Connecting to AGOL")        gis = GIS("pro")        ## Set input vars        item_ids = parameters[0].valueAsText.split(";")        backup_folder = parameters[1].valueAsText        make_datestamp = parameters[2].value        export_type = parameters[3].valueAsText        msg(f"item_ids: {item_ids}")        msg(f"backup_folder: {backup_folder}")        msg(f"make_datestamp: {make_datestamp}")        msg(f"export_type: {export_type}")        if make_datestamp:            timestamp = time.strftime('%Y%m%d')            backup_folder = join(backup_folder, timestamp)            if not os.path.isdir(backup_folder):                print(f"Making new folder {backup_folder}")                os.makedirs(backup_folder)        export_format = get_export_type(export_type)        msg(f"Input Item IDs: {', '.join(item_ids)}")        msg(f"Backup Folder: {backup_folder}")        msg(f"Export Type: {export_format}")        # Run backup on each item id        for item_id in item_ids:            data_item = gis.content.get(item_id)            data_title = strip_non_alphanum(data_item['title'])            msg(f"[+] Processing {data_title}")            temp_file = time.strftime(f"{data_title}_backup_%Y%m%d_%H%M")            msg(f"....Generatring temporary {export_format}: {temp_file}")            data_item.export(temp_file, export_format, parameters=None, wait=True)            exported_temp = gis.content.search(temp_file, item_type=export_format)            # ic(exported_file)            exported_file = gis.content.get(exported_temp[0].itemid)            username = exported_file['owner']            export_name = exported_file['name']            if export_format in ['File Geodatabase','Shapefile']:                new_export_name = export_name.replace('.zip', f'_{username}.zip')            elif export_format == 'GeoJson':                new_export_name = export_name.replace('.geojson', f'_{username}.geojson')            # ic(exported_file)            msg(f"....Downloading as {export_format}")            exported_file.download(save_path=backup_folder)            os.rename(join(backup_folder, export_name), join(backup_folder, new_export_name))            msg(f"....Removing {export_format} backup online") # No need to keep. Saves AGOL user account space.             exported_file.delete()            msg("....Download complete")        msg("Backup complete.")    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnclass APRXDataLister(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "APRX Project Data Lister"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="APRX File",        name="aprx",        datatype="GPString",        parameterType="Required",        direction="Input")        param1 = arcpy.Parameter(        displayName="Output CSV file",        name="out_csv",        datatype="GPString",        parameterType="Required",        direction="Input")        param2 = arcpy.Parameter(        displayName="Make Layout CSV?",        name="make_layout_csv",        datatype="GPBoolean",        parameterType="Optional",        direction="Input")        params = [param0, param1, param2]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        def does_path_exists(fc):            try:                return "True" if arcpy.Exists(fc) else "False"            except:                return "Path Exists Error"        def get_proj(fc):            try:                sr_name = arcpy.Describe(fc).spatialReference.name            except:                sr_name = "Spatial Reference Error"            return sr_name        def get_shape_type(fc):            try:                desc = arcpy.Describe(fc)                if desc.dataType == "RasterDataset":                    return "Raster"                elif desc.dataType == "FeatureClass":                    feature_type = arcpy.Describe(fc).shapeType                    return feature_type                else:                    return desc.dataType            except:                feature_type = "Type Error"            return feature_type        def get_source(layer):            if layer.supports("DATASOURCE"):                return layer.dataSource            else:                return "Data source not supported"        def get_def_query(layer):            if layer.supports("DEFINITIONQUERY"):                try:                    return layer.definitionQuery                except:                    return "Def query error"            else:                return "Def query not supported"        def make_mapframe_list(lyt):            map_list = []            for map_frame in lyt.listElements("MAPFRAME_ELEMENT"):                # Get the map object for the map frame                try:                    map_name = map_frame.map.name                    map_list.append(map_name)                except:                    map_list.append("Layout map error or no data")            return "; ".join(map_list)        ## Set input vars        aprx = parameters[0].valueAsText        outCSV = parameters[1].valueAsText        make_layout_csv = parameters[2].value        msg(aprx)        msg(outCSV)        p = arcpy.mp.ArcGISProject(aprx)        maps = p.listMaps()        error_count = 0        with open(outCSV, "w", newline='') as f:            w = csv.writer(f)            w.writerow(["aprx", "map_name", "layer_name", "data_path", "path_exists", "projection", "shape_type", "definition_query"])            for map_ in maps:                layers = map_.listLayers()                for layer in layers:                    try:                        msg("*"*50)                        msg(f"Processing {layer.name}...")                        fc_path = get_source(layer)                        path_exists = does_path_exists(fc_path)                        proj = get_proj(fc_path)                        shapeType = get_shape_type(fc_path)                        def_query = get_def_query(layer)                        row = [aprx, map_.name, layer.name, fc_path, path_exists, proj, shapeType, def_query]                        row_joined = " - ".join(row)                        msg("Writing to csv...")                        msg(row_joined)                        w.writerow(row)                    except:                        msg("Error writing row")                        row = ["Error", "Error", "Error", "Error", "Error", "Error", "Error", "Error"]                        w.writerow(row)                        error_count += 1        if make_layout_csv:            msg("Writing layouts...")            out_layout_csv = outCSV.replace(".csv", "_layouts.csv")            with open(out_layout_csv, "w", newline='') as f:                w = csv.writer(f)                w.writerow(["aprx", "layout_name", "map_frames", "page_height", "page_width", "page_units"])                for lyt in p.listLayouts():                    msg(f" ----------- {lyt.name} ({lyt.pageHeight} x {lyt.pageWidth} {lyt.pageUnits})")                    msg(f"Mapframes in layout: {make_mapframe_list(lyt)}")                    row = [aprx, lyt.name, make_mapframe_list(lyt), lyt.pageHeight, lyt.pageWidth, lyt.pageUnits]                    w.writerow(row)        msg(f"Row errors: {error_count}")        msg("Done.")        return    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnclass PrintBoundingBox(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "Print Bounding Box"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        """Define parameter definitions"""                param0 = arcpy.Parameter(        displayName="Featureclass(s)",        name="fc",        datatype="DEFeatureClass",        parameterType="Required",        direction="Input",        multiValue=True)        param1 = arcpy.Parameter(        displayName="Precision (decimal places)",        name="precision",        datatype="GPString",        parameterType="Required",        direction="Input")        param1.value = "4"        params = [param0, param1]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        ## Set input vars        fcs = parameters[0].values        precision_input = parameters[1].value        precision = f".{precision_input}f"        for fc in fcs:            msg(f"[+] Bounding box for: {fc}")            # NAD_1983_UTM_Zone_10N: 26910            # GCS_WGS_1984: 4326            sr = arcpy.SpatialReference(4326)            desc = arcpy.Describe(fc)            extent = desc.extent.projectAs(sr)            msg(f"""West: {extent.XMin:{precision}}East: {extent.XMax:{precision}}South: {extent.YMin:{precision}}North: {extent.YMax:{precision}}"""            )        return    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        return