from django.shortcuts import render
from .models import (
	AfgIncidentOasis,
	AfgIncidentOasisTemp,
	)
from geodb.models import (
	AfgAdmbndaAdm1,
	AfgAdmbndaAdm2,
	AfgAirdrmp,
	# AfgAvsa,
	AfgCapaGsmcvr,
	AfgCaptAdm1ItsProvcImmap,
	AfgCaptAdm1NearestProvcImmap,
	AfgCaptAdm2NearestDistrictcImmap,
	AfgCaptAirdrmImmap,
	AfgCaptHltfacTier1Immap,
	AfgCaptHltfacTier2Immap,
	AfgCaptHltfacTier3Immap,
	AfgCaptHltfacTierallImmap,
	AfgHltfac,
	# AfgIncidentOasis,
	AfgLndcrva,
	AfgPplp,
	AfgRdsl,
	districtsummary,
	# earthquake_events,
	# earthquake_shakemap,
	forecastedLastUpdate,
	LandcoverDescription,
	provincesummary,
	tempCurrentSC,
	# villagesummaryEQ,
	)
from geodb.geo_calc import (
	getCommonUse,
	# getFloodForecastBySource,
	# getFloodForecastMatrix,
	getGeoJson,
	getProvinceSummary_glofas,
	getProvinceSummary,
	getRawBaseLine,
	# getRawFloodRisk,
	# getSettlementAtFloodRisk,
	getShortCutData,
	getTotalArea,
	getTotalBuildings,
	getTotalPop,
	getTotalSettlement,
	getRiskNumber,
	)
from geodb.views import (
	get_nc_file_from_ftp,
	getCommonVillageData,
	)
# from geodb.geoapi import getRiskExecuteExternal
# from .riverflood import getFloodForecastBySource
from django.db import connection, connections
from django.db.models import Count, Sum
from geonode.maps.views import _resolve_map, _PERMISSION_MSG_VIEW
from geonode.utils import include_section, none_to_zero, query_to_dicts, RawSQL_nogroupby, ComboChart, dict_ext, linenum, list_ext
from matrix.models import matrix
from pprint import pprint
from pytz import timezone, all_timezones
from tastypie.cache import SimpleCache
from tastypie.resources import ModelResource, Resource
from urlparse import urlparse
from django.conf import settings
from netCDF4 import Dataset, num2date
from django.utils.translation import ugettext as _
from graphos.renderers import flot, gchart
from graphos.sources.simple import SimpleDataSource
from django.shortcuts import render_to_response
from django.template import RequestContext
import time, datetime
from geodb.radarchart import RadarChart
import json
from securitydb.models import SecureFeature
from tastypie.authorization import DjangoAuthorization

from .enumerations import *

def get_dashboard_meta():
	return {
		'pages': [
			{
				'name': 'security',
				'function': dashboard_security, 
				'template': 'dash_security.html',
				'menutitle': 'Humanitarian Access',
			},
		],
		'menutitle': 'Humanitarian Access',
	}

# def getQuickOverview(request, filterLock, flag, code, includes=[], excludes=[]):
# 	response = {}
# 	# response.update(getSecurity(request, filterLock, flag, code, excludes=['getListEQ']))
# 	rawFilterLock = filterLock if 'flag' in request.GET else None
# 	# if 'daterange' in request.GET:
# 	# 	daterange = request.GET.get('daterange')
# 	# elif 'daterange' in request.POST:
# 	# 	daterange = request.POST.get('daterange')
# 	daterange = request.GET.get('daterange') or request.POST.get('daterange') or None
# 	if not daterange:
# 		enddate = datetime.date.today()
# 		startdate = enddate - datetime.timedelta(days=365)
# 		daterange = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")

# 	response['main_type_child'] = getSAMParams(request, daterange, filterLock, flag, code, 'main_type')

# 	response['incident_type'] = request.GET.get('incident_type').split(',') or \
# 		request.POST.get('incident_type') or \
# 		(i['main_type'] for i in response['main_type_child'])
# 	# incident_target = request.GET.get('incident_target').split(',') or request.POST.get('incident_target') or []

# 	main_type_raw_data = getSAMParams(request, daterange, filterLock, flag, code, group='main_type', datafilter={'incident_type':response['incident_type']})
# 	# response['incident_type'] = (i['main_type'] for i in response['main_type_child'])
# 	# if 'incident_type' in request.GET:
# 	# 	response['incident_type'] = request.GET['incident_type'].split(',')
# 	response['incident_type_group']=[{
# 		'count':i['count'],
# 		'injured':i['injured'],
# 		'violent':i['violent']+i['affected'],
# 		'dead':i['dead'],
# 		'main_type':i['main_type'],
# 		'child':list(getSAMIncident(request, daterange, filterLock, flag, code, 'type', datafilter={'incident_type':[i['main_type']]})),
# 	} for i in main_type_raw_data]
# 	# for i in main_type_raw_data:
# 	# 	response['incident_type_group'].append({'count':i['count'],'injured':i['injured'],'violent':i['violent']+i['affected'],'dead':i['dead'],'main_type':i['main_type'],'child':list(getSAMIncident(request, daterange, filterLock, flag, code, 'type', i['main_type']))})

# 	return response

# moved from geodb.geo_calc

