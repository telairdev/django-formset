# Generated by Django 4.1.7 on 2023-04-20 21:21

from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models
import django.db.models.deletion

import formset.fields
import formset.richtext.fields


def initialize_opinions(apps, schema_editor):
    OpinionModel = apps.get_model('testapp', 'OpinionModel')
    for counter in range(1, 3000):
        label = f"Opinion {counter:04}"
        OpinionModel.objects.create(tenant=1, label=label)


def initialize_counties(apps, schema_editor):
    call_command('loaddata', settings.BASE_DIR / 'testapp/fixtures/counties.json', verbosity=0)
    CountyUnnormalized = apps.get_model('testapp', 'CountyUnnormalized')
    State = apps.get_model('testapp', 'State')
    County = apps.get_model('testapp', 'County')
    for county in CountyUnnormalized.objects.all():
        state, _ = State.objects.get_or_create(code=county.state_code, name=county.state_name)
        County.objects.create(state=state, name=county.county_name)


def initialize_reporters(apps, schema_editor):
    call_command('loaddata', settings.BASE_DIR / 'testapp/fixtures/reporters.json', verbosity=0)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', formset.richtext.fields.RichTextField()),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='CountyUnnormalized',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_code', models.CharField(max_length=2, verbose_name='State code')),
                ('state_name', models.CharField(db_index=True, max_length=20, verbose_name='State name')),
                ('county_name', models.CharField(max_length=30, verbose_name='County name')),
            ],
            options={
                'ordering': ['state_name', 'county_name'],
            },
        ),
        migrations.CreateModel(
            name='OpinionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant', models.PositiveSmallIntegerField()),
                ('label', models.CharField(max_length=50, verbose_name='Opinion')),
            ],
            options={
                'unique_together': {('tenant', 'label')},
            },
        ),
        migrations.CreateModel(
            name='PayloadModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='PollModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, verbose_name='Code')),
                ('name', models.CharField(db_index=True, max_length=20, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WeightedOpinion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.BigIntegerField(db_index=True, default=0, verbose_name='Weighted Opinion')),
                ('opinion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testapp.opinionmodel')),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testapp.pollmodel')),
            ],
            options={
                'ordering': ['weight'],
            },
        ),
        migrations.CreateModel(
            name='UserContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=25, null=True, verbose_name='Phone Number')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='pollmodel',
            name='weighted_opinions',
            field=formset.fields.SortableManyToManyField(through='testapp.WeightedOpinion', to='testapp.opinionmodel', verbose_name='Weighted Opinions'),
        ),
        migrations.CreateModel(
            name='PersonModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=50, verbose_name='Full Name')),
                ('avatar', models.FileField(blank=True, upload_to='images')),
                ('gender', models.CharField(choices=[('female', 'Female'), ('male', 'Male')], default=None, max_length=10, verbose_name='Gender')),
                ('birth_date', models.DateField(verbose_name='Birth Date')),
                ('continent', models.IntegerField(choices=[(1, 'America'), (2, 'Europe'), (3, 'Asia'), (4, 'Africa'), (5, 'Australia'), (6, 'Oceania'), (7, 'Antartica')], verbose_name='Continent')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
                ('opinion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='persons', to='testapp.opinionmodel', verbose_name='Opinion')),
                ('opinions', models.ManyToManyField(related_name='person_groups', to='testapp.opinionmodel', verbose_name='Opinions')),
            ],
        ),
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testapp.state')),
            ],
            options={
                'ordering': ['state', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Reporter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField()),
                ('headline', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='testapp.reporter')),
                ('teaser', models.FileField(blank=True, upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200)),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, verbose_name='Username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='Staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='ExtendUser',
            fields=[
                ('phone_number', models.CharField(blank=True, max_length=25, null=True, verbose_name='Phone Number')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='extend_user', serialize=False, to='testapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Company name')),
                ('created_by', models.CharField(db_index=True, editable=False, max_length=40)),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'unique_together': {('name', 'created_by')},
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Department name')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='testapp.company')),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'unique_together': {('name', 'company')},
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Team name')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='testapp.department')),
            ],
            options={
                'verbose_name': 'Team',
                'verbose_name_plural': 'Teams',
                'unique_together': {('name', 'department')},
            },
        ),
        migrations.RunPython(initialize_opinions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(initialize_counties, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(initialize_reporters, reverse_code=migrations.RunPython.noop),
    ]
