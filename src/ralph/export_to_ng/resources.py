# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from import_export import fields
from import_export import resources
from import_export import widgets
from ralph.discovery import models_device

from ralph.cmdb import models_ci
from ralph_assets import models_assets


class EmptyIdMixin(object):
    # no id in old ralph, should be added here, or changed resource in import
    id = fields.Field(column_name='id')
    def dehydrate_id(self, asset):
        return ""

class RalphResourceMixin(EmptyIdMixin, object):
    def get_export_headers(self):
        ralph_field2ng_field = {
            v or k: k for k, v in self.__class__.Meta.ng_field2ralph_field.items()
        }
        headers = [
            ralph_field2ng_field[force_text(field.column_name)]
            for field in self.get_fields()
        ]
        return headers

    def get_queryset(self):
        return self.Meta.model.objects.filter()



class BackOfficeAssetResource(RalphResourceMixin, resources.ModelResource):
    class Meta:
        ng_field2ralph_field = {
            'id': '',
            'barcode': '',
            'delivery_date': '',
            'deprecation_end_date': '',
            'deprecation_rate': '',
            'force_deprecation': '',
            'hostname': '',
            'invoice_date': '',
            'invoice_no': '',
            'loan_end_date': '',
            'model_id': 'model__name',
            'niw': '',
            'order_no': '',
            'price': '',
            'production_use_date': '',
            'production_year': '',
            'provider': '',
            'provider_order_date': '',
            'purchase_order': '',
            'request_date': '',
            'required_support': '',
            'sn': '',
            'source': '',
            'status': '',
            'task_url': '',
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_assets.Asset

    def get_queryset(self):
        return self.Meta.model.objects.filter(
            type=models_assets.AssetType.back_office,
        )



class DataCenterAssetResource(RalphResourceMixin, resources.ModelResource):
    service_env = fields.Field()
    def dehydrate_id(self, asset):
        return ""

    def dehydrate_service_env(self, asset):
        return "{}|{}".format(asset.service.name, asset.device_environment.name)

    class Meta:
        ng_field2ralph_field = {
            ## to be skipped
                'id': '',
            #    'asset_ptr': '',
            #    'baseobject_ptr': '',
            ## to be dehydrated
            'service_env': '',
            #TODO::
            #    'configuration_path': '',
            # complicated:
            #TODO::
            #    'parent': '',
            'barcode': '',
            #TODO:: m2m
            'connections': '',
            'created': '',
            'delivery_date': '',
            'deprecation_end_date': '',
            'deprecation_rate': '',
            'force_deprecation': '',
            'invoice_date': '',
            'invoice_no': '',
            'loan_end_date': '',
            'model': 'model__name',
            'modified': '',
            'niw': '',
            'order_no': '',
            'orientation': 'device_info__orientation',
            'position': '',
            'price': '',
            'production_use_date': '',
            'production_year': '',
            'provider': '',
            'provider_order_date': '',
            'purchase_order': '',
            'rack': 'device_info__rack__name',
            'remarks': '',
            'request_date': '',
            'required_support': '',
            'slot_no': 'device_info__slot_no',
            'slots': '',
            'sn': '',
            'source': '',
            'status': '',
            'task_url': '',
            'hostname': 'device_info__ralph_device__name',
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_assets.Asset

    def get_queryset(self):
        return self.Meta.model.objects.filter(
            type=models_assets.AssetType.data_center
        )


class AssetModelResource(RalphResourceMixin, resources.ModelResource):
    class Meta:
        ng_field2ralph_field = {
            'id': '',
            'category': 'category__slug',
            'cores_count': '',
            'height_of_device': '',
            'manufacturer': 'manufacturer__name',
            'power_consumption': '',
            'visualization_layout_back': '',
            'visualization_layout_front': '',
            ## verify, these missing in old ralph
            #'created': '',
            #'modified': '',
            #'name': '',
            #TODO:: map it
            #'type': '',
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_assets.AssetModel


class AssetCategoryResource(RalphResourceMixin, resources.ModelResource):
    id = fields.Field()
    slug = fields.Field()
    def dehydrate_slug(self, asset_category):
        return re.split(r'\d-', asset_category.slug)[-1]

    class Meta:
        ng_field2ralph_field = {
            'id': '',
            'created datetime': '',
            'created_by_id': '',
            'modified': '',
            'modified_by_id': '',
            'slug': '',
            'name': '',
            'code': '',
            'is_blade': '',
            'parent_id': 'parent__name',
            ## skip it
            # cache_version
            # level
            # lft
            # rght
            # tree_id
            # type
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_assets.AssetCategory


class ServiceEnvironmentResource(RalphResourceMixin, resources.ModelResource):
    service = fields.Field()
    environment = fields.Field()
    def dehydrate_service(self, ci_relation):
        return ci_relation.parent.name

    def dehydrate_environment(self, ci_relation):
        return ci_relation.child.name

    def get_queryset(self):
        return models_ci.CIRelation.objects.filter(
            type=models_ci.CI_RELATION_TYPES.CONTAINS,
            parent__type=models_ci.CIType.objects.get(name='Service'),
            child__type=models_ci.CIType.objects.get(name='Environment'),
        )

    class Meta:
        ng_field2ralph_field = {
            'id': '',
            'service': '',
            'environment': '',
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_ci.CIRelation


class ServiceResource(RalphResourceMixin, resources.ModelResource):
    def get_queryset(self):
        return models_ci.CIRelation.objects.filter(
            type=models_ci.CI_RELATION_TYPES.CONTAINS,
            parent__type=models_ci.CIType.objects.get(name='ProfitCenter'),
            child__type=models_ci.CIType.objects.get(name='Service'),
        )

    class Meta:
        ng_field2ralph_field = {
            'id': '',
            'name': 'child__name',
            'created': '',
            'modified': '',
            'profit_center': 'parent__name',
            #TODO:: no table in NG for now
            #'cost_center': '',
        }
        fields = [v or k for k, v in ng_field2ralph_field.items()]
        model = models_ci.CIRelation


class EnvironmentResource(EmptyIdMixin, resources.ModelResource):
    class Meta:
        fields = ('id', 'name', 'created', 'modified',)


######### AREK
from ralph_assets.licences.models import Licence, LicenceAsset, LicenceUser
from ralph_assets.models_support import Support


class LicenceResource(resources.ModelResource):
#     # ralph.licences.models.Licence
    class Meta:
        model = Licence
        fields = [
            'id', 'created', 'modified', 'manufacturer_id', 'licence_type_id',
            'software_category_id', 'number_bought', 'sn', 'niw', 'valid_thru',
            'order_no', 'price', 'accounting_id', 'invoice_date', 'provider',
            'invoice_no', 'remarks', 'license_details', 'licence_type',
            'software_category'
        ]

    def dehydrate_manufacturer(self, licence):
        return licence.manufacturer.name

    def dehydrate_licence_type(self, licence):
        return licence.licence_type.name

    def dehydrate_software_category(self, licence):
        return licence.software_category.name


class LicenceAssetResource(resources.ModelResource):
    class Meta:
        model = LicenceAsset

    def dehydrate_asset(self, rel):
        return rel.asset.barcode

    def dehydrate_licence(self, rel):
        return rel.licence.niw


class LicenceUserResource(resources.ModelResource):
    class Meta:
        model = LicenceUser

    def dehydrate_user(self, rel):
        return rel.user.username

    def dehydrate_licence(self, rel):
        return rel.licence.niw


class SupportAssetResource(resources.ModelResource):
    class Meta:
        model = Support.assets.through


class SupportResource(resources.ModelResource):
    # ralph.supports.models.Support
    class Meta:
        model = Support
        fields = [
            'id', 'name', 'created', 'modified', 'contract_id', 'description',
            'price', 'date_from', 'date_to', 'escalation_path',
            'contract_terms', 'additional_notes', 'sla_type', 'status',
            'producer', 'supplier', 'serial_no', 'invoice_no', 'invoice_date',
            'period_in_months'
        ]
######### END AREK