def getSecurity(request, filterLock, flag, code, includes=[], excludes=[], datafilter={}, response=dict_ext()):
	# rawFilterLock = None
	# if 'flag' in request.GET:
	#     rawFilterLock = filterLock
	#     filterLock = 'ST_GeomFromText(\''+filterLock+'\',4326)'

	# response = getCommonUse(request, flag, code)
	# response = dict_ext()

	# enddate = datetime.date.today()
	# startdate = datetime.date.today() - datetime.timedelta(days=365)
	# daterange = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")

	# if 'daterange' in request.GET:
	#     daterange = request.GET['daterange']

	# datestart, dateend = daterange.split(',')
	# daterange = ','.join([datestart+' 00:00:00.000000', dateend+' 23:59:59.999999'])

	daterange = datafilter.get('daterange')

	if include_section('total_casualties', includes, excludes):
		response.update(getIncidentCasualties(request, daterange, filterLock, flag, code))
	# rawCasualties = getIncidentCasualties(request, daterange, filterLock, flag, code)
	# for i in rawCasualties:
	# 	response[i]=rawCasualties[i]

	# dataHLT = []
	# dataHLT.append(['', '# of',  { 'role': 'annotation' }])
	# dataHLT.append(['Death',rawCasualties['total_dead'], rawCasualties['total_dead'] ])
	# dataHLT.append(['Violent',rawCasualties['total_violent'], rawCasualties['total_violent'] ])
	# dataHLT.append(['Injured',rawCasualties['total_injured'], rawCasualties['total_injured'] ])
	# dataHLT.append(['# Incidents',rawCasualties['total_incident'], rawCasualties['total_incident'] ])
	# response['casualties_chart'] = gchart.BarChart(
	#     SimpleDataSource(data=dataHLT),
	#     html_id="pie_chart1",
	#     options={
	#         'title': 'Security Incident Overview',
	#         'width': 300,
	#         'height': 300,
	#         'legend': { 'position': 'none' },

	#         'bars': 'horizontal',
	#         'axes': {
	#             'x': {
	#               '0': { 'side': 'top', 'label': '# of Casualties and Incident'}
	#             },

	#         },
	#         'bar': { 'groupWidth': '90%' },
	#         'chartArea': {'width': '50%'},
	#         'titleX':'# of Casualties and Incident',
	# })

	if include_section('incident_type', includes, excludes):
		response['main_type_child'] = getSAMParams(request, daterange, filterLock, flag, code, 'main_type')
		response['incident_type'] = datafilter.get('incident_type') or [i['main_type'] for i in response['main_type_child']]

		main_type_raw_data = getSAMParams(request, daterange, filterLock, flag, code, 'main_type', datafilter=datafilter)
		response['incident_type_group'] =[{
			'count':i['count'],
			'injured':i['injured'],
			'violent':i['violent']+i['affected'],
			'dead':i['dead'],
			'main_type':i['main_type'],
			'child':list(getSAMIncident(request, daterange, filterLock, flag, code, 'type', datafilter={'incident_type':[i['main_type']]}))
		} for i in main_type_raw_data]

	# data_main_type = []
	# data_main_type.append(['', 'incident',{ 'role': 'annotation' }, 'dead',{ 'role': 'annotation' }, 'violent',{ 'role': 'annotation' }, 'injured',{ 'role': 'annotation' } ])
	# for type_item in main_type_raw_data:
	#     data_main_type.append([type_item['main_type'],type_item['count'],type_item['count'], type_item['dead'], type_item['dead'], type_item['violent']+type_item['affected'], type_item['violent']+type_item['affected'], type_item['injured'], type_item['injured'] ])
	# response['main_type_chart'] = gchart.BarChart(
	#     SimpleDataSource(data=data_main_type),
	#     html_id="pie_chart2",
	#     options={
	#         'title': 'Incident type overview and casualties',
	#         'width': 450,
	#         'height': 450,
	#         'isStacked':'true',
	#         'bars': 'horizontal',
	#         'axes': {
	#             'x': {
	#               '0': { 'side': 'top', 'label': '# of Casualties and Incident'}
	#             },

	#         },
	#         'annotations': {
	#             'textStyle': {
	#                 'fontSize':7
	#             }
	#         },
	#         'bar': { 'groupWidth': '90%' },
	#         'chartArea': {'width': '60%', 'height': '90%'},
	#         'titleX':'# of incident and casualties',
	# })

	# data_main_type.append(['TYPE', 'incident', 'dead', 'violent', 'injured' ])
	# for type_item in main_type_raw_data:
	# 	data_main_type.append([type_item['main_type'],type_item['count'], type_item['dead'], (type_item['violent'] or 0)+(type_item['affected'] or 0), type_item['injured'] ])

	# data_main_type = ['TYPE', 'incident', 'dead', 'violent', 'injured' ]+[[
	# 	item['main_type'],
	# 	item['count'],
	# 	item['dead'],
	# 	(item['violent'] or 0)+(item['affected'] or 0),
	# 	item['injured'],
	# ]
	# for item in main_type_raw_data]

	# response['main_type_chart'] = RadarChart(SimpleDataSource(data=data_main_type),
	#         html_id="pie_chart2",
	#         options={
	#             'title': _('Number of Incident by Incident Type'),
	#             'col-included' : [
	#                 {'col-no':1,'name':_('Incidents'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['dead_casualties_type_chart'] = RadarChart(SimpleDataSource(data=data_main_type),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of dead casualties by Incident Type'),
	#             'col-included' : [
	#                 {'col-no':2,'name':_('Dead'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['injured_casualties_type_chart'] = RadarChart(SimpleDataSource(data=data_main_type),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of injured casualties by Incident Type'),
	#             'col-included' : [
	#                 {'col-no':4,'name':_('Violent'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['violent_casualties_type_chart'] = RadarChart(SimpleDataSource(data=data_main_type),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of affected person by Incident Type'),
	#             'col-included' : [
	#                 {'col-no':3,'name':_('Injured'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	if include_section('incident_target', includes, excludes):
		response['main_target_child'] = getSAMParams(request, daterange, filterLock, flag, code, 'main_target')
		response['incident_target'] = datafilter.get('incident_target') or [i['main_target'] for i in response['main_target_child']]

		main_target_raw_data = getSAMParams(request, daterange, filterLock, flag, code, 'main_target', datafilter=datafilter)
		response['incident_target_group'] = [{
			'count':i['count'],
			'injured':i['injured'],
			'violent':i['violent']+i['affected'],
			'dead':i['dead'],
			'main_target':i['main_target'],
			'child':list(getSAMIncident(request, daterange, filterLock, flag, code, 'target', datafilter={'incident_target':[i['main_target']]}))
		} for i in main_target_raw_data]

	# data_main_target = []
	# data_main_target.append(['', 'incident',{ 'role': 'annotation' }, 'dead',{ 'role': 'annotation' }, 'violent',{ 'role': 'annotation' }, 'injured',{ 'role': 'annotation' } ])
	# for type_item in main_target_raw_data:
	#      data_main_target.append([type_item['main_target'],type_item['count'],type_item['count'], type_item['dead'], type_item['dead'], type_item['violent']+type_item['affected'], type_item['violent']+type_item['affected'], type_item['injured'], type_item['injured'] ])

	# response['main_target_chart'] = gchart.BarChart(
	#     SimpleDataSource(data=data_main_target),
	#     html_id="pie_chart3",
	#     options={
	#         'title': 'Incident target overview and casualties',
	#         'width': 450,
	#         'height': 450,
	#         # 'legend': { 'position': 'none' },
	#         'isStacked':'true',
	#         'bars': 'horizontal',
	#         'axes': {
	#             'x': {
	#               '0': { 'side': 'top', 'label': '# of Casualties and Incident'}
	#             },

	#         },
	#         'annotations': {
	#             'textStyle': {
	#                 'fontSize':7
	#             }
	#         },
	#         'bar': { 'groupWidth': '90%' },
	#         'chartArea': {'width': '60%', 'height': '90%'},
	#         'titleX':'# of incident and casualties',
	# })
	# data_main_target.append(['Target', 'incident', 'dead', 'violent', 'injured' ])
	# for type_item in main_target_raw_data:
	#      data_main_target.append([type_item['main_target'],type_item['count'], type_item['dead'], (type_item['violent'] or 0)+(type_item['affected'] or 0), type_item['injured'] ])
	# response['main_target_chart'] = RadarChart(SimpleDataSource(data=data_main_target),
	#         html_id="pie_chart3",
	#         options={
	#             'title': _('Number of Incident by Incident Target'),
	#             'col-included' : [
	#                 {'col-no':1,'name':_('Incidents'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['dead_casualties_target_chart'] = RadarChart(SimpleDataSource(data=data_main_target),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of dead casualties by Incident Target'),
	#             'col-included' : [
	#                 {'col-no':2,'name':_('Dead'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['injured_casualties_target_chart'] = RadarChart(SimpleDataSource(data=data_main_target),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of injured casualties by Incident Target'),
	#             'col-included' : [
	#                 {'col-no':4,'name':_('Injured'),'fill':True}
	#             ]
	#         }
	#     ).get_image()

	# response['violent_casualties_target_chart'] = RadarChart(SimpleDataSource(data=data_main_target),
	#         html_id="pie_chart4",
	#         options={
	#             'title': _('Number of affected person by Incident Target'),
	#             'col-included' : [
	#                 {'col-no':3,'name':_('Injured'),'fill':True}
	#             ]
	#         }
	#     ).get_image()


	# for i in response['main_type_child']:
	# 	response['incident_type'].append(i['main_type'])

	# for i in response['main_target_child']:
	# 	response['incident_target'].append(i['main_target'])

	# if 'incident_type' in request.GET:
	# 	response['incident_type'] = request.GET['incident_type'].split(',')
	# 	# print response['incident_type']

	# if 'incident_target' in request.GET:
	# 	response['incident_target'] = request.GET['incident_target'].split(',')
	# 	# print response['incident_target']

	# data = getListIncidentCasualties(request, daterange, filterLock, flag, code)
	if include_section('lc_child', includes, excludes):
		response['lc_child'] = data = getListIncidentCasualties(request, daterange, filterLock, flag, code)

	if include_section('incident_list_100', includes, excludes):
		response['incident_list_100'] = getListIncidents(request, daterange, filterLock, flag, code)

	if include_section('GeoJson', includes, excludes):
		response['GeoJson'] = getGeoJson(request, flag, code)

	return response

