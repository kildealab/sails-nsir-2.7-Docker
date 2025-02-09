from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.db.models import Q, Max
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils import formats, timezone
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DetailView, TemplateView

from listable.views import BaseListableView, SELECT
from listable.views import Column as C

import json
import calendar
import collections
import datetime
import time
import re
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from time import strftime

import forms
import models
import feeds
from notifications_nsir import signals
from accounts.models import ILSUser

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def format_series_for_stacked(series_array, num_incidents):
    """Reformat the series_array to be passed as JSON data for highcharts generation, into
    a point based format for stacked column generation.

    This function is set up this way, because was added after creating the format_series_for_
    unstacked and pie were created. These were needed as the default (stacked) column
    series_array was not passed in point notation. The data was just passed as an array
    of ints stored in the 'data' key of each series in series_array. Was switched to array
    of dictionaries, each containing a y value and other keys-value pairs. This information
    is stored in the 'points' key of each series the series_array. Because the 'data' key
    is what is passed to JSON, need to reassign 'points' to 'data.'
    """
    colors = [
        '#77C4E8','#2FC826','#AA38C9','#EB696D','#386EA6',
        '#8BC726','#3ADCC6','#FE4CA6','#EDE478','#C8A67A',
        '#7FB279','#5280E9','#D58CD5','#4F8F8F','#FFD3AC',
        '#FE8E67'
    ]

    for choice in series_array:
        choice["series_total"] = sum(choice["data"])
        choice["data"] = choice["points"]

    series_array = sorted(series_array, key=itemgetter('series_total'), reverse=True)

    return series_array


def format_series_for_unstacked(series_array, x_bins, num_incidents):
    """Reformat the series_array to be passed as JSON data for highcharts generation, into
    the format required for an unstacked column chart binned by choice (not date).

    Args:
        series_array: An array of dicts, with each entry representing a single data series
        x_bins: An empty array to be filled in this function, with strings representing
            the bins into which incidents are sorted
    """
    # Old color scheme
    # colors = ['#27AED5','#8FD31E','#CF6FFC','#6BE04B','#DE52D1',
    #     '#16B661','#D0338A','#1CBC8A','#F65262','#6073E0',
    #     '#D3C247','#3E62A8','#F7983F','#B8A2F0','#73880B',
    #     '#B0B6EC','#776721','#9D96C5','#B14046','#217C8D']
    # colors = [
    #     '#77C4E8','#2FC826','#AA38C9','#EB696D','#386EA6',
    #     '#8BC726','#3ADCC6','#FE4CA6','#EDE478','#C8A67A',
    #     '#7FB279','#5280E9','#D58CD5','#4F8F8F','#FFD3AC',
    #     '#FE8E67'
    # ]
    colors = [ '#2B558B' ]

    # total_sum will hold total # of incidents being plotted
    total_sum = 0
    for choice in series_array:
        total_sum = total_sum + sum(choice["data"])

    new_data = []
    j = 0
    cj = 0
    #Create data points: loop through each choice
    for choice in series_array:
        if sum(choice["data"]) > 0:
            choice_point = {}
            choice_point["y"] = sum(choice["data"])
            # choice_point["color"] = colors[cj%len(colors)]
            choice_point["category"] = choice["name"]

            # calculate the percent of the total represented by the current data point
            choice_percent = 0
            if num_incidents != 0:
                choice_percent = (choice_point["y"]*100.0/num_incidents)
            choice_percent_string = "%.1f%%" % round(choice_percent,1)
            choice_point["fraction"] = choice_percent_string

            choice_point["total"] = total_sum

            # Create entries for each point in the current series, to be displayed in table
            # form (if chart pieces are clicked)
            choice_point["ids"] = []
            choice_point["descs"] = []
            choice_point["invs"] = []
            choice_point["oncs"] = []
            choice_point["datedec"] = []
            choice_point["etypes"] = []
            choice_point["compstatus"] = []
            for point in choice["points"]:
                choice_point["ids"] = choice_point["ids"] + point["ids"]
                choice_point["descs"] = choice_point["descs"] + point["descs"]
                choice_point["invs"] = choice_point["invs"] + point["invs"]
                choice_point["oncs"] = choice_point["oncs"] + point["oncs"]
                choice_point["datedec"] = choice_point["datedec"] + point["datedec"]
                choice_point["etypes"] = choice_point["etypes"] + point["etypes"]
                choice_point["compstatus"] = choice_point["compstatus"] + point["compstatus"]

            new_data.append(choice_point)
            # x_bins.append(choice["name"])
            j = j + 1
            cj = cj + 1

    # Sort the data
    unsorted_data = new_data
    new_data = []
    new_data = sorted(unsorted_data, key=itemgetter('y'), reverse=True)

    # Produce x bins (x axis labels) & assign colors (since data have been sorted)
    i = 0
    for item in new_data:
        x_bins.append(item["category"])
        item["color"] = colors[i%len(colors)]
        i=i+1

    #Format properly
    new_series = []
    new_series_dict = {}
    new_series_dict["name"] = "mydata"
    new_series_dict["data"] = new_data
    new_series_dict["showInLegend"] = False
    new_series_dict["num_incidents"] = num_incidents
    new_series.append(new_series_dict)

    return new_series

