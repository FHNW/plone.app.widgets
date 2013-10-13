# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from plone.app.widgets.base import InputWidget
from plone.app.widgets.base import SelectWidget
from plone.app.widgets.base import TextareaWidget
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import NotImplemented
from plone.app.widgets.utils import get_date_options
from plone.app.widgets.utils import get_portal_url
from plone.app.widgets.utils import get_time_options
from plone.uuid.interfaces import IUUID

import json


class BaseWidget(TypesWidget):
    """Base widget for Archetypes."""

    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'patterns_widget',
        'pattern': None,
        'pattern_options': {},
    })

    def _base(self, pattern, pattern_options={}):
        """Base widget class."""
        raise NotImplemented

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :param context: Instance of content type.
        :type context: context

        :param request: Request object.
        :type request: request

        :param field: Instance of field of this widget.
        :type field: field

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        if self.pattern is None:
            raise NotImplemented("'pattern' option is not provided.")
        return {
            'pattern': self.pattern,
            'pattern_options': self.pattern_options,
        }

    def view(self, context, field, request):
        """Render widget on view.

        :returns: Fields value.
        :rtype: string
        """
        return field.getAccessor(context)()

    def edit(self, context, field, request):
        """Render widget on edit.

        :returns: Widget's HTML.
        :rtype: string
        """
        return self._base(**self._base_args(context, field, request)).render()


class DateWidget(BaseWidget):
    """Date widget for Archetypes."""

    _base = InputWidget

    _properties = BaseWidget._properties.copy()
    _properties.update({
        'pattern': 'pickadate'
    })

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(DateWidget, self)._base_args(context, field, request)
        args['name'] = field.getName()
        args['value'] = (request.get(field.getName(),
                                     field.getAccessor(context)()))

        if args['value'] and isinstance(args['value'], DateTime):
            args['value'] = ('{year:}-{month:02}-{day:02}').format(
                year=args['value'].year(),
                month=args['value'].month(),
                day=args['value'].day(),
            )

        elif args['value'] and isinstance(args['value'], datetime):
            args['value'] = ('{year:}-{month:02}-{day:02}').format(
                year=args['value'].year,
                month=args['value'].month,
                day=args['value'].day,
            )

        args.setdefault('pattern_options', {})

        args['pattern_options'].setdefault('date', {})
        args['pattern_options']['date'] = dict_merge(
            args['pattern_options']['date'],
            get_date_options(request))

        args['pattern_options']['time'] = False

        return args

    security = ClassSecurityInfo()
    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None):
        """Basic impl for form processing in a widget"""

        value = form.get(field.getName(), None)
        if not value:
            return empty_marker

        try:
            value = DateTime(datetime(*map(int, value.split('-'))))
        except:
            return empty_marker

        return value, {}


registerWidget(
    DateWidget,
    title='Date widget',
    description=('Date widget'),
    used_for=('Products.Archetypes.Field.DateTimeField',)
)


class DatetimeWidget(DateWidget):
    """Date widget for Archetypes."""

    _properties = DateWidget._properties.copy()

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(DatetimeWidget, self)._base_args(context, field, request)
        args['name'] = field.getName()
        args['value'] = (request.get(field.getName(),
                                     field.getAccessor(context)()))
        if args['value'] and isinstance(args['value'], DateTime):
            args['value'] = ('{year:}-{month:02}-{day:02}').format(
                year=args['value'].year(),
                month=args['value'].month(),
                day=args['value'].day(),
            )

        elif args['value'] and isinstance(args['value'], datetime):
            args['value'] = ('{year:}-{month:02}-{day:02}').format(
                year=args['value'].year,
                month=args['value'].month,
                day=args['value'].day,
            )

        if args['value'] and len(args['value'].split(' ')) == 1:
            args['value'] += ' 00:00'

        if args['pattern_options']['time'] is False:
            args['pattern_options']['time'] = {}

        args['pattern_options']['time'] = dict_merge(
            args['pattern_options']['time'],
            get_time_options(request))

        return args

    def process_form(self, instance, field, form, empty_marker=None):
        """Basic impl for form processing in a widget"""

        value = form.get(field.getName(), None)
        if not value:
            return empty_marker, {}

        tmp = value.split(' ')
        if not tmp[0]:
            return empty_marker
        value = tmp[0].split('-')
        value += tmp[1].split(':')

        try:
            value = DateTime(datetime(*map(int, value)))
        except:
            return empty_marker, {}

        return value, {}

registerWidget(
    DatetimeWidget,
    title='Datetime widget',
    description=('Datetime widget'),
    used_for=('Products.Archetypes.Field.DateTimeField',)
)


class SelectWidget(BaseWidget):
    """Select widget for Archetypes."""

    _base = SelectWidget

    _properties = BaseWidget._properties.copy()
    _properties.update({
        'pattern': 'select2',
        'separator': ';',
        'multiple': False,
    })

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value
            - `multiple`: field multiple
            - `items`: field items from which we can select to

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(SelectWidget, self)._base_args(context, field, request)
        args['name'] = field.getName()
        args['value'] = (request.get(field.getName(),
                                     field.getAccessor(context)()))
        args['multiple'] = self.multiple

        items = []
        for item in field.Vocabulary(context).items():
            items.append((item[0], item[1]))
        args['items'] = items

        return args
        return args

registerWidget(
    SelectWidget,
    title='Select widget',
    description=('Select widget'),
    used_for=('Products.Archetypes.Field.SelectField',)
)






















