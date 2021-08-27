script.service.hyperion
=======================

Kodi addon to capture video data and send it to Hyperion. Note that this plugin will not work for Kodi running on the Raspberry Pi, because the video capture interface is not (yet?) supported on this device.

Information about Hyperion can be found here: https://wiki.hyperion-project.org

The addon can be installed by downlading the zip and extracting it to the addon directory (probably ~/.xbmc/addons on Linux and C:\Users\user\AppData\Roaming\XBMC\addons on Windows)


Changes in this repo
--------------------

The addon in this repo is based on the one from the Hyperion project. Since there were a couple annoying bugs, it was actually easier to rewrite the main part of the plugin, than to fix the bugs. At least for my specific case. For example: the settings were stripped down, cause I don't need them. Also I added a standalone script, that can be used to enable/disable the addon via remote.
