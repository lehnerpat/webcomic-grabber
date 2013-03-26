# wcgr -- Webcomic Grabber

Automatically downloads the images from continuous issues of a webcomic, allowing you to easily customize which part of the page's HTML is used as the issue title, the image URL and the link to the next issue.

# Prerequisites

* **Required:**
  * Python 2 *(should work with Python 2.6 and above, only tested on 2.7)*
  * lxml
* **Optional:**
  * *requests:* some web servers send responses on which Python's standard
    HTTP library barfs; the requests library is more robust at handling
    HTTP responses

# License

This program is released under the GNU GPLv3 or newer.

    Copyright (C) 2013 Nevik Rehnel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

For the full license text, see [LICENSE](LICENSE).
