#!/bin/bash

set -ex

export IHP_SOURCE_URL=https://raw.githubusercontent.com/KrzysztofHerman/IHP-Open-PDK/refs/heads/pycells/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib
export IHP_CODE=$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/python/sg13g2_pycell_lib

if [ ! -f "${IHP_CODE}/ihp/gring_code.py" ]; then

     cd $IHP_CODE

# diff -u current/__init__.py new/__init__.py
     sudo patch __init__.py <<EOF
--- current/__init__.py 2024-10-17 01:13:15.457070700 +0200
+++ new/__init__.py     2024-10-17 01:10:41.762632900 +0200
@@ -48,6 +48,7 @@
         'rhigh_code',
         'rppd_code',
         'sealring_code',
+        'gring_code',
         'npn13G2_base_code',
         'npn13G2_code',
         'npn13G2L_code',
EOF

# diff -u current/sg13g2_tech.json new/sg13g2_tech.json
     sudo patch sg13g2_tech.json <<EOF
--- current/sg13g2_tech.json    2024-10-17 01:13:15.466071400 +0200
+++ new/sg13g2_tech.json        2024-10-17 01:12:59.281839900 +0200
@@ -902,7 +902,10 @@
         "sealring_complete_minW": "50u",
         "sealring_complete_maxL": "25000u",
         "sealring_complete_maxW": "32000u",
-        "sealring_complete_edgeBox": "25u"
+        "sealring_complete_edgeBox": "25u",
+        
+        "gring_defW": "3u",
+        "gring_defL": "3u"
     },
     "Layers": {
     }
EOF

     cd ihp/
     sudo wget "${IHP_SOURCE_URL}/ihp/gring_code.py"

fi
