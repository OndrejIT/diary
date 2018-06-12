# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2018

from django.shortcuts import redirect
from reversion.admin import VersionAdmin
from django.contrib import messages


class PermissionVersionAdmin(VersionAdmin):
    def _reversion_revisionform_view(self, request, version, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Revert is supported only super user.")
            return redirect("{}:{}_{}_change".format(self.admin_site.name, self.opts.app_label, self.opts.model_name), object_id=version.object_id)
        else:
            return super()._reversion_revisionform_view(request, version, *args, **kwargs)
