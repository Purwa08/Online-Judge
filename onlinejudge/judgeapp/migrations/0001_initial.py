# Generated by Django 4.2.2 on 2023-06-20 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('difficulty', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.TextField()),
                ('expected_output', models.TextField()),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judgeapp.problem')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judgeapp.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judgeapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actual_output', models.TextField()),
                ('is_passed', models.BooleanField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judgeapp.submission')),
                ('test_case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judgeapp.testcase')),
            ],
        ),
    ]