def getListIncidentCasualties(request, daterange, filterLock, flag, code):
	response = []
	data = getProvinceSummary(filterLock, flag, code)
	for i in data:
		data ={}
		data['code'] = i['code']
		data['na_en'] = i['na_en']
		data['Population'] = i['Population']
		data['Area'] = i['Area']

		rawCasualties = getIncidentCasualties(request, daterange, filterLock, 'currentProvince', i['code'])
		for x in rawCasualties:
			data[x]=rawCasualties[x]

		response.append(data)
	return response

def getListIncidents(request, daterange, filterLock, flag, code):
	response = {}

	resource = SecureFeature.objects.all()
	date = daterange.split(',')

	if flag=='entireAfg':
		filterLock = ''
	elif flag =='currentProvince':
		filterLock = ''
		if len(str(code)) > 2:
			resource = resource.filter(scre_distid=code)
		else :
			resource = resource.filter(scre_provid=code)
	else:
		filterLock = filterLock

	if filterLock!='':
		resource = resource.filter(mpoint__contained=filterLock)

	if 'incident_type' in request.GET:
		resource = resource.filter(scre_eventid__evnt_name__in=request.GET['incident_type'].split(','))

	if 'incident_target' in request.GET:
		resource = resource.filter(scre_incidenttarget__inct_name__in=request.GET['incident_target'].split(','))

	resource = resource.filter(scre_incidentdate__gt=date[0],scre_incidentdate__lt=date[1]).order_by('-scre_incidentdate')

	resource = resource.extra(select={'incident_date': 'scre_incidentdate', 'description': "scre_notes"})
	resource = resource.values('incident_date','description')[:100]
	return resource

def getSAMIncident(request, daterange, filterLock, flag, code, type_name, datafilter={}):

	def joinnedname(oldname):
		names = {
			'main_type': 'scre_eventid__evnt_cat__cat_name',
			'type': 'scre_eventid__evnt_name',
			'main_target': 'scre_incidenttarget__inct_catid__cat_name',
			'target': 'scre_incidenttarget__inct_name',
		}
		if oldname in names:
			return names[oldname]
		else:
			return oldname

	def colname(oldname):
		names = {
			'main_type': 'afg_scr_eventtypecat.cat_name',
			'type': 'afg_scr_eventtype.evnt_name',
			'main_target': 'afg_scr_incidenttargetcat.cat_name',
			'target': 'afg_scr_incidenttarget.inct_name',
		}
		if oldname in names:
			return names[oldname]
		else:
			return oldname

	# response = {}
	resource = SecureFeature.objects.all()
	# if type_name == 'main_type':
	# 	resource = resource.filter(scre_eventid__evnt_cat__cat_name_in=type_values)
	# elif type_name == 'main_target':
	# 	resource = resource.filter(scre_incidenttarget__inct_catid__cat_name_in=type_values)
	date = daterange.split(',')

	if flag=='entireAfg':
		filterLock = ''
	elif flag =='currentProvince':
		filterLock = ''
		if len(str(code)) > 2:
			resource = resource.filter(scre_distid=code)
		else :
			resource = resource.filter(scre_provid=code)
	# else:
	# 	filterLock = filterLock

	if filterLock:
		resource = resource.filter(mpoint__contained=filterLock)

	# if 'incident_type' in request.GET:
	# 	resource = resource.filter(scre_eventid__evnt_cat__cat_name__in=request.GET['incident_type'].split(','))

	# if 'incident_target' in request.GET:
	# 	resource = resource.filter(scre_incidenttarget__inct_catid__cat_name__in=request.GET['incident_target'].split(','))

	if datafilter.get('incident_type'):
		resource = resource.filter(scre_eventid__evnt_cat__cat_name__in=datafilter['incident_type'])

	if datafilter.get('incident_target'):
		resource = resource.filter(scre_incidenttarget__inct_catid__cat_name__in=datafilter['incident_target'])

	resource = resource.\
		filter(scre_incidentdate__gt=date[0], scre_incidentdate__lt=date[1]).\
		extra(select={type_name: colname(type_name)}).\
		values(joinnedname(type_name), type_name).\
		annotate(
			count=Count('id'),
			injured=Sum('scre_injured'),
			dead=Sum('scre_dead'),
			affected=RawSQL_nogroupby('0',()),
			violent=RawSQL_nogroupby('sum(case when scre_violent then 1 else 0 end)',())
		).\
		order_by(type_name) 
		# alias for column in related table:
		# joinnedname(type_name) is a dummy select to make sql join and then colname(type_name) can be called to select column real name directly
		# alternative for django 1.8+: annotate(**{type_name:F(joinnedname(type_name))}).values(type_name)
		# affected is dummy for compatibility

	print linenum(), 'type_name:%s'%(type_name)
	print resource.query

	return resource

