/*
A KBase module: NarrativeService
*/

module NarrativeService {

    /* @range [0,1] */
    typedef int boolean;

    /*
        A time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
        character Z (representing the UTC timezone) or the difference
        in time to UTC in the format +/-HHMM, eg:
            2012-12-17T23:24:06-0500 (EST time)
            2013-04-03T08:56:32+0000 (UTC time)
            2013-04-03T08:56:32Z (UTC time)
    */
    typedef string timestamp;

    /* Represents the permissions a user or users have to a workspace:

        'a' - administrator. All operations allowed.
        'w' - read/write.
        'r' - read.
        'n' - no permissions.
    */
    typedef string permission;

    /* The lock status of a workspace.
        One of 'unlocked', 'locked', or 'published'.
    */
    typedef string lock_status;

    /* Information about an object, including user provided metadata.

        obj_id objid - the numerical id of the object.
        obj_name name - the name of the object.
        type_string type - the type of the object.
        timestamp save_date - the save date of the object.
        obj_ver ver - the version of the object.
        username saved_by - the user that saved or copied the object.
        ws_id wsid - the workspace containing the object.
        ws_name workspace - the workspace containing the object.
        string chsum - the md5 checksum of the object.
        int size - the size of the object in bytes.
        usermeta meta - arbitrary user-supplied metadata about
            the object.
    */
    typedef tuple<int objid, string name, string type,
        timestamp save_date, int version, string saved_by,
        int wsid, string workspace, string chsum, int size,
        mapping<string, string> meta> object_info;

    /* Information about a workspace.

        ws_id id - the numerical ID of the workspace.
        ws_name workspace - name of the workspace.
        username owner - name of the user who owns (e.g. created) this workspace.
        timestamp moddate - date when the workspace was last modified.
        int max_objid - the maximum object ID appearing in this workspace.
            Since cloning a workspace preserves object IDs, this number may be
            greater than the number of objects in a newly cloned workspace.
        permission user_permission - permissions for the authenticated user of
            this workspace.
        permission globalread - whether this workspace is globally readable.
        lock_status lockstat - the status of the workspace lock.
        usermeta metadata - arbitrary user-supplied metadata about
            the workspace.

    */
    typedef tuple<int id, string workspace, string owner, string moddate,
        int max_objid, string user_permission, string globalread,
        string lockstat, mapping<string, string> metadata> workspace_info;

    typedef structure {
        list<object_info> set_items_info;
    } SetItems;

    /*
        ref - reference to any DataPalette container pointing to given object,
        refs - list of references to all DataPalette containers pointing to
            given object.
    */
    typedef structure {
        string ref;
        list<string> refs;
    } DataPaletteInfo;

    /*
        object_info - workspace info for object (including set object),
        set_items - optional property listing info for items of set object,
        dp_info - optional data-palette info (defined for items stored in
            DataPalette object).
    */
    typedef structure {
        object_info object_info;
        SetItems set_items;
        DataPaletteInfo dp_info;
    } ListItem;

    /*
        ws_name/ws_id/workspaces - alternative way of defining workspaces (in
            case of 'workspaces' each string could be workspace name or ID
            converted into string).
        types - optional filter field, limiting output list to set of types.
        includeMetadata - if 1, includes object metadata, if 0, does not. Default 0.
        include_data_palettes - if 1, includes data palette info, if 0, does not. Default 0.
    */
    typedef structure {
        string ws_name;
        int ws_id;
        list<string> workspaces;
        list<string> types;
        boolean includeMetadata;
        boolean include_data_palettes;
    } ListObjectsWithSetsParams;

    /*
        data_palette_refs - mapping from workspace Id to reference to DataPalette
            container existing in given workspace. Not present if include_data_palettes is 0
            in the input parameters.
    */
    typedef structure {
        list<ListItem> data;
        mapping<string ws_text_id, string ws_ref> data_palette_refs;
    } ListObjectsWithSetsOutput;

    funcdef list_objects_with_sets(ListObjectsWithSetsParams params)
        returns (ListObjectsWithSetsOutput) authentication required;

    /*
        workspaceId - optional workspace ID, if not specified then
            property from workspaceRef object info is used.
    */
    typedef structure {
        string workspaceRef;
        int workspaceId;
        string newName;
    } CopyNarrativeParams;

