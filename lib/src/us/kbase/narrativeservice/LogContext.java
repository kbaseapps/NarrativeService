
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
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "narr_ref",
    "narr_version",
    "log_time",
    "level"
})
public class LogContext {

    @JsonProperty("narr_ref")
    private String narrRef;
    @JsonProperty("narr_version")
    private Long narrVersion;
    @JsonProperty("log_time")
    private String logTime;
    @JsonProperty("level")
    private String level;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("narr_ref")
    public String getNarrRef() {
        return narrRef;
    }

    @JsonProperty("narr_ref")
    public void setNarrRef(String narrRef) {
        this.narrRef = narrRef;
    }

    public LogContext withNarrRef(String narrRef) {
        this.narrRef = narrRef;
        return this;
    }

    @JsonProperty("narr_version")
    public Long getNarrVersion() {
        return narrVersion;
    }

    @JsonProperty("narr_version")
    public void setNarrVersion(Long narrVersion) {
        this.narrVersion = narrVersion;
    }

    public LogContext withNarrVersion(Long narrVersion) {
        this.narrVersion = narrVersion;
        return this;
    }

    @JsonProperty("log_time")
    public String getLogTime() {
        return logTime;
    }

    @JsonProperty("log_time")
    public void setLogTime(String logTime) {
        this.logTime = logTime;
    }

    public LogContext withLogTime(String logTime) {
        this.logTime = logTime;
        return this;
    }

    @JsonProperty("level")
    public String getLevel() {
        return level;
    }

    @JsonProperty("level")
    public void setLevel(String level) {
        this.level = level;
    }

    public LogContext withLevel(String level) {
        this.level = level;
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
        return ((((((((((("LogContext"+" [narrRef=")+ narrRef)+", narrVersion=")+ narrVersion)+", logTime=")+ logTime)+", level=")+ level)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