def format_series_for_pie(series_array,date_range,query_model_title,num_incidents):
    """Reformat the series_array to be passed as JSON data for highcharts generation, into
    the format required for a multi-series pie chart.

    Args:
        series_array: An array of dicts, with each entry representing a single data series
        date_range: An array of strings representing the bins into which incidents are
        sorted
        query_model_title: Name of the model being plotted
    """
    # Colors from: http://paletton.com/#uid=15b0u0kvXrwlAxXryve-slHHGgs
    # Old colors:
    # pie_colors = [
    #     "#DB0600", "#DB6400", "#DB9200", "#DBB700", "#DBDA00", "#88CD00",
    #     "#00AF00", "#017F84", "#0F3B92", "#301297", "#610892", "#B10061"
    # ]
    # pie_colors = [
    #     "#FF535C", "#FFA153", "#FFC653", "#FFE153", "#FFF353", "#B93F43",
    #     "#43CF43", "#359BA0", "#4567AF", "#6149B4", "#883FAF", "#D04493"
    # ]
    colors = [
        '#77C4E8','#2FC826','#AA38C9','#EB696D','#386EA6',
        '#8BC726','#3ADCC6','#FE4CA6','#EDE478','#C8A67A',
        '#7FB279','#5280E9','#D58CD5','#4F8F8F','#FFD3AC',
        '#FE8E67'
    ]

    # Each array will hold data for a series
    base_data = [] # inner pie (no date binning)
    drill_data = [] # outer pie (date binning)

    # total_sum will hold total # of incidents being plotted
    total_sum = 0
    for choice in series_array:
        total_sum = total_sum + sum(choice["data"])

    # Loop through all choices, and produce data points to be added to each series array
    # The outer loop creates the inner pie displayed on the chart. This data is not sorted
    # by date at all. Is basically the unstacked column chart equivalent. The inner loop
    # filters into drilldown data that creates the outer pie displayed on the chart. This
    # data is sorted by date.
    i = 0
    for choice in series_array:
        # calculate the percent of the total represented by the current data point
        base_percent = 0
        base_y = sum(choice["data"])
        if num_incidents != 0:
            base_percent = (base_y*100.0/num_incidents)
        base_percent_string = "%.1f%%" % round(base_percent,1)

        # Only display choices which have counts
        # if base_y != 0:
        display_inner = True
        if base_y == 0:
            display_inner = False

        # Create entries for each point in the current series, to be displayed in table
        # form (if chart pieces are clicked)
        array_ids = []
        array_descs = []
        array_invs = []
        array_oncs = []
        array_datedec = []
        array_etypes = []
        array_compstatus = []
        for point in choice["points"]:
            array_ids = array_ids + point["ids"]
            array_descs = array_descs + point["descs"]
            array_invs = array_invs + point["invs"]
            array_oncs = array_oncs + point["oncs"]
            array_datedec = array_datedec + point["datedec"]
            array_etypes = array_etypes + point["etypes"]
            array_compstatus = array_compstatus + point["compstatus"]

        # Create the points
        base_data.append({"name": choice["name"],
            "y": base_y,
            "fraction": base_percent_string,
            "total": total_sum,
            "showInLegend": display_inner,
            "ids": array_ids,
            "descs": array_descs,
            "invs": array_invs,
            "oncs": array_oncs,
            "datedec": array_datedec,
            "etypes": array_etypes,
            "compstatus": array_compstatus,
            # "color": colors[i%len(colors)]
        })

        # Outer pie data
        # j = 0
        # for date_bin in date_range:
        #     # calculate the percent of the total represented by the current data point
        #     denom = base_data[i]["y"]
        #     numer = choice["data"][j]            
        #     percent = 0
        #     if denom != 0:
        #         percent = (numer*100.0)/(denom)
        #     percent_string = "%.1f%%" % round(percent,1)

        #     display_date = False
        #     if i == 0:
        #         display_date = True
            
        #     # Create the points
        #     drill_data.append({"name": date_bin,
        #         "series_name": choice["name"],
        #         "y": choice["data"][j],
        #         "ids":choice["points"][j]["ids"],
        #         "descs":choice["points"][j]["descs"],
        #         "invs":choice["points"][j]["invs"],
        #         "oncs":choice["points"][j]["oncs"],
        #         "datedec":choice["points"][j]["datedec"],
        #         "etypes":choice["points"][j]["etypes"],
        #         "compstatus":choice["points"][j]["compstatus"],
        #         "year":choice["points"][j]["year"],
        #         "color": pie_colors[j%12], "fraction":percent_string,
        #         "showInLegend": display_date
        #     })
        #     j = j + 1
        i = i + 1

    # Allow legend hovering on inner pie, but not outer pie (b/c the series repeats)
    hover_dict = {"enabled": True}
    outer_hover_dict = {"hover": hover_dict}

    # drill_hover_dict = {"enabled": False}
    # drill_outer_hover_dict = {"hover": drill_hover_dict}

    # Process inner data only to be displayed in decreasing order:
    old_base_data = base_data
    base_data = []
    base_data = sorted(old_base_data, key=itemgetter('y'), reverse=True)
    i = 0
    for item in base_data:
        item["color"] = colors[i%len(colors)]
        i = i+1

    # The new series array to be provided to highcharts as JSON
    new_series = [
        {'data': base_data, 'name': query_model_title, 'size': '90%', 'states':outer_hover_dict, 'num_incidents':num_incidents},
        # {'data': drill_data, 'name': "Date Bins", 'size': '95%', 'innerSize': '90%', 'states':drill_outer_hover_dict}
    ]

    return new_series

