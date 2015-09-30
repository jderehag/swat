#!/usr/bin/env bash
# Copyright (c) 2015, Jesper Derehag <jesper.derehag@ericsson.com> for Ericsson AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#**************************    THIS LINE IS 120 CHARACTERS WIDE - DO *NOT* EXCEED 120 CHARACTERS!    ******************
# Short description:
#   This script installs all repo specific hooks into the repo.
#   It MUST be run the first thing when cloning a repo.
#
#   It reads all files in git-hooks and creates symlinks to those in .git/hooks/
#
#   I have also experimented a little bit with gitconfig init.templatedir and copying all the hooks.
#   But in the end, that config still needs to be set one way or another (git init) so from a usability point of view
#   it makes little difference (its not stored on remotes).

REPO_ROOT=`dirname $0`
pushd . > /dev/null
cd $REPO_ROOT

HOOKS=`ls tools/git-hooks`
for HOOK in $HOOKS
do
	ln -fs ../../tools/git-hooks/$HOOK .git/hooks/$HOOK
done

popd > /dev/null
