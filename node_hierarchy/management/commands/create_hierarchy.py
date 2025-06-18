from django.core.management.base import BaseCommand, CommandError
from node_hierarchy.models import NodeHierarchy
import sys, csv
import os
from optparse import make_option

class Command(BaseCommand):
    help = 'Create Hierarchy'
    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest = "filename",
            help = "specify import file",
            metavar = "FILE"
        ),
    )

    def get_or_create(self, name, parent, node_type):
        try:
            return NodeHierarchy.objects.get(name=name, parent=parent)
        except:
            return NodeHierarchy.objects.create(name=name, parent=parent, node_type=node_type)

    def handle(self, *args, **options):
        # make sure file option is present
        if options['filename'] == None :
            raise CommandError("Option `--file=...` must be specified.")

        # make sure file path resolves
        if not os.path.isfile(options['filename']) :
            raise CommandError("File does not exist at the specified path.")


        path = options['filename']
        with open(path, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            try:
                state = NodeHierarchy.objects.get(parent=None, node_type=0)
            except:
                sys.stderr.write("Create State first.")
                sys.exit(0)

            for idx, row in enumerate(reader):
                print row
                if idx:
                    district, taluko, city = row[1], row[2], row[3]
                    district_obj = self.get_or_create(district, state, 1)
                    taluko_obj = self.get_or_create(taluko, district_obj, 2)
                    city_obj = self.get_or_create(city, taluko_obj, 3)

            sys.stdout.write("Success!")

