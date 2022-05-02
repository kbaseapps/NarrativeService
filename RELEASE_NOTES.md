
## v0.5.2
* Fix `get_narrative_doc` method for fetching legacy narratives with `worksheets` as a key

## v0.3.4
* Add `get_narrative_doc` method that returns narrative data in the same format as the Search API results
## v0.3.3
* Fixed unittests and added GHA

## v0.3.2
* Adjust intro cell height

## v0.3.1
* Switch welcome/intro cell from markdown to a prerendered code cell with an embedded IFrame

## v0.2.6
* Refactor `list_objects_with_sets` function to its own submodule.
* Modify dynamic service client with URL caching to not require a separate token on each request - these are only alive for the lifetime of a single call to the service anyway, so it just uses a single token.
* Make a stub for the rename_narrative function.
