# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('BNS', 'Bonus')], max_length=3)),
                ('wagering_requirement', models.IntegerField()),
                ('action', models.CharField(choices=[('deposit', 'Deposit'), ('login', 'User login')], max_length=7)),
                ('min_amount', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
            ],
            options={
                'verbose_name_plural': 'bonuses',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_spent_money', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('BNS', 'Bonus')], max_length=3)),
                ('wagering_requirement', models.IntegerField()),
                ('created', models.DateTimeField(editable=False)),
                ('spent_money_on_start', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('depleted', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='casino.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