def get_num_incidents(query_dates,start_date,end_date,query_complete,query_field):
    """Get the number of incidents that will form the denominator of each chart piece's
    fractional representation.

    Args:
        query_dates: a string representing the Incident modelfield name of the date type 
            to establish bins for
        query_complete: A string that may be used to determine what level of completeness
            Incident objects should be filtered to in producing the desired plot
        start_date: Datetime object representing start date to filter Incidents by
        end_date: Datetime object representing end date to filter Incidents by
        query_field: A string representing a model field ID to facilitate determination
            of which event types are applicable, and facilitate Incident query accordingly
    """
    # STEPS:
    # Create a queryset filter for all incidents within the time frame specified
    # Get a queryset filter for all incidents with particular completion status
    # Determine which event types the field being plotted is applicable to
    # Get a queryset filter for all incidents with the determined event types
    # Filter incidents accordingly
    date_kwargs = {
        '{0}__{1}'.format(query_dates,'gte'): start_date,
        '{0}__{1}'.format(query_dates,'lte'): end_date
    }

    complete_filter = get_complete_filter(query_complete)

    event_types = models.Incident.get_event_type_ids_for_field_id(query_field)
    type_filter = get_type_filter(event_types)

    incidents = models.Incident.valids.filter(Q(**date_kwargs),complete_filter,type_filter)
    num_considered_incidents = incidents.count()
    # FOR FK TYPE FIELDS:
    # Get the number of incidents that have provided at least one value for the field
    # being queried (M2M fields may have more than 1 selection per incident, but should)
    # only be counted once.
    # filled_incident_kwargs = {query_field.name+"__isnull": True}
    # num_filled_incidents = incidents.exclude(Q(**filled_incident_kwargs)).distinct().count()

    # FOR USER TYPE FIELDS
    # Get the number of incidents that have provided at least one value for the field
    # being queried (M2M fields may have more than 1 selection per incident, but should)
    # only be counted once.
    # filled_incident_kwargs = {user_type.incident_field_name+"__isnull": True}
    # num_filled_incidents = incidents.exclude(Q(**filled_incident_kwargs)).distinct().count()

    return num_considered_incidents