#class TinyMCEWidget(BaseWidget):
#    _properties = BaseWidget._properties.copy()
#    _properties.update({
#        'pattern': 'tinymce',
#    })
#    _widget = TextareaWidget
#
#    def _widget_args(self, context, field, request):
#        args = super(TinyMCEWidget, self)._widget_args(context, field, request)
#        return args
#
#
#registerWidget(
#    TinyMCEWidget,
#    title='TinyMCE widget',
#    description=('TinyMCE widget'),
#    used_for=('Products.Archetypes.Field.TextField',)
#)
#
#
#class AjaxSelectWidget(BaseWidget):
#    _properties = BaseWidget._properties.copy()
#    _properties.update({
#        'pattern': 'select2',
#        'separator': ';',
#        'orderable': False,
#        'ajax_vocabulary': None
#    })
#    _widget = InputWidget
#
#    def getWidgetValue(self, context, field, request):
#        return self.separator.join(
#            request.get(field.getName(), field.getAccessor(context)()))
#
#    def _widget_args(self, context, field, request):
#        args = super(AjaxSelectWidget, self)._widget_args(context, field, request)
#
#        vocabulary_name = getattr(field, 'vocabulary_factory', None)
#        if self.ajax_vocabulary:
#            vocabulary_name = self.ajax_vocabulary
#        if vocabulary_name:
#            url = base_url(context, request)
#            url += '/@@getVocabulary?name=' + vocabulary_name
#            if 'pattern_options' not in args:
#                args['pattern_options'] = {}
#            args['pattern_options']['ajaxVocabulary'] = url
#        args['value'] = self.getWidgetValue(context, field, request)
#        return args
#
#    def process_form(self, instance, field, form, empty_marker=None):
#        value = form.get(field.getName(), empty_marker)
#        if value is empty_marker:
#            return empty_marker
#        value = value.strip().split(self.separator)
#        return value, {}
#
#
#registerWidget(
#    AjaxSelectWidget,
#    title='Ajax select widget',
#    description=('Ajax select widget'),
#    used_for=('Products.Archetypes.Field.LinesField',)
#)
#
#
#class RelatedItemsWidget(AjaxSelectWidget):
#    _properties = AjaxSelectWidget._properties.copy()
#    _properties.update({
#        'pattern': 'relateditems',
#        'separator': ','
#    })
#    vocabulary_view = "@@getVocabulary"
#
#    def getWidgetValue(self, context, field, request):
#        reqvalues = request.get(field.getName(), None)
#        if not reqvalues:
#            values = request.get(field.getName(), field.getAccessor(context)())
#            values = [IUUID(o) for o in values if o]
#        else:
#            values = [v.split('/')[0]
#                      for v in reqvalues.strip().split(self.separator)]
#        return self.separator.join(values)
#
#    def _widget_args(self, context, field, request):
#        args = super(RelatedItemsWidget, self)._widget_args(
#            context, field, request)
#
#        vocabulary_name = getattr(field, 'vocabulary_factory',
#                                  self.ajax_vocabulary)
#        if not vocabulary_name:
#            vocabulary_name = 'plone.app.vocabularies.Catalog'
#        url = base_url(context, request)
#        vocabulary_view = self.vocabulary_view
#        url += '/' + vocabulary_view + '?name=' + vocabulary_name
#        if 'pattern_options' not in args:
#            args['pattern_options'] = {}
#        args['pattern_options']['ajaxVocabulary'] = url
#
#        pprops = getToolByName(context, 'portal_properties', None)
#        folder_types = ['Folder']
#        if pprops:
#            site_props = pprops.site_properties
#            folder_types = site_props.getProperty(
#                'typesLinkToFolderContentsInFC',
#                ['Folder'])
#        args['pattern_options']['folderTypes'] = folder_types
#        return args
#
#    def process_form(self, instance, field, form, empty_marker=None):
#        # select2 will add unique identifier information to results
#        # so we're stripping it out here.
#        value, other = super(RelatedItemsWidget, self).process_form(
#            instance, field, form, empty_marker)
#        value = [v.split('/')[0] for v in value]
#        return value, other
#
#
#registerWidget(
#    RelatedItemsWidget,
#    title='Related items widget',
#    description=('Related items widget'),
#    used_for='Products.Archetypes.Field.ReferenceField')
#
#
#class QueryStringWidget(BaseWidget):
#    _properties = BaseWidget._properties.copy()
#    _properties.update({
#        'pattern': 'querystring',
#    })
#
#    def _widget_args(self, context, field, request):
#        args = super(QueryStringWidget, self)._widget_args(
#            context, field, request)
#
#        if 'pattern_options' not in args:
#            args['pattern_options'] = {}
#
#        args['pattern_options']['indexOptionsUrl'] = '%s/@@qsOptions' % (
#            base_url(context, request))
#
#        criterias = [dict(c) for c in field.getRaw(context)]
#        args['value'] = request.get(field.getName(),
#                                    json.dumps(criterias))
#        return args
#
#    security = ClassSecurityInfo()
#    security.declarePublic('process_form')
#
#    def process_form(self, instance, field, form, empty_marker=None,
#                     emptyReturnsMarker=False, validating=True):
#        value = form.get(field.getName(), empty_marker)
#        if value is empty_marker:
#            return empty_marker
#        value = json.loads(value)
#        return value, {}
#
#
#registerWidget(
#    QueryStringWidget,
#    title='Querystring widget',
#    description=('Querystring widget'),
#    used_for='archetypes.querywidget.field.QueryField')
