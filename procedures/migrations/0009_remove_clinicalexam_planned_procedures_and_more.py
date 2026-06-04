from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('procedures', '0008_remove_clinicalexam_planned_procedures_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicalexam',
            name='planned_procedures',
            field=models.ForeignKey(
                to='procedures.dentalprocedure',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                related_name='planned_exams',
            ),
        ),
    ]
