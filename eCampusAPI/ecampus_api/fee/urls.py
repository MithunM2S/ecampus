from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fee.views import *
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'type', FeeTypeViewset)
router.register(r'category', FeeCategoryViewset)
router.register(r'fee-to-class', FeeToClassViewset)
router.register(r'payment-mode', PaymentModeViewset)
router.register(r'concession', FeeConcessionViewset)
router.register(r'collection', FeeCollectionViewset)
router.register(r'master-collection', FeeMasterCollectionViewset)
router.register(r'daily-report', DailyReportViewset)


urlpatterns = [
    path('fees/<student_id>/<fee_category_id>', FetchFees.as_view(), name='fetch_fees'),
    path('collection-report/', FeeCollectionReport.as_view({'get': 'list'}), name='fee_collection_report'),
    path('search/fee-to-class/', SearchFeeToClass.as_view(), name='search_fee_to_class'),
    path('daily-report-xlsx/', DailyReportXlsx.as_view(), name='daily_report_xlsx'),
    path('dashboard-report/', FeeDashboard.as_view(), name='fee_dashboard_report'),
    path('bill-to-bill-report/', BillToBillReport.as_view(), name='bill_to_bill'),
]
urlpatterns += router.urls
