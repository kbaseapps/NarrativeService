
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
 * <p>Original spec-file type: RequestNarrativeShareOutput</p>
 * <pre>
 * ok: 0 if the request failed, 1 if the request succeeded.
 * error (optional): if a failure happened during the request, this has a reason why. Not present if it succeeded.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ok",
    "error"
})
public class RequestNarrativeShareOutput {

    @JsonProperty("ok")
    private Long ok;
    @JsonProperty("error")
    private String error;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("ok")
    public Long getOk() {
        return ok;
    }

    @JsonProperty("ok")
    public void setOk(Long ok) {
        this.ok = ok;
    }

    public RequestNarrativeShareOutput withOk(Long ok) {
        this.ok = ok;
        return this;
    }

    @JsonProperty("error")
    public String getError() {
        return error;
    }

    @JsonProperty("error")
    public void setError(String error) {
        this.error = error;
    }

    public RequestNarrativeShareOutput withError(String error) {
        this.error = error;
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
        return ((((((("RequestNarrativeShareOutput"+" [ok=")+ ok)+", error=")+ error)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