def getSAMParams(request, daterange, filterLock, flag, code, group, datafilter={}):

	resource = AfgIncidentOasis.objects.all()
	datestart, dateend = daterange.split(',')

	if flag=='entireAfg':
		filterLock = ''
	elif flag =='currentProvince':
		filterLock = ''
		if len(str(code)) > 2:
			resource = resource.filter(dist_code=code)
		else :
			resource = resource.filter(prov_code=code)
	else:
		filterLock = filterLock

	if filterLock:
		resource = resource.filter(wkb_geometry__intersects=filterLock)

	# if includeFilter and request.GET.get('incident_type', ''):
	# 	resource = resource.filter(main_type__in=request.GET['incident_type'].split(','))

	# if includeFilter and request.GET.get('incident_target', ''):
	# 	resource = resource.filter(main_target__in=request.GET['incident_target'].split(','))

	if datafilter.get('incident_type'):
		resource = resource.filter(main_type__in=datafilter['incident_type'])

	if datafilter.get('incident_target'):
		resource = resource.filter(main_target__in=datafilter['incident_target'])

	resource = resource.\
		filter(incident_date__gt=datestart,incident_date__lt=dateend).\
		values(group).\
		annotate(
			count=Count('uid'), 
			affected=Sum('affected'), 
			injured=Sum('injured'), 
			violent=Sum('violent'), 
			dead=Sum('dead')
		).\
		order_by(group)
	print linenum(), resource.query

	return resource

def getIncidentCasualties(request, daterange, filterLock, flag, code):
	response = {}
	resource = SecureFeature.objects.all()
	date = daterange.split(',')

	if flag=='entireAfg':
		filterLock = ''
	elif flag =='currentProvince':
		filterLock = ''
		if len(str(code)) > 2:
			resource = resource.filter(scre_distid=code)
		else :
			resource = resource.filter(scre_provid=code)
	else:
		filterLock = filterLock

	if filterLock!='':
		resource = resource.filter(mpoint__contained=filterLock)

	resource = resource.filter(scre_incidentdate__gt=date[0],scre_incidentdate__lt=date[1])

	if 'incident_type' in request.GET:
		resource = resource.filter(scre_eventid__evnt_name__in=request.GET['incident_type'].split(','))

	if 'incident_target' in request.GET:
		resource = resource.filter(scre_incidenttarget__inct_name__in=request.GET['incident_target'].split(','))

	resource1 = resource.aggregate(count=Count('id'), injured=Sum('scre_injured'), dead=Sum('scre_dead'))
	# print resource.query
	resource2 = resource.extra(select={'violent':"sum(case when scre_violent then 1 else 0 end)", 'affected':'sum(0)'}).values('violent', 'affected') # affected is dummy
	# print resource2.query

	response['total_incident'] = resource1['count'] if resource1['count'] != None else 0
	response['total_injured'] = resource1['injured'] if resource1['injured'] != None else 0
	response['total_violent'] = resource2[0]['violent'] if resource2[0]['violent'] != None else 0 +resource2[0]['affected'] if resource2[0]['affected'] != None else 0
	response['total_dead'] = resource1['dead'] if resource1['dead'] != None else 0

	return response

# moved from geodb.geoapi