    typedef structure {
        int newWsId;
        int newNarId;
    } CopyNarrativeOutput;

    funcdef copy_narrative(CopyNarrativeParams params)
        returns (CopyNarrativeOutput) authentication required;


    /* Restructured workspace object info 'data' tuple:
        id: data[0],
        name: data[1],
        type: data[2],
        save_date: data[3],
        version: data[4],
        saved_by: data[5],
        wsid: data[6],
        ws: data[7],
        checksum: data[8],
        size: data[9],
        metadata: data[10],
        ref: data[6] + '/' + data[0] + '/' + data[4],
        obj_id: 'ws.' + data[6] + '.obj.' + data[0],
        typeModule: type[0],
        typeName: type[1],
        typeMajorVersion: type[2],
        typeMinorVersion: type[3],
        saveDateMs: ServiceUtils.iso8601ToMillisSinceEpoch(data[3])
    */
    typedef structure {
        int id;
        string name;
        string type;
        string save_date;
        int version;
        string saved_by;
        int wsid;
        string ws;
        string checksum;
        int size;
        mapping<string,string> metadata;
        string ref;
        string obj_id;
        string typeModule;
        string typeName;
        string typeMajorVersion;
        string typeMinorVersion;
        int saveDateMs;
    } ObjectInfo;

    /* Restructured workspace info 'wsInfo' tuple:
        id: wsInfo[0],
        name: wsInfo[1],
        owner: wsInfo[2],
        moddate: wsInfo[3],
        object_count: wsInfo[4],
        user_permission: wsInfo[5],
        globalread: wsInfo[6],
        lockstat: wsInfo[7],
        metadata: wsInfo[8],
        modDateMs: ServiceUtils.iso8601ToMillisSinceEpoch(wsInfo[3])
    */
    typedef structure {
        int id;
        string name;
        string owner;
        timestamp moddate;
        int object_count;
        permission user_permission;
        permission globalread;
        lock_status lockstat;
        mapping<string,string> metadata;
        int modDateMs;
    } WorkspaceInfo;

    typedef tuple<int step_pos, string key, string value> AppParam;

    /*
        app - name of app (optional, either app or method may be defined)
        method - name of method (optional, either app or method may be defined)
        appparam - parameters of app/method packed into string in format:
            "step_pos,param_name,param_value(;...)*" (alternative to appData)
        appData - parameters of app/method in unpacked form (alternative to appparam)
        markdown - markdown text for cell of 'markdown' type (optional)
        copydata - packed import data in format "import(;...)*" (alternative to importData)
        importData - import data in unpacked form (alternative to copydata)
        includeIntroCell - if 1, adds an introductory markdown cell at the top (optional, default 0)
        title - name of the new narrative (optional, if a string besides 'Untitled', this will
                mark the narrative as not temporary, so it will appear in the dashboard)
    */
    typedef structure {
        string app;
        string method;
        string appparam;
        list<AppParam> appData;
        string markdown;
        string copydata;
        list<string> importData;
        boolean includeIntroCell;
        string title;
    } CreateNewNarrativeParams;

    typedef structure {
        WorkspaceInfo workspaceInfo;
        ObjectInfo narrativeInfo;
    } CreateNewNarrativeOutput;

    funcdef create_new_narrative(CreateNewNarrativeParams params)
        returns (CreateNewNarrativeOutput) authentication required;


    /*
        ref - workspace reference to source object,
        target_ws_id/target_ws_name - alternative ways to define target workspace,
        target_name - optional target object name (if not set then source object
            name is used).
    */
    typedef structure {
        string ref;
        int target_ws_id;
        string target_ws_name;
        string target_name;
    } CopyObjectParams;

    /*
        info - workspace info of created object
    */
    typedef structure {
        ObjectInfo info;
    } CopyObjectOutput;

    funcdef copy_object(CopyObjectParams params)
        returns (CopyObjectOutput) authentication required;


    /*
        workspaces - list of items where each one is workspace name of textual ID.
    */
    typedef structure {
        list<string> workspaces;
    } ListAvailableTypesParams;

    /*
        type_stat - number of objects by type
    */
    typedef structure {
        mapping<string, int> type_stat;
    } ListAvailableTypesOutput;

