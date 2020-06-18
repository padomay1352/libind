# Generated by Django 3.0.7 on 2020-06-18 14:21

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=150, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=254)),
                ('last_name', models.CharField(max_length=150)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('date_of_birth', models.DateTimeField(blank=True, null=True)),
                ('date_joined', models.DateTimeField()),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField()),
                ('is_staff', models.IntegerField(blank=True, null=True)),
                ('is_active', models.IntegerField(blank=True, null=True)),
                ('first_name', models.CharField(
                    blank=True, max_length=30, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BoardCategories',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=100)),
                ('category_description', models.CharField(max_length=100)),
                ('list_count', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Boards',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('board_type', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=300)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(
                    blank=True, null=True)),
                ('registered_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('last_update_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('view_count', models.IntegerField(blank=True, default=0)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to='library_search_app.BoardCategories')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BoardReplies',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(blank=True, null=True)),
                ('content', models.TextField()),
                ('registered_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('last_update_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('reference_reply_id', models.IntegerField(blank=True, null=True)),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to='library_search_app.Boards')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BoardLikes',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_date', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to='library_search_app.Boards')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
