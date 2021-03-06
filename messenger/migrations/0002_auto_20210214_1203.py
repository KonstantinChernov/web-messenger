# Generated by Django 3.1.6 on 2021-02-14 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messenger', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='interlocutor_1',
        ),
        migrations.RemoveField(
            model_name='message',
            name='interlocutor_2',
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('D', 'dialog'), ('C', 'chat')], default='D', max_length=1, verbose_name='type')),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='member')),
            ],
        ),
    ]