def get_counts_user(bin_object, query_range, query_model, user_type, user_choice, query_dates, query_complete, start_date, end_date):
    """Create an array of data to be used as a series in producing a HighCharts chart in
    jQuery, given pertinent input parameters.

    Args:
        bin_object: StatDateBin object (e.g. Monthly - Choose Range).
        query_range: an array containing the bins into which counts should be sorted (
            elements may be tuples of (year,month) as ints or just ints (year))
        query_model: a class variable representing the user model (ILSUser)
        user_type: Stat object representing the type of user (Investigator or Oncologist)
        user_choice: a string representing either "All" to get all choices or a single
            ILSUser
        query_dates: a string representing the Incident modelfield name of the date type 
            to establish bins for
        query_complete: A string that may be used to determine what level of completeness
            Incident objects should be filtered to in producing the desired plot
        start_date: Datetime object representing start date to filter Incidents by
        end_date: Datetime object representing end date to filter Incidents by
    """
    # Get all choices and the total number of choices for the desired type of ILSUser
    choices = None
    if user_choice == "All":
        filter_kwargs = {
            user_type.account_field_name: True
        }
        user_q = Q(**filter_kwargs)
        choices = query_model.objects.filter(user_q)
    else:
        choices = query_model.objects.filter(id=user_choice)
    num_choices = choices.count()

    # Create a queryset filter for all incidents within the time frame specified
    # Get a queryset filter for all incidents with particular completion status
    # Filter incidents accordingly
    date_kwargs = {
        '{0}__{1}'.format(query_dates,'gte'): start_date,
        '{0}__{1}'.format(query_dates,'lte'): end_date
    }
    complete_filter = get_complete_filter(query_complete)
    incidents = models.Incident.valids.filter(Q(**date_kwargs),complete_filter)

    series_array = []
    for choice in choices:
        choice_dict = {}
        choice_dict["name"] = choice.get_name()

        filter_kwargs = {
            user_type.incident_field_name: choice
        }
        myq = Q(**filter_kwargs)

        if "monthly" in bin_object.name.lower():
            # Get the counts per month, store in data of current dict
            temp_results = incident_counts_by_date(incidents.filter(myq),query_dates=query_dates,month_range=query_range)
            choice_dict["points"] = temp_results["points"] # points with extra keys
            choice_dict["data"] = temp_results["counts"] # numeric data only
            series_array.append(choice_dict)
        elif "yearly" in bin_object.name.lower():
            temp_results = incident_counts_by_date_yearly(incidents.filter(**filter_kwargs),query_dates=query_dates,year_range=query_range)
            choice_dict["points"] = temp_results["points"] # points with extra keys
            choice_dict["data"] = temp_results["counts"] # numeric data only
            series_array.append(choice_dict)

    # Must JSON handle the data in function returned-to b/c of unicode names. 
    return series_array


