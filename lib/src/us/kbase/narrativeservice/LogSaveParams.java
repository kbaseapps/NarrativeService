
package us.kbase.narrativeservice;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: LogSaveParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "context"
})
public class LogSaveParams {

    /**
     * <p>Original spec-file type: LogContext</p>
     * <pre>
     * Log message context.
     * narr_ref - the Narrative reference (of the form wsid/objid - leaving version off should make lookup/aggregation easier)
     * narr_version - the current version of the narrative (if a save_narrative message, the new version)
     * log_time - timestamp of event in ISO-8601 format
     * level - should be one of INFO, ERROR, WARN (default INFO if not present)
     * (the username is inferred from the auth token)
     * </pre>
     * 
     */
    @JsonProperty("context")
    private LogContext context;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    /**
     * <p>Original spec-file type: LogContext</p>
     * <pre>
     * Log message context.
     * narr_ref - the Narrative reference (of the form wsid/objid - leaving version off should make lookup/aggregation easier)
     * narr_version - the current version of the narrative (if a save_narrative message, the new version)
     * log_time - timestamp of event in ISO-8601 format
     * level - should be one of INFO, ERROR, WARN (default INFO if not present)
     * (the username is inferred from the auth token)
     * </pre>
     * 
     */
    @JsonProperty("context")
    public LogContext getContext() {
        return context;
    }

    /**
     * <p>Original spec-file type: LogContext</p>
     * <pre>
     * Log message context.
     * narr_ref - the Narrative reference (of the form wsid/objid - leaving version off should make lookup/aggregation easier)
     * narr_version - the current version of the narrative (if a save_narrative message, the new version)
     * log_time - timestamp of event in ISO-8601 format
     * level - should be one of INFO, ERROR, WARN (default INFO if not present)
     * (the username is inferred from the auth token)
     * </pre>
     * 
     */
    @JsonProperty("context")
    public void setContext(LogContext context) {
        this.context = context;
    }

    public LogSaveParams withContext(LogContext context) {
        this.context = context;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((("LogSaveParams"+" [context=")+ context)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
