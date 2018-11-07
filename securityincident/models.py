from django.contrib.gis.db import models
# from geodb.models import AfgShedaLvl4

class AfgIncidentOasis(models.Model):
    uid = models.IntegerField(db_column='UID', primary_key=True) # Field name made lowercase.
    xmin = models.FloatField(db_column='XMIN', blank=True, null=True) # Field name made lowercase.
    xmax = models.FloatField(db_column='XMAX', blank=True, null=True) # Field name made lowercase.
    ymin = models.FloatField(db_column='YMIN', blank=True, null=True) # Field name made lowercase.
    ymax = models.FloatField(db_column='YMAX', blank=True, null=True) # Field name made lowercase.
    id = models.CharField(db_column='ID', max_length=255, blank=True) # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=255, blank=True) # Field name made lowercase.
    type = models.CharField(db_column='TYPE', max_length=255, blank=True) # Field name made lowercase.
    target = models.CharField(db_column='TARGET', max_length=255, blank=True) # Field name made lowercase.
    dead = models.IntegerField(blank=True, null=True)
    affected = models.IntegerField(blank=True, null=True)
    violent = models.IntegerField(blank=True, null=True)
    injured = models.IntegerField(blank=True, null=True)
    incident_date = models.DateField(blank=True, null=True)
    time00 = models.CharField(max_length=255, blank=True)
    locdesc = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    town = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    scoring = models.IntegerField(blank=True, null=True)
    incident_dateserial = models.BigIntegerField(blank=True, null=True)
    wkb_geometry = models.PointField(blank=True, null=True)
    accumulative_affected = models.IntegerField(blank=True, null=True)
    main_type = models.CharField(max_length=255, blank=True)
    main_target = models.CharField(max_length=255, blank=True)
    prov_code = models.IntegerField(blank=True, null=True)
    dist_code = models.IntegerField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = True
        db_table = 'afg_incident_oasis'

class AfgIncidentOasisTemp(models.Model):
    uid = models.IntegerField(db_column='UID', primary_key=True) # Field name made lowercase.
    name = models.CharField(db_column='NAME', max_length=255, blank=True) # Field name made lowercase.
    type = models.CharField(db_column='TYPE', max_length=255, blank=True) # Field name made lowercase.
    target = models.CharField(db_column='TARGET', max_length=255, blank=True) # Field name made lowercase.
    dead = models.IntegerField(blank=True, null=True)
    affected = models.IntegerField(blank=True, null=True)
    violent = models.IntegerField(blank=True, null=True)
    injured = models.IntegerField(blank=True, null=True)
    incident_date = models.DateField(blank=True, null=True)
    locdesc = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    town = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    wkb_geometry = models.PointField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = True
        db_table = 'afg_incident_oasis_temp'
