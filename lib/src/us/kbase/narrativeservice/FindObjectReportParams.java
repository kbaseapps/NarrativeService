
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
 * <p>Original spec-file type: FindObjectReportParams</p>
 * <pre>
 * This first version only takes a single UPA as input and attempts to find the report that made it.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "upa"
})
public class FindObjectReportParams {

    @JsonProperty("upa")
    private String upa;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("upa")
    public String getUpa() {
        return upa;
    }

    @JsonProperty("upa")
    public void setUpa(String upa) {
        this.upa = upa;
    }

    public FindObjectReportParams withUpa(String upa) {
        this.upa = upa;
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
        return ((((("FindObjectReportParams"+" [upa=")+ upa)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