    funcdef list_available_types(ListAvailableTypesParams params)
        returns (ListAvailableTypesOutput) authentication required;




    /* ********************************** */
    /* Listing Narratives / Naratorials (plus Narratorial Management) */

    typedef structure { } ListNarratorialParams;

    /* info for a narratorial */
    typedef structure {
        workspace_info ws;
        object_info nar;
    } Narratorial;

    typedef structure {
        list <Narratorial> narratorials;
    } NarratorialList;

    funcdef list_narratorials(ListNarratorialParams params)
        returns (NarratorialList) authentication optional;




    typedef structure {
        workspace_info ws;
        object_info nar;
    } Narrative;

    typedef structure {
        list <Narrative> narratives;
    } NarrativeList;

    /* List narratives
        type parameter indicates which narratives to return.
        Supported options are for now 'mine', 'public', or 'shared'
    */
    typedef structure {
        string type;
    } ListNarrativeParams;

    funcdef list_narratives(ListNarrativeParams params)
        returns (NarrativeList) authentication optional;


    /*
        ws field is a string, but properly interpreted whether it is a workspace
        name or ID
    */
    typedef structure {
        string ws;
        string description;
    } SetNarratorialParams;

    typedef structure { } SetNarratorialResult;

    /*
        Allows a user to create a Narratorial given a WS they own. Right now
        anyone can do this, but we may restrict in the future to users that
        have a particular role.  Run simply as:
            ns.set_narratorial({'ws':'MyWsName'}) or,
            ns.set_narratorial({'ws':'4231'})
    */
    funcdef set_narratorial(SetNarratorialParams params)
        returns (SetNarratorialResult) authentication required;

    typedef structure {
        string ws;
    } RemoveNarratorialParams;

    typedef structure { } RemoveNarratorialResult;

    funcdef remove_narratorial(RemoveNarratorialParams params)
        returns (RemoveNarratorialResult) authentication required;

    /*
        This first version only takes a single UPA as input and attempts to find the report that made it.
    */
    typedef structure {
        string upa;
    } FindObjectReportParams;

    /*
        report_upas: the UPAs for the report object. If empty list, then no report is available. But there might be more than one...
        object_upa: the UPA for the object that this report references. If the originally passed object
                    was copied, then this will be the source of that copy that has a referencing report.
        copy_inaccessible: 1 if this object was copied, and the user can't see the source, so no report's available.
        error: if an error occurred while looking up (found an unavailable copy, or the report is not accessible),
               this will have a sensible string, more or less. Optional.
    */
    typedef structure {
        list<string> report_upas;
        string object_upa;
        boolean copy_inaccessible;
        string error;
    } FindObjectReportOutput;
    /*
        find_object_report searches for a referencing report. All reports (if made properly) reference the objects
        that were created at the same time. To find that report, we search back up the reference chain.

        If the object in question was a copy, then there is no referencing report. We might still want to see it,
        though! If the original object is accessible, we'll continue the search from that object, and mark the
        associated object UPA in the return value.
    */
    funcdef find_object_report(FindObjectReportParams params) returns (FindObjectReportOutput) authentication required;

    /*
        ws_id: The workspace id containing the narrative to share
        share_level: The level of sharing requested - one of "r" (read), "w" (write), "a" (admin)
        user: The user to be shared with
    */
    typedef structure {
        int ws_id;
        string share_level;
        string user;
    } RequestNarrativeShareInput;

    /*
        ok: 0 if the request failed, 1 if the request succeeded.
        error (optional): if a failure happened during the request, this has a reason why. Not present if it succeeded.
    */
    typedef structure {
        boolean ok;
        string error;
    } RequestNarrativeShareOutput;

    /*
        This sends a notification to the admins of a workspace (or anyone with share privileges) that a
        user would like access to it.

        If a request has already been made, this will fail and return with the string "a request has already been made"
    */
    funcdef request_narrative_share(RequestNarrativeShareInput params) returns (RequestNarrativeShareOutput) authentication required;

    typedef structure {
        string tag;
        string user;
    } GetAppInfoInput;

    typedef structure {
        string description;
        string id;
        string name;
        string parent_ids;
        string tooltip;
        string ver;
    } CategoryInfo;