def get_counts_key(bin_object, query_range, query_model, fk_choice, query_field, query_dates, query_complete, start_date, end_date):
    """Create an array of data to be used as a series in producing a HighCharts chart in
    jQuery, given pertinent input parameters.

    Args:
        bin_object: StatDateBin object (e.g. Monthly - Choose Range).
        query_range: an array containing the bins into which counts should be sorted (
            elements may be tuples of (year,month) as ints or just ints (year))
        query_model: a class variable representing a Model (e.g. EventType)
        fk_choice: a string representing either "All" to get all choices or a single option
            for a particular FK model
        query_field: a string representing the Incident modelfield corresponding to the 
            query_model
        query_dates: a string representing the Incident modelfield name of the date type 
            to establish bins for
        query_complete: A string that may be used to determine what level of completeness
            Incident objects should be filtered to in producing the desired plot
        start_date: Datetime object representing start date to filter Incidents by
        end_date: Datetime object representing end date to filter Incidents by
    """
    is_tree = "Tree" in query_field.get_internal_type()

    # Get all choices and the total number of choices for the desired model
    choices = None
    if fk_choice == "All":
        # If is_tree type class, for an 'All' selection, only show child choices b/c
        # the parents would have none (can't be selected)
        if is_tree:
            child_choices = set()
            for choice in query_model.objects.all():
                descendants = choice.get_descendants()
                if len(descendants) == 0:
                    child_choices.add(choice.pk)
            choices = query_model.objects.filter(pk__in=child_choices)
        else:
            choices = query_model.objects.all()
    elif is_tree:
        parent_choice = query_model.objects.get(name=fk_choice)
        children = parent_choice.get_children()
        if len(children) == 0:
            choices = query_model.objects.filter(name=fk_choice)
        else:
            child_choices = set()
            for child in children:
                child_choices.add(child.pk)
            choices = query_model.objects.filter(pk__in=child_choices)
        # REMOVE THIS:
        # choices = query_model.objects.filter(name=fk_choice)
    else:
        choices = query_model.objects.filter(name=fk_choice)

    num_choices = choices.count()

    # Create a queryset filter for all incidents within the time frame specified
    # Get a queryset filter for all incidents with particular completion status
    # Filter incidents accordingly
    date_kwargs = {
        '{0}__{1}'.format(query_dates,'gte'): start_date,
        '{0}__{1}'.format(query_dates,'lte'): end_date
    }
    complete_filter = get_complete_filter(query_complete)
    incidents = models.Incident.valids.filter(Q(**date_kwargs),complete_filter)

    # series_array will hold an array of dictionaries. One dictionary per choice in the
    # desired model. Each dictionary keys {data} to an array of data and to the name of
    # of the choice {name}. This format allows plugging directly into highcharts
    series_array = []
    for choice in choices:
        choice_dict = {}
        choice_dict["name"] = choice.name

        # Dynamically set QS filtering parameters (the incident model field, and FK choice)
        # If is a tree type, and user has selected a particular option (not All), and 
        # that option is a parent choice in a tree structure, assign counts as sum of all
        # counts of descendant choices of the choice of interest
        myq = None
        if is_tree and fk_choice != "All":
            descendants = choice.get_descendants()
            if len(descendants) > 0:
                queries = []
                for value in descendants:
                    filter_kwargs = {
                        query_field.name: value
                    }
                    queries.append(Q(**filter_kwargs))
                # queries = [Q(query_field.name=value) for value in descendants] # array of Q objects
                query = queries.pop()
                for item in queries:
                    query |= item
                myq = query
            else:
                filter_kwargs = {
                    query_field.name: choice
                }
                myq = Q(**filter_kwargs)
        else:
            filter_kwargs = {
                query_field.name: choice
            }
            myq = Q(**filter_kwargs)
        if "monthly" in bin_object.name.lower():
            # Get the counts per month, store in data of current dict
            temp_results = incident_counts_by_date(incidents.filter(myq),query_dates=query_dates,month_range=query_range)
            choice_dict["points"] = temp_results["points"] # points with extra keys
            choice_dict["data"] = temp_results["counts"] # numeric data only
            series_array.append(choice_dict)
        elif "yearly" in bin_object.name.lower():
            temp_results = incident_counts_by_date_yearly(incidents.filter(**filter_kwargs),query_dates=query_dates,year_range=query_range)
            choice_dict["points"] = temp_results["points"] #points with extra keys
            choice_dict["data"] = temp_results["counts"] #numeric data only
            series_array.append(choice_dict)

    # Must JSON handle the data in function returned-to b/c of unicode names. 
    return series_array

def get_complete_filter(complete_filter):
    """Create and return a Q object which may be used to filter Incident objects by their
    investigation_complete status, when given a particular keyword for desired completion
    status.
    """
    Q_filter = None
    if complete_filter == "complete":
        Q_filter = Q(investigation_complete=True)
    elif complete_filter == "incomplete":
        Q_filter = Q(investigation_complete=False)
    else:
        Q_filter = Q()
    return Q_filter

