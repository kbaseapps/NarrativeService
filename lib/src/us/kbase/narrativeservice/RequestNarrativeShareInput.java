
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
 * <p>Original spec-file type: RequestNarrativeShareInput</p>
 * <pre>
 * ws_id: The workspace id containing the narrative to share
 * share_level: The level of sharing requested - one of "r" (read), "w" (write), "a" (admin)
 * user: The user to be shared with
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ws_id",
    "share_level",
    "user"
})
public class RequestNarrativeShareInput {

    @JsonProperty("ws_id")
    private Long wsId;
    @JsonProperty("share_level")
    private String shareLevel;
    @JsonProperty("user")
    private String user;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("ws_id")
    public Long getWsId() {
        return wsId;
    }

    @JsonProperty("ws_id")
    public void setWsId(Long wsId) {
        this.wsId = wsId;
    }

    public RequestNarrativeShareInput withWsId(Long wsId) {
        this.wsId = wsId;
        return this;
    }

    @JsonProperty("share_level")
    public String getShareLevel() {
        return shareLevel;
    }

    @JsonProperty("share_level")
    public void setShareLevel(String shareLevel) {
        this.shareLevel = shareLevel;
    }

    public RequestNarrativeShareInput withShareLevel(String shareLevel) {
        this.shareLevel = shareLevel;
        return this;
    }

    @JsonProperty("user")
    public String getUser() {
        return user;
    }

    @JsonProperty("user")
    public void setUser(String user) {
        this.user = user;
    }

    public RequestNarrativeShareInput withUser(String user) {
        this.user = user;
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
        return ((((((((("RequestNarrativeShareInput"+" [wsId=")+ wsId)+", shareLevel=")+ shareLevel)+", user=")+ user)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
