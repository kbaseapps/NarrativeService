## v0.2.6
* Refactor `list_objects_with_sets` function to its own submodule.
* Modify dynamic service client with URL caching to not require a separate token on each request - these are only alive for the lifetime of a single call to the service anyway, so it just uses a single token.
* Make a stub for the rename_narrative function.
