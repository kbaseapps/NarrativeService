package us.kbase.narrativeservice;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: NarrativeService</p>
 * <pre>
 * A KBase module: NarrativeService
 * </pre>
 */
public class NarrativeServiceClient {
    private JsonClientCaller caller;
    private String serviceVersion = null;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public NarrativeServiceClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public NarrativeServiceClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public NarrativeServiceClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Constructs a client with a custom URL
     * and a custom authorization service URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @param auth the URL of the authorization server.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public NarrativeServiceClient(URL url, String user, String password, URL auth) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password, auth);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    public String getServiceVersion() {
        return this.serviceVersion;
    }

    public void setServiceVersion(String newValue) {
        this.serviceVersion = newValue;
    }

    /**
     * <p>Original spec-file function name: list_objects_with_sets</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.ListObjectsWithSetsParams ListObjectsWithSetsParams}
     * @return   instance of type {@link us.kbase.narrativeservice.ListObjectsWithSetsOutput ListObjectsWithSetsOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ListObjectsWithSetsOutput listObjectsWithSets(ListObjectsWithSetsParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<ListObjectsWithSetsOutput>> retType = new TypeReference<List<ListObjectsWithSetsOutput>>() {};
        List<ListObjectsWithSetsOutput> res = caller.jsonrpcCall("NarrativeService.list_objects_with_sets", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: copy_narrative</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.CopyNarrativeParams CopyNarrativeParams}
     * @return   instance of type {@link us.kbase.narrativeservice.CopyNarrativeOutput CopyNarrativeOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public CopyNarrativeOutput copyNarrative(CopyNarrativeParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<CopyNarrativeOutput>> retType = new TypeReference<List<CopyNarrativeOutput>>() {};
        List<CopyNarrativeOutput> res = caller.jsonrpcCall("NarrativeService.copy_narrative", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: create_new_narrative</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.CreateNewNarrativeParams CreateNewNarrativeParams}
     * @return   instance of type {@link us.kbase.narrativeservice.CreateNewNarrativeOutput CreateNewNarrativeOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public CreateNewNarrativeOutput createNewNarrative(CreateNewNarrativeParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<CreateNewNarrativeOutput>> retType = new TypeReference<List<CreateNewNarrativeOutput>>() {};
        List<CreateNewNarrativeOutput> res = caller.jsonrpcCall("NarrativeService.create_new_narrative", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: copy_object</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.CopyObjectParams CopyObjectParams}
     * @return   instance of type {@link us.kbase.narrativeservice.CopyObjectOutput CopyObjectOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public CopyObjectOutput copyObject(CopyObjectParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<CopyObjectOutput>> retType = new TypeReference<List<CopyObjectOutput>>() {};
        List<CopyObjectOutput> res = caller.jsonrpcCall("NarrativeService.copy_object", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_available_types</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.ListAvailableTypesParams ListAvailableTypesParams}
     * @return   instance of type {@link us.kbase.narrativeservice.ListAvailableTypesOutput ListAvailableTypesOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ListAvailableTypesOutput listAvailableTypes(ListAvailableTypesParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<ListAvailableTypesOutput>> retType = new TypeReference<List<ListAvailableTypesOutput>>() {};
        List<ListAvailableTypesOutput> res = caller.jsonrpcCall("NarrativeService.list_available_types", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_narratorials</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.ListNarratorialParams ListNarratorialParams}
     * @return   instance of type {@link us.kbase.narrativeservice.NarratorialList NarratorialList}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public NarratorialList listNarratorials(ListNarratorialParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<NarratorialList>> retType = new TypeReference<List<NarratorialList>>() {};
        List<NarratorialList> res = caller.jsonrpcCall("NarrativeService.list_narratorials", args, retType, true, false, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_narratives</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.ListNarrativeParams ListNarrativeParams}
     * @return   instance of type {@link us.kbase.narrativeservice.NarrativeList NarrativeList}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public NarrativeList listNarratives(ListNarrativeParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<NarrativeList>> retType = new TypeReference<List<NarrativeList>>() {};
        List<NarrativeList> res = caller.jsonrpcCall("NarrativeService.list_narratives", args, retType, true, false, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: set_narratorial</p>
     * <pre>
     * Allows a user to create a Narratorial given a WS they own. Right now
     * anyone can do this, but we may restrict in the future to users that
     * have a particular role.  Run simply as:
     *     ns.set_narratorial({'ws':'MyWsName'}) or,
     *     ns.set_narratorial({'ws':'4231'})
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.SetNarratorialParams SetNarratorialParams}
     * @return   instance of type {@link us.kbase.narrativeservice.SetNarratorialResult SetNarratorialResult}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public SetNarratorialResult setNarratorial(SetNarratorialParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<SetNarratorialResult>> retType = new TypeReference<List<SetNarratorialResult>>() {};
        List<SetNarratorialResult> res = caller.jsonrpcCall("NarrativeService.set_narratorial", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: remove_narratorial</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.RemoveNarratorialParams RemoveNarratorialParams}
     * @return   instance of type {@link us.kbase.narrativeservice.RemoveNarratorialResult RemoveNarratorialResult}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public RemoveNarratorialResult removeNarratorial(RemoveNarratorialParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<RemoveNarratorialResult>> retType = new TypeReference<List<RemoveNarratorialResult>>() {};
        List<RemoveNarratorialResult> res = caller.jsonrpcCall("NarrativeService.remove_narratorial", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: find_object_report</p>
     * <pre>
     * find_object_report searches for a referencing report. All reports (if made properly) reference the objects
     * that were created at the same time. To find that report, we search back up the reference chain.
     * If the object in question was a copy, then there is no referencing report. We might still want to see it,
     * though! If the original object is accessible, we'll continue the search from that object, and mark the
     * associated object UPA in the return value.
     * </pre>
     * @param   params   instance of type {@link us.kbase.narrativeservice.FindObjectReportParams FindObjectReportParams}
     * @return   instance of type {@link us.kbase.narrativeservice.FindObjectReportOutput FindObjectReportOutput}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public FindObjectReportOutput findObjectReport(FindObjectReportParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<FindObjectReportOutput>> retType = new TypeReference<List<FindObjectReportOutput>>() {};
        List<FindObjectReportOutput> res = caller.jsonrpcCall("NarrativeService.find_object_report", args, retType, true, true, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }

    public Map<String, Object> status(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<Map<String, Object>>> retType = new TypeReference<List<Map<String, Object>>>() {};
        List<Map<String, Object>> res = caller.jsonrpcCall("NarrativeService.status", args, retType, true, false, jsonRpcContext, this.serviceVersion);
        return res.get(0);
    }
}
