
package us.kbase.narrativeservice;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: FindObjectReportOutput</p>
 * <pre>
 * report_upas: the UPAs for the report object. If empty list, then no report is available. But there might be more than one...
 * object_upa: the UPA for the object that this report references. If the originally passed object
 *             was copied, then this will be the source of that copy that has a referencing report.
 * copy_inaccessible: 1 if this object was copied, and the user can't see the source, so no report's available.
 * error: if an error occurred while looking up (found an unavailable copy, or the report is not accessible),
 *        this will have a sensible string, more or less. Optional.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_upas",
    "object_upa",
    "copy_inaccessible",
    "error"
})
public class FindObjectReportOutput {

    @JsonProperty("report_upas")
    private List<String> reportUpas;
    @JsonProperty("object_upa")
    private java.lang.String objectUpa;
    @JsonProperty("copy_inaccessible")
    private Long copyInaccessible;
    @JsonProperty("error")
    private java.lang.String error;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("report_upas")
    public List<String> getReportUpas() {
        return reportUpas;
    }

    @JsonProperty("report_upas")
    public void setReportUpas(List<String> reportUpas) {
        this.reportUpas = reportUpas;
    }

    public FindObjectReportOutput withReportUpas(List<String> reportUpas) {
        this.reportUpas = reportUpas;
        return this;
    }

    @JsonProperty("object_upa")
    public java.lang.String getObjectUpa() {
        return objectUpa;
    }

    @JsonProperty("object_upa")
    public void setObjectUpa(java.lang.String objectUpa) {
        this.objectUpa = objectUpa;
    }

    public FindObjectReportOutput withObjectUpa(java.lang.String objectUpa) {
        this.objectUpa = objectUpa;
        return this;
    }

    @JsonProperty("copy_inaccessible")
    public Long getCopyInaccessible() {
        return copyInaccessible;
    }

    @JsonProperty("copy_inaccessible")
    public void setCopyInaccessible(Long copyInaccessible) {
        this.copyInaccessible = copyInaccessible;
    }

    public FindObjectReportOutput withCopyInaccessible(Long copyInaccessible) {
        this.copyInaccessible = copyInaccessible;
        return this;
    }

    @JsonProperty("error")
    public java.lang.String getError() {
        return error;
    }

    @JsonProperty("error")
    public void setError(java.lang.String error) {
        this.error = error;
    }

    public FindObjectReportOutput withError(java.lang.String error) {
        this.error = error;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((("FindObjectReportOutput"+" [reportUpas=")+ reportUpas)+", objectUpa=")+ objectUpa)+", copyInaccessible=")+ copyInaccessible)+", error=")+ error)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
