# Copyright (C) 2014 Okami, okami@fuzetsu.info

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import logging

import radicale.config
import radicale.log
from django.conf import settings

old_load = radicale.config.load


def new_load(*args, **kwargs):
    return old_load(extra_config=settings.RADICALE_CONFIG)


radicale.config.load = new_load
radicale.log.LOGGER = logging.getLogger("diary")

default_app_config = 'modules.diary.apps.DiaryConfig'