# lanjutan clone dari api.py
class getSAMParameters(ModelResource):
	"""inicidents type and target api"""

	class Meta:
		authorization = DjangoAuthorization()
		resource_name = 'sam_params'
		allowed_methods = ['post']
		detail_allowed_methods = ['post']
		always_return_data = True
		object_class=None

	def post_list(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		response = self.getStats(request)
		return self.create_response(request, response)   

	def getStats(self, request):
		# print str(request.POST['query_type']) #.strip('[]')
		# print request.POST
		query_filter_group = []
		temp_group = dict(request.POST)['query_type']
		filterLock = dict(request.POST)['filterlock']
		# print filterLock

		response = {}
		response['objects'] = []

		resource = AfgIncidentOasis.objects.all()

		if filterLock[0]:
			resource = resource.filter(wkb_geometry__intersects=filterLock[0])

		group_title = subgroup_title = None
		if len(temp_group)==1:
			group_title = temp_group[0]
			resource = resource.filter(incident_date__gt=request.POST['start_date'],incident_date__lt=request.POST['end_date'])           
			resource = resource.values(group_title).annotate(count=Count('uid'), affected=Sum('affected'), injured=Sum('injured'), violent=Sum('violent'), dead=Sum('dead')).order_by(group_title)       
		elif len(temp_group)==2:
			group_title, subgroup_title = temp_group
			stat_type_filter = dict(request.POST)['incident_type']
			stat_target_filter = dict(request.POST)['incident_target']
			
			resource = resource.filter(incident_date__gt=request.POST['start_date'],incident_date__lt=request.POST['end_date'])

			if stat_type_filter[0]=='':
				resource = resource
			else:
				resource = resource.filter(main_type__in=stat_type_filter)

			if stat_target_filter[0]=='':   
				resource = resource
			else:
				resource = resource.filter(main_target__in=stat_target_filter)
			
			resourceAgregate = resource
			resource = resource.values(group_title,subgroup_title).annotate(count=Count('uid'), affected=Sum('affected'), injured=Sum('injured'), violent=Sum('violent'), dead=Sum('dead')).order_by(group_title,subgroup_title)
			resourceAgregate = resourceAgregate.aggregate(count=Count('uid'), affected=Sum('affected'), injured=Sum('injured'), violent=Sum('violent'), dead=Sum('dead'))

			response['total_incident'] = resourceAgregate['count']
			response['total_injured'] = resourceAgregate['injured']
			response['total_violent'] = resourceAgregate['violent']
			response['total_dead'] = resourceAgregate['dead']

		response['values'] = []
		response['values_titles'] = [_('Title')]+[_(CASUALTY_TYPES[i]) for i in ['count','dead','injured','violent',]]
		if subgroup_title and len(resource):
			group = {'title':resource[0][group_title],'values':[]}
		for i in resource:
			i['visible']=True
			response['objects'].append(i)
			value = [
				i[subgroup_title or group_title],
				i['count'],
				i['dead'],
				i['injured'],
				i['violent'],
			]
			if subgroup_title:
				group['values'].append(value)
				is_newgroup = bool(group['title'] != i[group_title])
				is_lastloop = bool(i is resource[len(resource)-1])
				if is_newgroup or is_lastloop:
					response['values'].append(group)
					group = {'title':i[group_title],'values':[],}
			else:
				response['values'].append(value)

		# response['objects'] = resource
		response['total_count'] = resource.count()

		with connections['geodb'].cursor() as cursor:
			cursor.execute("SELECT last_incidentdate, last_sync FROM ref_security ORDER BY id DESC LIMIT 1")
			row = cursor.fetchall()
			# cursor.close()

			if row:
				response['last_incidentdate'] = row[0][0].strftime("%Y-%m-%d")
				response['last_incidentsync'] = row[0][1].strftime("%Y-%m-%d")

				date_N_days_ago = datetime.date.today() - row[0][0]
				response['last_incidentdate_ago'] = str(date_N_days_ago).split(',')[0]

				response['color_code'] = 'black'

				if date_N_days_ago <= datetime.timedelta(days=2):
					response['color_code'] = 'green'
				elif date_N_days_ago > datetime.timedelta(days=2) and date_N_days_ago <= datetime.timedelta(days=4):
					response['color_code'] = 'yellow'
				elif date_N_days_ago > datetime.timedelta(days=4) and date_N_days_ago <= datetime.timedelta(days=5):
					response['color_code'] = 'orange'
				elif date_N_days_ago > datetime.timedelta(days=5):
					response['color_code'] = 'red'

				# date_N_days_ago = datetime.date.today() - row[0][1]
				# response['last_incidentsync_ago'] = str(date_N_days_ago).split(',')[0]

		response = dict_ext(response).without('objects')

		return none_to_zero(response)

	def getStats2(self, request):

		def newname(oldname):
			names = {
				'main_type': 'scre_eventid__evnt_cat__cat_name',
				'type': 'scre_eventid__evnt_name',
				'main_target': 'scre_incidenttarget__inct_catid__cat_name',
				'target': 'scre_incidenttarget__inct_name',
			}
			if oldname in names:
				return names[oldname]
			else:
				return oldname

		def colname(oldname):
			names = {
				'main_type': 'afg_scr_eventtypecat.cat_name',
				'type': 'afg_scr_eventtype.evnt_name',
				'main_target': 'afg_scr_incidenttargetcat.cat_name',
				'target': 'afg_scr_incidenttarget.inct_name',
			}
			if oldname in names:
				return names[oldname]
			else:
				return oldname

		# print str(request.POST['query_type']) #.strip('[]')
		# print request.POST
		query_filter_group = []
		temp_group = dict(request.POST)['query_type']
		filterLock = dict(request.POST)['filterlock']
		# print filterLock

		response = {}
		response['objects'] = []

		resource = SecureFeature.objects.all()

		if filterLock[0]!='':
			resource = resource.filter(mpoint__contained=filterLock[0])

		if len(temp_group)==1:
			resource = resource.\
				filter(
					scre_incidentdate__gt=request.POST['start_date'],
					scre_incidentdate__lt=request.POST['end_date']
					).\
				extra(select={
					temp_group[0]: colname(temp_group[0]), 
					}).\
				values(temp_group[0]).\
				annotate(\
					count=Count('id'),
					injured=Sum('scre_injured'),
					dead=Sum('scre_dead'),
					affected=RawSQL_nogroupby('0',()),
					violent=RawSQL_nogroupby('sum(case when scre_violent then 1 else 0 end)',())
					).\
				order_by(newname(temp_group[0]))
		elif len(temp_group)==2:
			stat_type_filter = dict(request.POST)['incident_type'];
			stat_target_filter = dict(request.POST)['incident_target'];

			resource = resource.filter(scre_incidentdate__gt=request.POST['start_date'],scre_incidentdate__lt=request.POST['end_date'])

			if stat_type_filter[0]=='':
				resource = resource
			else:
				resource = resource.filter(scre_eventid__evnt_name__in=stat_type_filter)

			if stat_target_filter[0]=='':
				resource = resource
			else:
				resource = resource.filter(scre_incidenttarget__inct_name__in=stat_target_filter)

			resourceAgregate2 = resourceAgregate = resource
			resource = resource.extra(select={temp_group[0]: colname(temp_group[0]), temp_group[1]: colname(temp_group[1])})
			resource = resource.values(temp_group[0], temp_group[1]).annotate(count=Count('id'), affected=RawSQL_nogroupby('0',()), injured=Sum('scre_injured'), dead=Sum('scre_dead'), violent=RawSQL_nogroupby('sum(case when scre_violent then 1 else 0 end)',())).order_by(newname(temp_group[0]),newname(temp_group[1]))

			resourceAgregate = resourceAgregate.aggregate(count=Count('id'), affected=Sum('scre_injured'), injured=Sum('scre_injured'), dead=Sum('scre_dead'), violent=RawSQL_nogroupby('sum(case when scre_violent then 1 else 0 end)',()))
			response['total_incident'] = resourceAgregate['count']
			response['total_injured'] = resourceAgregate['injured']
			response['total_dead'] = resourceAgregate['dead']
			response['total_violent'] = resourceAgregate['violent']

			# resourceAgregate2 = resourceAgregate2.annotate(violent=RawSQL_nogroupby('sum(case when scre_violent then 1 else 0 end)',()))
			# response['total_violent'] = resourceAgregate2[0]['violent']

		# print resource.query
		for i in resource:
			i['visible']=True
			response['objects'].append(i)
		# response['objects'] = resource
		response['total_count'] = resource.count()

		with connections['geodb'].cursor() as cursor:
			cursor.execute("SELECT last_incidentdate, last_sync FROM ref_security ORDER BY id DESC LIMIT 1")
			row = cursor.fetchall()
			# cursor.close()

			if row:
				response['last_incidentdate'] = row[0][0].strftime("%Y-%m-%d")
				response['last_incidentsync'] = row[0][1].strftime("%Y-%m-%d")

				date_N_days_ago = datetime.date.today() - row[0][0]
				response['last_incidentdate_ago'] = str(date_N_days_ago).split(',')[0]

				response['color_code'] = 'black'

				if date_N_days_ago <= datetime.timedelta(days=2):
					response['color_code'] = 'green'
				elif date_N_days_ago > datetime.timedelta(days=2) and date_N_days_ago <= datetime.timedelta(days=4):
					response['color_code'] = 'yellow'
				elif date_N_days_ago > datetime.timedelta(days=4) and date_N_days_ago <= datetime.timedelta(days=5):
					response['color_code'] = 'orange'
				elif date_N_days_ago > datetime.timedelta(days=5):
					response['color_code'] = 'red'

				# date_N_days_ago = datetime.date.today() - row[0][1]
				# response['last_incidentsync_ago'] = str(date_N_days_ago).split(',')[0]

		return none_to_zero(response)

# lanjutan clone dari api.py
class getIncidentsRaw(ModelResource):
	"""Incidents raw api"""

	class Meta:
		authorization = DjangoAuthorization()
		resource_name = 'incident_raw'
		allowed_methods = ['post']
		detail_allowed_methods = ['post']
		always_return_data = True
		object_class=None

	def post_list(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		response = self.getStats(request)
		return self.create_response(request, response)   

	def getStats(self, request):
		query_filter_group = []
		temp_group = dict(request.POST)['query_type']
		filterLock = dict(request.POST)['filterlock']

		response = {}
		response['objects'] = []

		resource = AfgIncidentOasis.objects.all()

		if filterLock[0]!='':
			resource = resource.filter(wkb_geometry__intersects=filterLock[0])

		if len(temp_group)==1:
			resource = resource.filter(incident_date__gt=request.POST['start_date'],incident_date__lt=request.POST['end_date']).order_by('-incident_date')
		elif len(temp_group)==2:
			stat_type_filter = dict(request.POST)['incident_type']
			stat_target_filter = dict(request.POST)['incident_target']
			
			resource = resource.filter(incident_date__gt=request.POST['start_date'],incident_date__lt=request.POST['end_date']).order_by('-incident_date')

			if stat_type_filter[0]=='':
				resource = resource
				# resource = AfgIncidentOasis.objects.filter(incident_date__gt=request.POST['start_date'],incident_date__lt=request.POST['end_date']).values(temp_group[0],temp_group[1]).annotate(count=Count('uid'), affected=Sum('affected'), injured=Sum('injured'), violent=Sum('violent'), dead=Sum('dead')).order_by(temp_group[0],temp_group[1])
			else:
				resource = resource.filter(main_type__in=stat_type_filter)

			if stat_target_filter[0]=='':   
				resource = resource[:100]
			else:
				resource = resource.filter(main_target__in=stat_target_filter)[:100]
			
			
		for i in resource:
			response['objects'].append({
				'date':i.incident_date,
				'desc':i.description
			})
		response['values_titles'] = [_('Date'),_('Description'),]
		response['values'] = [[i.incident_date,i.description,] for i in resource]

		response['total_count'] = resource.count()

		with connections['geodb'].cursor() as cursor:
			cursor.execute("SELECT last_incidentdate, last_sync FROM ref_security ORDER BY id DESC LIMIT 1")  
			row = cursor.fetchall()
		
			if row:
				response['last_incidentdate'] = row[0][0].strftime("%Y-%m-%d")
				response['last_incidentsync'] = row[0][1].strftime("%Y-%m-%d")

				# cursor.close()

		response = dict_ext(response).without('objects')

		return none_to_zero(response)

	def getStats2(self, request):
		query_filter_group = []
		temp_group = dict(request.POST)['query_type']
		filterLock = dict(request.POST)['filterlock']

		response = {}
		response['objects'] = []

		resource = SecureFeature.objects.all()

		if filterLock[0]!='':
			resource = resource.filter(mpoint__contained=filterLock[0])

		if len(temp_group)==1:
			resource = resource.filter(scre_incidentdate__gt=request.POST['start_date'],scre_incidentdate__lt=request.POST['end_date']).order_by('-scre_incidentdate')
		elif len(temp_group)==2:
			stat_type_filter = dict(request.POST)['incident_type'];
			stat_target_filter = dict(request.POST)['incident_target'];

			resource = resource.filter(scre_incidentdate__gt=request.POST['start_date'],scre_incidentdate__lt=request.POST['end_date']).order_by('-scre_incidentdate')

			if stat_type_filter[0]=='':
				resource = resource
				# resource = AfgIncidentOasis.objects.filter(scre_incidentdate__gt=request.POST['start_date'],scre_incidentdate__lt=request.POST['end_date']).values(temp_group[0],temp_group[1]).annotate(count=Count('uid'), affected=Sum('affected'), injured=Sum('injured'), violent=Sum('violent'), dead=Sum('dead')).order_by(temp_group[0],temp_group[1])
			else:
				resource = resource.filter(scre_eventid__evnt_name__in=stat_type_filter)

			if stat_target_filter[0]=='':
				resource = resource[:100]
			else:
				resource = resource.filter(scre_incidenttarget__inct_name__in=stat_target_filter)[:100]


		for i in resource:
			response['objects'].append({
				'date':i.scre_incidentdate,
				'desc':i.scre_notes
			})

		response['total_count'] = resource.count()

		with connections['geodb'].cursor() as cursor:
			cursor.execute("SELECT last_incidentdate, last_sync FROM ref_security ORDER BY id DESC LIMIT 1")
			row = cursor.fetchall()

			if row:
				response['last_incidentdate'] = row[0][0].strftime("%Y-%m-%d")
				response['last_incidentsync'] = row[0][1].strftime("%Y-%m-%d")

			# cursor.close()

		return none_to_zero(response)

def get_datafilter(source):

	if 'daterange' in source:
		daterange = source['daterange']
	else:
		enddate = datetime.date.today()
		startdate = datetime.date.today() - datetime.timedelta(days=365)
		daterange = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")

	datafilter = {
		'daterange':daterange,
		'incident_type':filter(None,source.get('incident_type','').split(',')),
		'incident_target':filter(None,source.get('incident_target','').split(',')),	
	}

	return datafilter

def dashboard_security(request, filterLock, flag, code, includes=[], excludes=[], datafilter={}, response=dict_ext()):

	datafilter = datafilter or get_datafilter(request.GET)

	# incident_type = request.GET.get('incident_type','').split(',')
	# incident_target = request.GET.get('incident_target','').split(',')

	# response = dict_ext()

	if include_section('getCommonUse', includes, excludes):
		response.update(getCommonUse(request, flag, code))

	response['source'] = source = response.pathget('cache','getSecurity') or dict_ext(getSecurity(request, filterLock, flag, code, includes=includes, excludes=excludes, datafilter=datafilter))
	panels = response.path('panels')
	barcharts = response.path('panels','charts','bar')
	spidercharts = response.path('panels','charts','spider')
	tables = response.path('panels','tables')

	# titles = {
	# 	'casualties':{
	# 		'number_of_casualties_by_incident_type':'Number of Casualties by Incident Type',
	# 		'number_of_casualties_by_target_type':'Number of Casualties by Target Type', 
	# 	},
	# 	'incidents':{
	# 		'number_of_incidents_by_incident_type':'Number of Incidents by Incident Type',
	# 		'number_of_incidents_by_target_type':'Number of Incidents by Target Type',
	# }
	# labels = {
	# 	'type':source['incident_type'],
	# 	'target':source['incident_target'],
	# }
	# numbersource = {
	# 	'type':source['incident_type_group'],
	# 	'target':source['incident_target_group'],
	# }
	# for k,t in titles.items():
	# 	barcharts.path(k)['key'] = k
	# 	barcharts.path(k)['title'] = t
	# 	barcharts.path(k)['labels'] = source['incident_type']
	# 	barcharts.path(k)['child'] = [{
	# 		'name':CASUALTY_TYPES[t],
	# 		'data':[i[t] for i in source['incident_type_group']]
	# 	} for t in CASUALTY_TYPES_ORDER]

	if source.containall('incident_type','incident_type_group'):

		k = 'number_of_casualties_by_incident_type'
		barcharts[k] = {
			'key':k,
			'title':'Number of Casualties by Incident Type',
			'labels':source['incident_type'],
			'child':[{
				'name':CASUALTY_TYPES[t],
				'data':[i[t] for i in source['incident_type_group']]
			} for t in ['dead','injured']],
		}

		k = 'number_of_incidents_by_incident_type'
		barcharts[k] = {
			'key':k,
			'title':'Number of Incidents by Incident Type',
			'labels':source['incident_type'],
			'child':[{
				'name':CASUALTY_TYPES[t],
				'data':[i[t] for i in source['incident_type_group']]
			} for t in ['count','violent']],
		}

		chart = spidercharts.path('graph_of_incident_and_casualties_trend_by_incident_type')
		chart['key'] = 'graph_of_incident_and_casualties_trend_by_incident_type'
		chart['title'] = 'Graph of Incident and Casualties Trend by Incident Type'
		chart['labels'] = source['incident_type']
		chart['labels_all'] = [{
			'name':t['main_type'],
			'count':t['count'],
			'selected':t['main_type'] in source['incident_type'],
		} for t in source['main_type_child']]
		chart['child'] = [{
			'type':CASUALTY_TYPES[t],
			'data':[i[t] for i in source['incident_type_group']]
		} for t in CASUALTY_TYPES_ORDER]

	if source.containall('incident_target','incident_target_group'):

		k = 'number_of_casualties_by_target_type'
		barcharts[k] = {
			'key':k,
			'title':'Number of Casualties by Target Type',
			'labels':source['incident_target'],
			'child':[{
				'name':CASUALTY_TYPES[t],
				'data':[i[t] for i in source['incident_target_group']]
			} for t in ['dead','injured']],
		}

		k = 'number_of_incidents_by_target_type'
		barcharts[k] = {
			'key':k,
			'title':'Number of Incidents by Target Type',
			'labels':source['incident_target'],
			'child':[{
				'name':CASUALTY_TYPES[t],
				'data':[i[t] for i in source['incident_target_group']]
			} for t in ['count','violent']],
		}

		chart = spidercharts.path('graph_of_incident_and_casualties_trend_by_target_type')
		chart['key'] = 'graph_of_incident_and_casualties_trend_by_target_type'
		chart['title'] = 'Graph of Incident and Casualties Trend by Target Type'
		chart['labels'] = source['incident_target']
		chart['labels_all'] = [{
			'name':t['main_target'],
			'count':t['count'],
			'selected':t['main_target'] in source['incident_target'],
		} for t in source['main_target_child']]
		chart['child'] = [{
			'type':CASUALTY_TYPES[t],
			'data':[i[t] for i in source['incident_target_group']]
		} for t in CASUALTY_TYPES_ORDER]

	# titles = {
	# 	'number_of_casualties_by_target_type':'Number of Casualties by Target Type', 
	# 	'number_of_incidents_by_target_type':'Number of Incidents by Target Type'
	# }
	# for k,t in titles.items():
	# 	barcharts.path(k)['key'] = k
	# 	barcharts.path(k)['title'] = t
	# 	barcharts.path(k)['labels'] = source['incident_target']
	# 	barcharts.path(k)['child'] = [{
	# 		'name':CASUALTY_TYPES[t],
	# 		'data':[i[t] for i in source['incident_target_group']]
	# 	} for t in CASUALTY_TYPES_ORDER]

	# titles = {
	# 	'graph_of_incident_and_casualties_trend_by_incident_type':'Graph of Incident and Casualties Trend by Incident Type', 
	# 	'graph_of_incident_and_casualties_trend_by_target_type':'Graph of Incident and Casualties Trend by Target Type'
	# }
	# for k,t in titles.items():
	# 	spidercharts.path(k)['key'] = k
	# 	spidercharts.path(k)['title'] = t
	# 	spidercharts.path(k)['labels'] = source['incident_type']
	# 	spidercharts.path(k)['child'] = [{
	# 		'type':CASUALTY_TYPES[t],
	# 		'data':[i[t] for i in source['incident_type_group']]
	# 	} for t in CASUALTY_TYPES_ORDER]

	if source.containall('incident_target_group'):
		table = tables['incidents_and_casualties_by_incident_type'] = dict_ext()
		table['key'] = 'incidents_and_casualties_by_incident_type'
		table['title'] = _('Incidents and Casualties by Incident Type')
		table['child'] = []
		for i in source['incident_type_group']:
			table['child'] += [{
				'isgroup':True,
				'value':[i['main_type'],i['count'],i['violent'],i['injured'],i['dead']],
			}] + [{
				'value':[j['type'],j['count'],j['violent'],j['injured'],j['dead']],
			} for j in i['child']]

	if source.containall('incident_target_group'):
		table = tables['incident_and_casualties_trend_by_target_type'] = dict_ext()
		table['key'] = 'incident_and_casualties_trend_by_target_type'
		table['title'] = _('Incidents and Casualties by Target Type')
		table['child'] = []
		for i in source['incident_target_group']:
			table['child'] += [{
				'isgroup':True,
				'value':[i['main_target'],i['count'],i['violent'],i['injured'],i['dead']],
			}] + [{
				'value':[j['target'],j['count'],j['violent'],j['injured'],j['dead']],
			} for j in i['child']]

	if source.containall('parent_label') and source.containall('lc_child','total_incident','total_violent','total_injured','total_dead'):
		tables['number_of_incident_and_casualties_overview'] = {
			'title':_('Number of Incident and Casualties Overview'),
			'key':'number_of_incident_and_casualties_overview',
			'parentdata':[response['parent_label'],source['total_incident'],source['total_violent'],source['total_injured'],source['total_dead']],
			'child':[{
				'code':i['code'],
				'value':[i['na_en'],i['total_incident'],i['total_violent'],i['total_injured'],i['total_dead']],
			}
			for i in source['lc_child']],
		}

	if source.containall('incident_target','incident_list_100'):
		tables['list_of_latest_incidents'] = {
			'title':_('List of Latest Incidents'),
			'key':'list_of_latest_incidents',
			'child':[[i['incident_date'],i['description'],] for i in source['incident_list_100']],
		}

	if include_section('GeoJson', includes, excludes):
		response['GeoJson'] = geojsonadd_security(response)

	return response

class SecurityStatisticResource(ModelResource):

	class Meta:
		# authorization = DjangoAuthorization()
		resource_name = 'statistic_security'
		allowed_methods = ['post']
		detail_allowed_methods = ['post']
		cache = SimpleCache()
		object_class=None
		# always_return_data = True
 
	def getRisk(self, request):

		p = urlparse(request.META.get('HTTP_REFERER')).path.split('/')
		mapCode = p[3] if 'v2' in p else p[2]
		map_obj = _resolve_map(request, mapCode, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)

		queryset = matrix(user=request.user,resourceid=map_obj,action='Interactive Calculation')
		queryset.save()

		requestbody = boundaryFilter = json.loads(request.body)

		wkts = ['ST_GeomFromText(\''+i+'\',4326)' for i in boundaryFilter['spatialfilter']]
		bring = wkts[-1] if len(wkts) else None
		filterLock = 'ST_Union(ARRAY['+', '.join(wkts)+'])'

		response = getSecurityStatistic(request, filterLock, boundaryFilter.get('flag'), boundaryFilter.get('code'), requestbody=requestbody)

		return response

	def post_list(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		response = self.getRisk(request)
		return self.create_response(request, response)  

def getSecurityStatistic(request,filterLock, flag, code, requestbody={}):

	if 'daterange' in requestbody:
		daterange = requestbody['daterange']
	else:
		enddate = datetime.date.today()
		startdate = datetime.date.today() - datetime.timedelta(days=365)
		daterange = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")

	datafilter = {
		'daterange':daterange,
		'incident_type':filter(None,requestbody.get('incident_type',[])),
		'incident_target':filter(None,requestbody.get('incident_target',[])),	
	}

	response_dashboard = dashboard_security(request, filterLock, flag, code, datafilter=datafilter)
	panels_list = dict_ext()

	panels_list.path('charts')['bar'] = dict_ext(response_dashboard['panels']['charts']['bar']).valueslistbykey(['number_of_casualties_by_incident_type','number_of_incidents_by_incident_type','number_of_casualties_by_target_type','number_of_incidents_by_target_type',])
	panels_list.path('charts')['spider'] = dict_ext(response_dashboard['panels']['charts']['spider']).valueslistbykey(['graph_of_incident_and_casualties_trend_by_incident_type','graph_of_incident_and_casualties_trend_by_target_type',])
	panels_list['tables'] = dict_ext(response_dashboard['panels']['tables']).valueslistbykey(['incidents_and_casualties_by_incident_type','incident_and_casualties_trend_by_target_type','number_of_incident_and_casualties_overview','list_of_latest_incidents',])

	return {'panels_list':panels_list}

def geojsonadd_security(response):

	source = response['source']
	boundary = source['GeoJson']
	source['lc_child_dict'] = {v['code']:v for v in source['lc_child']}

	for k,v in enumerate(boundary.get('features',[])):
		boundary['features'][k]['properties'] = prop = dict_ext(boundary['features'][k]['properties'])

		# Checking if it's in a district
		if response['areatype'] == 'district':
			response['set_jenk_divider'] = 1
			prop['na_en']=response['parent_label']
			prop.update(dict_ext(source).within('total_dead','total_incident','total_injured','total_violent'))

		else:
			response['set_jenk_divider'] = 7
			child = source['lc_child_dict'].get(prop['code'])
			if child:
				prop.update(dict_ext(child).within('na_en','total_dead','total_incident','total_injured','total_violent'))

	return boundary

def getQuickOverview(request, filterLock, flag, code, response=dict_ext()):

	datafilter = get_datafilter(request.GET)
	
	response.path('cache')['getSecurity'] = response.pathget('cache','getSecurity') or getSecurity(request, filterLock, flag, code, includes=['incident_type'], datafilter=datafilter, response=response.within('cache'))
	dashboard_security_response = dashboard_security(request, filterLock, flag, code, includes=[''], datafilter=datafilter, response=response.within('cache','parent_label'))
	
	return {
		'templates':{
			'panels':'dash_qoview_security.html',
		},
		'data':dict_ext(dashboard_security_response).within('panels','eq_list','add_link'),
	}
