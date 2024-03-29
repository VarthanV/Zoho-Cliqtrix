# Generated by Django 2.1.7 on 2019-09-11 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockapp', '0009_auto_20190909_2140'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseBookMark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('url', models.URLField()),
                ('tag', models.CharField(max_length=300)),
                ('title', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='title',
            field=models.TextField(),
        ),
    ]
