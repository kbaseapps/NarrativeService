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
    */
    typedef structure {
        string ws_name;
        int ws_id;
        list<string> workspaces;
        list<string> types;
        boolean includeMetadata;
    } ListObjectsWithSetsParams;

    /*
        data_palette_refs - mapping from workspace Id to reference to DataPalette
            container existing in given workspace.
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
        Log message context.
        narr_ref - the Narrative reference (of the form wsid/objid - leaving version off should make lookup/aggregation easier)
        narr_version - the current version of the narrative (if a save_narrative message, the new version)
        log_time - timestamp of event in ISO-8601 format
        level - should be one of INFO, ERROR, WARN (default INFO if not present)
        (the username is inferred from the auth token)
    */
    typedef structure {
        string narr_ref;
        int narr_version;
        timestamp log_time;
        string level;
    } LogContext;

    typedef structure {
        LogContext context;
    } LogOpenParams;

    funcdef log_open_narrative(LogOpenParams params) returns (boolean log_result) authentication required;

    typedef structure {
        LogContext context;
    } LogSaveParams;

    funcdef log_save_narrative(LogSaveParams params) returns (boolean log_result) authentication required;

};
