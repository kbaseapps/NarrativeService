
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
import us.kbase.common.service.Tuple3;


/**
 * <p>Original spec-file type: CreateNewNarrativeParams</p>
 * <pre>
 * app - name of app (optional, either app or method may be defined)
 * method - name of method (optional, either app or method may be defined)
 * appparam - parameters of app/method packed into string in format:
 *     "step_pos,param_name,param_value(;...)*" (alternative to appData)
 * appData - parameters of app/method in unpacked form (alternative to appparam)
 * markdown - markdown text for cell of 'markdown' type (optional)
 * copydata - packed import data in format "import(;...)*" (alternative to importData)
 * importData - import data in unpacked form (alternative to copydata)
 * includeIntroCell - if 1, adds an introductory markdown cell at the top (optional, default 0)
 * title - name of the new narrative (optional, if a string besides 'Untitled', this will
 *         mark the narrative as not temporary, so it will appear in the dashboard)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "app",
    "method",
    "appparam",
    "appData",
    "markdown",
    "copydata",
    "importData",
    "includeIntroCell",
    "title"
})
public class CreateNewNarrativeParams {

    @JsonProperty("app")
    private java.lang.String app;
    @JsonProperty("method")
    private java.lang.String method;
    @JsonProperty("appparam")
    private java.lang.String appparam;
    @JsonProperty("appData")
    private List<Tuple3 <Long, String, String>> appData;
    @JsonProperty("markdown")
    private java.lang.String markdown;
    @JsonProperty("copydata")
    private java.lang.String copydata;
    @JsonProperty("importData")
    private List<String> importData;
    @JsonProperty("includeIntroCell")
    private java.lang.Long includeIntroCell;
    @JsonProperty("title")
    private java.lang.String title;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("app")
    public java.lang.String getApp() {
        return app;
    }

    @JsonProperty("app")
    public void setApp(java.lang.String app) {
        this.app = app;
    }

    public CreateNewNarrativeParams withApp(java.lang.String app) {
        this.app = app;
        return this;
    }

    @JsonProperty("method")
    public java.lang.String getMethod() {
        return method;
    }

    @JsonProperty("method")
    public void setMethod(java.lang.String method) {
        this.method = method;
    }

    public CreateNewNarrativeParams withMethod(java.lang.String method) {
        this.method = method;
        return this;
    }

    @JsonProperty("appparam")
    public java.lang.String getAppparam() {
        return appparam;
    }

    @JsonProperty("appparam")
    public void setAppparam(java.lang.String appparam) {
        this.appparam = appparam;
    }

    public CreateNewNarrativeParams withAppparam(java.lang.String appparam) {
        this.appparam = appparam;
        return this;
    }

    @JsonProperty("appData")
    public List<Tuple3 <Long, String, String>> getAppData() {
        return appData;
    }

    @JsonProperty("appData")
    public void setAppData(List<Tuple3 <Long, String, String>> appData) {
        this.appData = appData;
    }

    public CreateNewNarrativeParams withAppData(List<Tuple3 <Long, String, String>> appData) {
        this.appData = appData;
        return this;
    }

    @JsonProperty("markdown")
    public java.lang.String getMarkdown() {
        return markdown;
    }

    @JsonProperty("markdown")
    public void setMarkdown(java.lang.String markdown) {
        this.markdown = markdown;
    }

    public CreateNewNarrativeParams withMarkdown(java.lang.String markdown) {
        this.markdown = markdown;
        return this;
    }

    @JsonProperty("copydata")
    public java.lang.String getCopydata() {
        return copydata;
    }

    @JsonProperty("copydata")
    public void setCopydata(java.lang.String copydata) {
        this.copydata = copydata;
    }

    public CreateNewNarrativeParams withCopydata(java.lang.String copydata) {
        this.copydata = copydata;
        return this;
    }

    @JsonProperty("importData")
    public List<String> getImportData() {
        return importData;
    }

    @JsonProperty("importData")
    public void setImportData(List<String> importData) {
        this.importData = importData;
    }

    public CreateNewNarrativeParams withImportData(List<String> importData) {
        this.importData = importData;
        return this;
    }

    @JsonProperty("includeIntroCell")
    public java.lang.Long getIncludeIntroCell() {
        return includeIntroCell;
    }

    @JsonProperty("includeIntroCell")
    public void setIncludeIntroCell(java.lang.Long includeIntroCell) {
        this.includeIntroCell = includeIntroCell;
    }

    public CreateNewNarrativeParams withIncludeIntroCell(java.lang.Long includeIntroCell) {
        this.includeIntroCell = includeIntroCell;
        return this;
    }

    @JsonProperty("title")
    public java.lang.String getTitle() {
        return title;
    }

    @JsonProperty("title")
    public void setTitle(java.lang.String title) {
        this.title = title;
    }

    public CreateNewNarrativeParams withTitle(java.lang.String title) {
        this.title = title;
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
        return ((((((((((((((((((((("CreateNewNarrativeParams"+" [app=")+ app)+", method=")+ method)+", appparam=")+ appparam)+", appData=")+ appData)+", markdown=")+ markdown)+", copydata=")+ copydata)+", importData=")+ importData)+", includeIntroCell=")+ includeIntroCell)+", title=")+ title)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
