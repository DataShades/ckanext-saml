# API actions

The extension has several actions which greatly facilitate the process of 
setting up remote IdP metadata and actually make it possible to make these 
settings without actually copying them.

--------------------------------------------------------------------------------
## Read remote metadata

**`saml_idp_refresh`**(context: dict[str, Any], data_dict: dict[str, Any])

Refresh IdP details using remote metadata. It gets the remote metadata XML file 
from the provided URL, parses it, caches and returns a dict with extracted data.

**Parameters**: `url`(string) - a URL for the remote metadata source 

**Return**: settings dict with extracted idp data 

**Type**: `dict`

--------------------------------------------------------------------------------
## Show remote metadata

**`saml_idp_show`**(context: dict[str, Any], data_dict: dict[str, Any])

Show IdP details pulled from the remote metadata.
Actually it gets previously cached remote metadata and returns a dict with this 
data. 

**Return**: settings dict with extracted idp data 

**Type**: `dict`

--------------------------------------------------------------------------------