# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand

from django_munin.services.discovery_service import scan_modules


class Command(BaseCommand):
    help = "Discover installed Volkanos modules and persist to DB"

    def handle(self, *args, **options):
        created, updated, deactivated = scan_modules()
        total = created + updated
        if options["verbosity"] > 0:
            self.stdout.write(
                f"Discovered {total} modules ({created} created, {updated} updated, {deactivated} deactivated)"
            )
