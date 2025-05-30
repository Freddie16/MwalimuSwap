import json
from django.core.management.base import BaseCommand
from users.models import County, SubCounty, Ward # adjust if your models are in a different app

class Command(BaseCommand):
    help = "Import Kenya Counties, SubCounties and Wards from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to Kenya-Counties-SubCounties-and-Wards.json'
        )

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        self.stdout.write(f"📥 Loading data from: {json_file}")

        try:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)

            # Assuming the JSON structure is a dictionary where keys are county names
            # and values are dictionaries containing subcounties and wards.
            # Example: { "Mombasa": { "Changamwe": ["Port Reitz", ...], ... }, ... }
            
            # Iterate through counties (keys of the top-level dictionary)
            for county_name, subcounties_data in data.items():
                county, created_county = County.objects.get_or_create(name=county_name)
                if created_county:
                    self.stdout.write(self.style.SUCCESS(f"  ➕ Created County: {county_name}"))
                
                # Iterate through subcounties within each county
                for subcounty_name, wards_list in subcounties_data.items():
                    subcounty, created_subcounty = SubCounty.objects.get_or_create(name=subcounty_name, county=county)
                    if created_subcounty:
                        self.stdout.write(self.style.SUCCESS(f"    ➕ Created SubCounty: {subcounty_name} in {county_name}"))
                    
                    # Iterate through wards within each subcounty
                    for ward_name in wards_list:
                        ward, created_ward = Ward.objects.get_or_create(name=ward_name, subcounty=subcounty)
                        if created_ward:
                            self.stdout.write(self.style.SUCCESS(f"      ➕ Created Ward: {ward_name} in {subcounty_name}"))

            self.stdout.write(self.style.SUCCESS("✅ All counties, subcounties, and wards have been imported successfully!"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"❌ Error: JSON file not found at {json_file}"))
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"❌ Error: Could not decode JSON from {json_file}. Check file format."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ An unexpected error occurred: {e}"))

