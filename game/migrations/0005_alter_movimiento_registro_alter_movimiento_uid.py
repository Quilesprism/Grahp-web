# Generated by Django 5.0.8 on 2024-08-10 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_alter_movimiento_fecha_hora_alter_movimiento_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimiento',
            name='registro',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='movimiento',
            name='uid',
            field=models.CharField(max_length=200),
        ),
    ]