    /*
        favorite is optional - if the app is one of the user's favorites, this will be the timestamp when it was made a favorite.
    */
    typedef structure {
        string app_type;
        list<string> authors;
        list<string> categories;
        string git_commit_hash;
        string id;
        list<string> input_types;
        string module_name;
        string name;
        string namespace;
        list<string> output_types;
        string subtitle;
        string tooltip;
        string ver;
        int favorite;
    } AppInfo;

    /*
        App info ids are all lowercase - module/app_id
    */
    typedef structure {
        mapping<string, string> module_versions;
        mapping<string, CategoryInfo> categories;
        mapping<string, mapping<string, AppInfo>> app_infos;
    } AllAppInfo;

    /*
        This returns all app info from the KBase catalog, formatted in a way to make life easy for the
        Narrative APPS panel on startup.
    */
    funcdef get_all_app_info(GetAppInfoInput input) returns (AllAppInfo output);

    /*
        This returns ignored app categories used in Narrative Apps Panel.
    */
    funcdef get_ignore_categories() returns (mapping<string, int> ignore_categories);


    /*
        data_set - should be one of "mine", "shared" - other values with throw an error
        include_type_counts - (default 0) if 1, will populate the list of types with the count of each data type
        simple_types - (default 0) if 1, will "simplify" types to just their subtype (KBaseGenomes.Genome -> Genome)
        ignore_narratives - (default 1) if 1, won't return any KBaseNarrative.* objects
        include_metadata - (default 0) if 1, includes object metadata
        ignore_workspaces - (optional) list of workspace ids - if present, will ignore any workspace ids given (useful for skipping the
            currently loaded Narrative)
        limit - (default is 30000) if present, limits returned data objects to the number given. Must be > 0 if present.
        types - (default null or empty list) if present, will only return the types specified.
    */
    typedef structure {
        string data_set;
        boolean include_type_counts;
        boolean simple_types;
        boolean ignore_narratives;
        boolean include_metadata;
        list<int> ignore_workspaces;
        int limit;
        list<string> types;
    } ListAllDataParams;

    /*
        upa - the UPA for the most recent version of the object (wsid/objid/ver format)
        name - the string name for the object
        narr_name - the name of the Narrative that the object came from
        type - the type of object this is (if simple_types was used, then this will be the simple type)
        savedate - the timestamp this object was saved
        saved_by - the user id who saved this object
    */
    typedef structure {
        string upa;
        string name;
        string narr_name;
        string type;
        int savedate;
        string saved_by;
    } DataObjectView;

    /*
        display - the display name for the workspace (typically the Narrative name)
        count - the number of objects found in the workspace (excluding Narratives, if requested)
    */
    typedef structure {
        string display;
        int count;
    } WorkspaceStats;

    /*
        objects - list of objects returned by this function
        limit_reached - 1 if there are more data objects than given by the limit in params, 0 otherwise
        type_counts - mapping of type -> count in this function call. If simple_types was 1, these types are all
            the "simple" format (Genome vs KBaseGenomes.Genome)
        workspace_display - handy thing for quickly displaying Narrative info.
    */
    typedef structure {
        list<DataObjectView> objects;
        boolean limit_reached;
        mapping<string, int> type_counts;
        mapping<int, WorkspaceStats> workspace_display;
    } ListDataResult;

    /*
        This is intended to support the Narrative front end. It returns all data a user
        owns, or is shared with them, excluding global data.

        Note that if the limit is reached, then the workspace data counts and type counts only
        reflect what data is returned.

        If there's a limit, this will return objects from the most recently modified Workspace(s).
    */
    funcdef list_all_data(ListAllDataParams params) returns (ListDataResult result) authentication required;

    /*
        workspace_ids - list of workspace ids - will only return info from these workspaces.
        include_type_counts - (default 0) if 1, will populate the list of types with the count of each data type
        simple_types - (default 0) if 1, will "simplify" types to just their subtype (KBaseGenomes.Genome -> Genome)
        ignore_narratives - (default 1) if 1, won't return any KBaseNarrative.* objects
        include_metadata - (default 0) if 1, includes object metadata
        limit - (default is 30000) if present, limits returned data objects to the number given. Must be > 0 if present.
        types - (default null or empty list) if present, will only return the types specified.
    */
    typedef structure {
        list<int> workspace_ids;
        boolean include_type_counts;
        boolean simple_types;
        boolean ignore_narratives;
        boolean include_metadata;
        int limit;
        list<string> types;
    } ListWorkspaceDataParams;