def get_type_filter(event_types):
    """Create and return a joint-OR Q object which may be used to select only Incidents
    with an event type in the provided array of event_types (pks)
    """
    # Create array of Q objects, one entry per allowed event type
    event_queries = [Q(event_type__id=event_type) for event_type in event_types]
    # Extract the first Q object
    event_Q = event_queries.pop()
    # Join Q objects via ORs
    for query in event_queries:
        event_Q |= query

    # Return the joint-OR Q object
    return event_Q


# returns array containing counts of filtered set of incidents per month
def incident_counts_by_date(incidents,query_dates,month_range):
    """Count the number of incidents matching each date bin (year & month), return as an
    array (of ints) and an array of point dictionaries that contain a y value, as well as
    arrays of other parameters needed to produce tables of incidents corresponding to
    certain chart selections.
    """
    results = {}
    counts = [] # counts only
    points = [] # points
    for year, month in month_range:
        point = {}
        cur_count = 0
        ids = []
        descs = []
        invs = []
        oncs = []
        datedec = []
        etypes = []
        compstatus = []
        for x in incidents:
            if getattr(x, query_dates).month == month and getattr(x, query_dates).year == year:
                ids.append(x.incident_id)
                descs.append(x.descriptor)
                if x.investigator != None:
                    invs.append(x.investigator.get_name())
                else:
                    invs.append("")
                if x.oncologist != None:
                    oncs.append(x.oncologist.get_name())
                else:
                    oncs.append("")
                datedec.append(x.date_incident_detected)
                etypes.append(x.event_type.name)
                compstatus.append(x.investigation_complete)
                cur_count += 1
        counts.append(cur_count)
        point["y"] = cur_count
        point["ids"] = ids
        point["descs"] = descs
        point["invs"] = invs
        point["oncs"] = oncs
        point["datedec"] = datedec
        point["year"] = year
        point["etypes"] = etypes
        point["compstatus"] = compstatus
        points.append(point)
    results["points"] = points
    results["counts"] = counts
    return results

# returns array containing counts of filtered set of incidents per month
def incident_counts_by_date_yearly(incidents,query_dates,year_range):
    """Count the number of incidents matching each date bin (year), return as an array (of
    ints) and an array of point dictionaries that contain a y value, as well as
    arrays of other parameters needed to produce tables of incidents corresponding to
    certain chart selections.
    """
    results = {}
    counts = [] # counts only
    points = [] # points
    for year in year_range:
        point = {}
        cur_count = 0
        ids = []
        descs = []
        invs = []
        oncs = []
        datedec = []
        etypes = []
        compstatus = []
        for x in incidents:
            if getattr(x, query_dates).year == year:
                ids.append(x.incident_id)
                descs.append(x.descriptor)
                if x.investigator != None:
                    invs.append(x.investigator.get_name())
                else:
                    invs.append("")
                if x.oncologist != None:
                    oncs.append(x.oncologist.get_name())
                else:
                    oncs.append("")
                datedec.append(x.date_incident_detected)
                etypes.append(x.event_type.name)
                compstatus.append(x.investigation_complete)
                cur_count += 1
        counts.append(cur_count)
        point["y"] = cur_count
        point["ids"] = ids
        point["descs"] = descs
        point["invs"] = invs
        point["oncs"] = oncs
        point["datedec"] = datedec
        point["etypes"] = etypes
        point["compstatus"] = compstatus
        points.append(point)
    results["points"] = points
    results["counts"] = counts
    return results

