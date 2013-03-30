# wcgr -- Webcomic Grabber

Automatically downloads the images from continuous issues of a webcomic, allowing you to easily customize which part of the page's HTML is used as the issue title, the image URL and the link to the next issue.

# Prerequisites

* **Required:**
  * Python 2 *(should work with Python 2.6 and above, only tested on 2.7)*
  * lxml *(including* cssselect; *which might be placed in an extra package)*
* **Optional:**
  * *requests:* some web servers send responses on which Python's standard
    HTTP library barfs; the requests library is more robust at handling
    HTTP responses

# A Note on Artist Permission

While this program is free to use (under the terms of the GNU GPLv3), please be aware that the intellectual property rights of each comic belong to the respective author(s)! This program is meant for private use only.

Many artists rely on the ad revenues of their website as a source of income, so if you mean to use this program to get more than a few pages from a comic, please be polite and send them a short email asking for permission. Most will not mind it if you do this only once and for personal use, but many artists and webmasters have made bad experiences with these programs, where other people took their copyrighted work, and bundled it with their own apps without permission.

Don't be a thief.

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