    /*
        Also intended to support the Narrative front end. It returns data from a list of
        workspaces. If the authenticated user doesn't have access to any of workspaces, it raises
        an exception. Otherwise, it returns the same structure of results as list_all_data.

        Note that if the limit is reached, then the workspace data counts and type counts only
        reflect what data is returned.

        If there's a limit, this will return objects from the most recently modified Workspace(s).
    */
    funcdef list_workspace_data(ListWorkspaceDataParams params) returns (ListDataResult result) authentication required;

    /*
        narrative_ref - either a Narrative reference (ws_id/obj_id) or UPA (ws_id/obj_id/ver).
            Should probably be a ref string to avoid overwriting changes.
        new_name - the new name for the narrative. Note that this isn't the object name, but the
            narrative's readable name.
    */
    typedef structure {
        string narrative_ref;
        string new_name;
    } RenameNarrativeParams;

    /*
        narrative_upa - UPA of the updated and saved narrative object.
    */
    typedef structure {
        string narrative_upa;
    } RenameNarrativeResult;

    /*
        This function renames a Narrative without the need to go through the Narrative application.
        It does so by the following steps:
        1. Ensure that the rename is just a string. Anything besides a string will fail.
        2. Test to see if the authenticated user has admin permissions (as this modifies the workspace
            metadata, only a workspace admin can do a rename).
        3. Rename the narrative first in the workspace metadata, then create a new Narrative object with
            the new name.
        If all this goes off well, the new narrative UPA is returned.
    */
    funcdef rename_narrative(RenameNarrativeParams params) returns (RenameNarrativeResult result) authentication required;

    /*
        narrative_upa - UPA of the narrative to be requested in search doc format.
    */
    typedef structure {
        string narrative_upa;
    } SearchDocNarrativeParams;

    /*
        desc - a brief description of the narrative cell.
        cell_type - the type of cell. Can be of type 'markdown', 'widget', 'data', 'kbase_app', 'code_cell', or '' if type is not determined.
    */
    typedef structure {
        string desc;
        string cell_type;
    } DocCell;

    /*
        name - The name of the data object.
        obj_type - The type of data object.
        readableType - The data object type in a human readable format for displays.
    */
    typedef structure {
        string name;
        string obj_type;
        string readableType;
    } DocDataObject;

    /*
        access_group - A numeric ID which corresponds to the ownership group.
        cells - A list of each cell's metadata within a given narrative.
        creation_date - The date this narrative was created (ISO 8601).
        creator - The username of the creator of a given narrative.
        data_objects - A list of each data object used in a given narrative.
        is_public - Whether or not a given narrative is publicly shared.
        modified_at - The date a given narrative was last updated according to the version provided in the UPA param (ms since epoch).
        narrative_title - The title of a given narrative.
        obj_id - The id of a given narrative
        shared_users - A list of users who are allowed access to a given narrative.
        timestamp - The time that a given narrative was last saved, regardless of version.
        total_cells - The total number of cells in a given narrative.
        version - The version of the narrative requested
    */
    typedef structure {
        int access_group;
        list<DocCell> cells;
        string creation_date;
        string creator;
        list<DocDataObject> data_objects;
        boolean is_public;
        int modified_at;
        string narrative_title;
        int obj_id;
        string owner;
        list<string> shared_users;
        int timestamp;
        int total_cells;
        int version;
    } SearchDocResult;

    /*
        Intended to return data of previous versions of a given narrative in the same format returned from Search.
        Formats a call to workspace service to fit the appropriate schema that is intended for use in UI displays
        in the narrative navigator. Raises error is "narrative_upa" param is not in specified <workspace_id/obj_id/version> format. 
        Note that this method is currently to support the UI only, and does not return the full result of a search call,
        and the following fields are omitted: boolean copied, boolean is_narratorial, boolean is_temporary, string obj_name, string obj_type_module,
        string obj_type_version, list<string> tags.
    */
    funcdef get_narrative_doc(SearchDocNarrativeParams params) returns (SearchDocResult result) authentication required;
};
