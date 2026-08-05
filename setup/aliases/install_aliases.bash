#!/bin/bash
cp .bash_aliases $(eval echo ~$USER)
source "$(eval echo ~$USER)/.bashrc"

