#! /usr/bin/env sh

rm web2py.plugin.daxs-media-galley.w2p
tar czvf web2py.plugin.daxs-media-galley.w2p --exclude='*.sh'  --exclude='*.md' --exclude='LICENSE' --exclude='*.pyc' *
