# Generated by Django 2.2.1 on 2019-06-10 18:11

from django.db import migrations, models


class Migration(migrations.Migration):


    def update_nationality(apps, schema_editor):
        def create_or_update_country(apps, slug, country_code, country_name):
            slug = slug.lower()
            Country = apps.get_model('core', 'Country')
            person, created = Country.objects.get_or_create(
                slug=slug, 
                defaults={"name": country_name, "code": country_code}
            )

        create_or_update_country(apps, 'na', '0', 'Unknown')

        countries = [
            {"slug":"ENG","country_code":"44-0","country_name":"England",},
            {"slug":"SCO","country_code":"44-1","country_name":"Scotland",},
            {"slug":"WLS","country_code":"44-2","country_name":"Wales",},
        ]

        for country in countries:
            create_or_update_country(apps, country['slug'],country['country_code'],country['country_name'])

        nationalities={
            "Afghanistan":"Afghan",
            "Albania":"Albanian",
            "Algeria":"Algerian",
            "Argentina":"Argentine",
            "Australia":"Australian",
            "Austria":"Austrian",
            "Bangladesh":"Bangladeshi",
            "Belgium":"Belgian",
            "Bolivia":"Bolivian",
            "Botswana":"Batswana",
            "Brazil":"Brazilian",
            "Bulgaria":"Bulgarian",
            "Cambodia":"Cambodian",
            "Cameroon":"Cameroonian",
            "Canada":"Canadian",
            "Chile":"Chilean",
            "China":"Chinese",
            "Colombia":"Colombian",
            "Costa Rica":"Costa Rican",
            "Croatia":"Croatian",
            "Cuba":"Cuban",
            "Czech Republic":"Czech",
            "Denmark":"Danish",
            "Dominican Republic":"Dominican",
            "Ecuador":"Ecuadorian",
            "Egypt":"Egyptian",
            "El Salvador":"Salvadorian",
            "England":"English",
            "Estonia":"Estonian",
            "Ethiopia":"Ethiopian",
            "Fiji":"Fijian",
            "Finland":"Finnish",
            "France":"French",
            "Germany":"German",
            "Ghana":"Ghanaian",
            "Greece":"Greek",
            "Guatemala":"Guatemalan",
            "Haiti":"Haitian",
            "Honduras":"Honduran",
            "Hungary":"Hungarian",
            "Iceland":"Icelandic",
            "India":"Indian",
            "Indonesia":"Indonesian",
            "Iran":"Iranian",
            "Iraq":"Iraqi",
            "Ireland":"Irish",
            "Israel":"Israeli",
            "Italy":"Italian",
            "Jamaica":"Jamaican",
            "Japan":"Japanese",
            "Jordan":"Jordanian",
            "Kenya":"Kenyan",
            "Kuwait":"Kuwaiti",
            "Laos":"Lao",
            "Latvia":"Latvian",
            "Lebanon":"Lebanese",
            "Libya":"Libyan",
            "Lithuania":"Lithuanian",
            "Malaysia":"Malaysian",
            "Mali":"Malian",
            "Malta":"Maltese",
            "Mexico":"Mexican",
            "Mongolia":"Mongolian",
            "Morocco":"Moroccan",
            "Mozambique":"Mozambican",
            "Namibia":"Namibian",
            "Nepal":"Nepalese",
            "Netherlands":"Dutch",
            "New Zealand":"New Zealand",
            "Nicaragua":"Nicaraguan",
            "Nigeria":"Nigerian",
            "Norway":"Norwegian",
            "Pakistan":"Pakistani",
            "Panama":"Panamanian",
            "Paraguay":"Paraguayan",
            "Peru":"Peruvian",
            "Philippines":"Philippine",
            "Poland":"Polish",
            "Portugal":"Portuguese",
            "Romania":"Romanian",
            "Russia":"Russian",
            "Saudi Arabia":"Saudi",
            "Scotland":"Scottish",
            "Senegal":"Senegalese",
            "Serbia":"Serbian",
            "Singapore":"Singaporean",
            "Slovakia":"Slovak",
            "South Africa":"South African",
            "South Korea":"Korean",
            "Spain":"Spanish",
            "Sri Lanka":"Sri Lankan",
            "Sudan":"Sudanese",
            "Sweden":"Swedish",
            "Switzerland":"Swiss",
            "Syria":"Syrian",
            "Taiwan":"Taiwanese",
            "Tajikistan":"Tajikistani",
            "Thailand":"Thai",
            "Tonga":"Tongan",
            "Tunisia":"Tunisian",
            "Turkey":"Turkish",
            "Ukraine":"Ukrainian",
            "United Arab Emirates":"Emirati",
            "United Kingdom":"British",
            "United States":"American",
            "Uruguay":"Uruguayan",
            "Venezuela":"Venezuelan",
            "Vietnam":"Vietnamese",
            "Wales":"Welsh",
            "Zambia":"Zambian",
            "Zimbabwe":"Zimbabwean",
        }

        #update nationality
        Country = apps.get_model('core', 'Country')
        for country in Country.objects.all():
            nationality = nationalities.get(country.name)
            if nationality:
                country.nationality = nationality
                country.save()


    dependencies = [
        ('core', '0008_auto_20190529_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='nationality',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nationality'),
        ),
        migrations.RunPython(update_nationality),
    ]