def handle_dates(form, response_data, bin_object=None,start_month=None,start_year=None,end_month=None,end_year=None):
    """Prepare a dictionary containing important date related data which is required
    to generate date filtered statistics plots.

    This function uses cleaned valid form data to determine the start and end date, as
    datetime objects within which incidents should be filtered. The function also
    determines whether a monthly or yearly type binning will be performed, and fills
    the dictionary to returned accordingly. The "date range" key of response_data
    dictionary to be JSONified is also filled, this is used to create x axes labels.

    Args:
        form: Accep the cleaned, valid (filled) form.
        response_data: dictionary of data which is to be JSONified to generated plots

    Returns:
        A dictionary with date related parameters needed to filter incidents by date.
        Relevant keys:
            query_range: depending on whether binning by year or by month, this will be
            an array of years or an array of tuples, with each tuple containing a year
            and a month
            start_date: datetime representing the start date to filter incidents by.
            end_date: datetime representing the end date to filter incidents by.
    """
    # Constants used for determining/describing errors in inputted form data
    MONTH_CAP = 24
    YEAR_CAP = 5
    TOO_MANY_MONTHS = "Please choose a narrower month range (%i months or fewer)" % MONTH_CAP
    TOO_MANY_YEARS = "Please choose a narrower year range (%i months or fewer)" % YEAR_CAP
    INCORRECT_RANGE = "Please select an End Date which falls after the Start Date"

    # variable to return
    return_dict = {}

    if form != None:
        # Date binning related fields
        # StatDateBin object
        bin_object = form.cleaned_data['date_bin']
        # Month object
        start_month = form.cleaned_data['start_month']
        # String representing the year (e.g. 2016)
        start_year = form.cleaned_data['start_year']
        end_month = form.cleaned_data['end_month']
        end_year = form.cleaned_data['end_year']

    date_stuff = None # dictionary to hold various date related variables - fill in below

    # If doing a monthly type filter
    if "monthly" in bin_object.name.lower():
        if bin_object.bin_name == "monthly_choose_range":
            date_stuff = handle_date_range(bin_object, start_month, end_month, int(start_year), int(end_year))
        elif bin_object.bin_name == "monthly_last_year":
            date_stuff = handle_date_range(bin_object=bin_object, start_month=None, end_month=None, start_year=None, end_year=None)

        # {int} e.g. 18
        num_months = date_stuff["num_months"]
        # {array of tuples} e.g. [(2015, 1), (2015, 2), ...]
        year_month_array = date_stuff["year_month_array"]
        # {array of strings} e.g. ['Jan', 'Feb', ...]
        month_array = date_stuff["month_array"]
        response_data["date_range"] = month_array
        # DateTime objects:
        start_date = date_stuff["start_date"]
        end_date = date_stuff["end_date"]

        return_dict['query_range'] = year_month_array
        return_dict['start_date'] = date_stuff["start_date"]
        return_dict['end_date'] = date_stuff["end_date"]

        if num_months > MONTH_CAP:
            response_data["error_message"] = TOO_MANY_MONTHS
            return None
        if end_date < start_date:
            response_data["error_message"] = INCORRECT_RANGE
            return None

    # If doing a yearly type filter
    elif "yearly" in bin_object.name.lower():
        if bin_object.bin_name == "yearly_choose_range":
            date_stuff = handle_date_range_yearly(bin_object=bin_object, start_year=int(start_year), end_year=int(end_year))

        num_years = date_stuff["num_years"]
        year_array = date_stuff["year_array"]
        response_data["date_range"] = year_array
        start_date = date_stuff["start_date"]
        end_date = date_stuff["end_date"]

        return_dict['query_range'] = year_array
        return_dict['start_date'] = date_stuff["start_date"]
        return_dict['end_date'] = date_stuff["end_date"]

        if num_years > YEAR_CAP:
            response_data["error_message"] = TOO_MANY_YEARS
            return None
        if end_date < start_date:
            response_data["error_message"] = INCORRECT_RANGE
            return None

    return return_dict

