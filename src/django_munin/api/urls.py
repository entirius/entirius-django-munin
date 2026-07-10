# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.urls import path

from django_munin.api.views import ConfigEntryViewSet, MuninViewSet

munin_list = MuninViewSet.as_view({"get": "list"})
munin_detail = MuninViewSet.as_view({"get": "retrieve"})

config_entry_list = ConfigEntryViewSet.as_view({"get": "list", "post": "create"})
config_entry_detail = ConfigEntryViewSet.as_view({"patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path("", munin_list, name="munin-list"),
    path("<str:key>/", munin_detail, name="munin-detail"),
    path("admin/entries/", config_entry_list, name="munin-config-entry-list"),
    path("admin/entries/<str:key>/", config_entry_detail, name="munin-config-entry-detail"),
]
