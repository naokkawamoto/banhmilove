# Generated by Django 4.2.11 on 2024-05-28 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banhmilove_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('ranking', models.IntegerField()),
                ('weighted_score', models.FloatField()),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banhmilove_app.store')),
            ],
            options={
                'unique_together': {('date', 'store')},
            },
        ),
    ]