def handle_date_range(bin_object, start_month, end_month, start_year, end_year):
    """Handle creation of a number of date related parameters.

    Args:
        bin_object: StatDateBin object (e.g. Monthly - Choose Range).
        start_month & end_month: Month objects
        start_year & end_year: ints representing years

    Return:
        A dictionary. Relevant keys:
        num_months: an integer indicating the number of months spanned
        month_array: an array of strings representing months
        year_month_array: an array of tuples which contain (year, month) pairs, each as
            an int
        start_date: datetime object
        end_date: datetime object
    """
    month_objects = models.Month.objects.all()

    # Handle case if certain month/years not provided: i.e. adjust parameters to span
    # the previous year
    if start_month == None or start_year == None or end_month == None or end_year == None:
        now = timezone.now()
        mod_time = relativedelta(months=11)
        start_month_i = (now - mod_time).month
        start_year = (now - mod_time).year
        end_month_i = now.month
        end_year = now.year

        start_month = month_objects.get(order=start_month_i)
        end_month = month_objects.get(order=end_month_i)

    # dictionary of results to be returned
    results = {}

    num_months = (end_year - start_year)*12 + end_month.order - start_month.order + 1

    month_array = []
    year_month_array = []
    cur_month = start_month
    cur_year = start_year
    for i in range(0, num_months):
        query_order = start_month.order + i
        # new year
        if query_order % 12 == 1 and i != 0:
            query_order = query_order % 12
            cur_year += 1
        # not december
        elif query_order % 12 != 0:
            query_order = query_order % 12
        else:
            query_order = 12

        cur_month = month_objects.get(order=query_order)
        month_array.append(str(cur_month.abbrev))
        year_month_array.append((cur_year,int(query_order)))

    # Create datetimes out of start/end_month/year variables
    start_day = 1
    start_date = datetime.datetime(start_year,int(start_month.order),start_day)
    end_day = calendar.monthrange(end_year,int(end_month.order))[1]
    end_date = datetime.datetime(end_year,int(end_month.order),end_day,23,59,59)

    results['num_months'] = num_months
    results['month_array'] = month_array
    results['year_month_array'] = year_month_array
    results['start_date'] = start_date
    results['end_date'] = end_date

    return results


def handle_date_range_yearly(bin_object, start_year, end_year):
    """Handle creation of a number of date related parameters.

    Args:
        bin_object: StatDateBin object (e.g. Monthly - Choose Range).
        start_year & end_year: ints representing years

    Return:
        A dictionary. Relevant keys:
        num_years: an integer indicating the number of years spanned
        month_array: an array of ints representing years
        start_date: datetime object
        end_date: datetime object
    """
    results = {}
    num_years = end_year - start_year

    year_array = []
    for year in range(start_year, end_year+1):
        year_array.append(year)

    start_day = 1
    start_month = 1
    start_date = datetime.datetime(start_year,start_month,start_day)
    end_month = 12
    end_day = calendar.monthrange(end_year,end_month)[1]
    end_date = datetime.datetime(end_year,end_month,end_day,23,59,59)

    results['num_years'] = num_years
    results['year_array'] = year_array
    results['start_date'] = start_date
    results['end_date'] = end_date

    return results






#-----------------------------------------------------------------------------------------
# NO LONGER USED
#-----------------------------------------------------------------------------------------
def get_month_list_array():
    # Datetimes. Need to convert from being last_year to specified date range
    now = timezone.now()
    last_year = now - timezone.timedelta(days=365)

    # months holds an array of (year,  month) combinations begining with the month from
    # 12 months ago, up to the current month/year
    months = [time.localtime(time.mktime([now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0]))[:2] for n in range(12)]
    months.reverse()
    return months

def get_month_array():
    # Datetimes. Need to convert from being last_year to specified date range
    now = timezone.now()
    last_year = now - timezone.timedelta(days=365)

    # months holds an array of (year,  month) combinations begining with the month from
    # 12 months ago, up to the current month/year

    # for n in range(12):
    #     print [now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0]
    #     print time.mktime([now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0])
    #     print time.localtime(time.mktime([now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0]))
    #     print time.localtime(time.mktime([now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0]))[1]
    months = [time.localtime(time.mktime([now.year, now.month - n, 1, 0, 0, 0, 0, 0, 0]))[1] for n in range(12)]
    months.reverse()
    return months

def month_int_to_str(month_array):
    month_dict = {
        "1": "Jan",
        "2": "Feb",
        "3": "Mar",
        "4": "Apr",
        "5": "May",
        "6": "Jun",
        "7": "Jul",
        "8": "Aug",
        "9": "Sep",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec"
    }
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    new_array = []

    for month in month_array:
        # new_array.append(month_dict[month])
        new_array.append(MONTHS[month-1])

    return new_array