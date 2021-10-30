from django.db import models
from django.db.models.deletion import SET_NULL
from enumchoicefield import ChoiceEnum, EnumChoiceField
from auth_app.models import TimeStampMixin, User
from django.contrib.postgres.fields import ArrayField
from backend.doctor_app.models import Doctor

from backend.user_app.models import Appointment, DiscountType


class Department(ChoiceEnum):
    SALES = 'sales'
    MANAGEMENT = 'management'
    CUSTOMER_SUPPORT = 'customer_support'
    PHARMACY = 'pharmacy'
    INVENTORY = 'inventory'
    # Other departments we can consider later
    # DEVELOPMENT = 'development'
    # MARKETING = 'marketing'

class AdminStaffPermissions(ChoiceEnum):
    MANAGE_USERS = 'manage_users'
    MANAGE_CLIENTS = 'manage_clients'
    MANAGE_ADMIN_STAFF = 'manage_admin_staff'
    # Here client means Doctor, Hospital, Pharmacy etc. and not Users.
    HANDLE_USER_REQUESTS = 'handle_user_request'
    HANDLE_USER_COMPLAINTS = 'handle_user_complaints'
    HANDLE_REVIEWS = 'handle_reviews'
    HANDLE_CLIENT_REQUESTS = 'handle_client_request'
    HANDLE_CLIENT_COMPLAINTS = 'handle_client_complaints'
    HANDLE_PHARMACY_ORDERS = 'handle_pharmacy_order'
    HANDLE_PHARMACY_HELP_REQUESTS = 'handle_pharmacy_complaint'
    MANAGE_PHARMACY_STOCK = 'manage_pharmacy_stock'
    CREATE_COUPONS = 'create_coupons'
    ISSUE_COUPONS = 'issue_coupons'
    ALL = 'all'


class AdminStaffPosts(ChoiceEnum):
    BUSINESS_DEVELOPMENT_EXECUTIVE = 'business_development_executive'
    SENIOR_BUSINESS_DEVELOPMENT_EXECUTIVE = 'senior_business_development_executive'
    SALES_MANAGER = 'sales_manager'
    OPERATION_MANAGEMENT_EXECUTIVE = 'operation_management_executive'
    OPERATON_MANAGER = 'operation_manager'
    CUSTOMER_SUPPORT_EXECUTIVE = 'customer_support_executive'
    CLIENT_SUPPORT_EXECUTIVE = 'client_support_executive'
    SENOIR_SUPPORT_EXECUTIVE = 'senior_support_executive'
    RELATIONSHIP_MANAGER = 'relationship_manager'
    INVENTORY_MANAGER = 'inventory_manager'
    EXECUTIVE_PHARMACIST = 'executive_pharmacist'
    SENIOR_EXECUTIVE_PHARMACIST = 'senior_executive_pharmacist'
    # Other posts we can consider later
    # CEO = 'ceo'
    # CFO = 'cfo'
    # CTO = 'cto'
    # DEVELOPER = 'developer'
    # SENIOR_DEVELOPER = 'senior_developer'
    # TEAM_LEADER = 'team_leader'
    # PROJECT_MANAGER = 'project_manager'
    # ACCOUNTANT = 'accountant'


default_role_permissions = [
    {
        "department": Department.SALES,
        "post": AdminStaffPosts.BUSINESS_DEVELOPMENT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.MANAGE_USERS,
                        AdminStaffPermissions.MANAGE_CLIENTS,
                        AdminStaffPermissions.ISSUE_COUPONS)
    },
    {
        "department": Department.SALES,
        "post": AdminStaffPosts.SENIOR_BUSINESS_DEVELOPMENT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.MANAGE_USERS,
                        AdminStaffPermissions.MANAGE_CLIENTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS)
    },
    {
        "department": Department.SALES,
        "post": AdminStaffPosts.SALES_MANAGER,
        "permissions": (AdminStaffPermissions.MANAGE_USERS,
                        AdminStaffPermissions.MANAGE_CLIENTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS)
    },
    {
        "department": Department.MANAGEMENT,
        "post": AdminStaffPosts.OPERATION_MANAGEMENT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.ALL)
    },
    {
        "department": Department.MANAGEMENT,
        "post": AdminStaffPosts.OPERATON_MANAGER,
        "permissions": (AdminStaffPermissions.ALL)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.CUSTOMER_SUPPORT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.CLIENT_SUPPORT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.HANDLE_CLIENT_REQUESTS,
                        AdminStaffPermissions.HANDLE_CLIENT_COMPLAINTS,
                        AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.SENOIR_SUPPORT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.HANDLE_CLIENT_REQUESTS,
                        AdminStaffPermissions.HANDLE_CLIENT_COMPLAINTS,
                        AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.SENOIR_SUPPORT_EXECUTIVE,
        "permissions": (AdminStaffPermissions.HANDLE_CLIENT_REQUESTS,
                        AdminStaffPermissions.HANDLE_CLIENT_COMPLAINTS,
                        AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.RELATIONSHIP_MANAGER,
        "permissions": (AdminStaffPermissions.HANDLE_CLIENT_REQUESTS,
                        AdminStaffPermissions.HANDLE_CLIENT_COMPLAINTS,
                        AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS,
                        AdminStaffPermissions.MANAGE_USERS,
                        AdminStaffPermissions.MANAGE_CLIENTS)
    },
    {
        "department": Department.CUSTOMER_SUPPORT,
        "post": AdminStaffPosts.RELATIONSHIP_MANAGER,
        "permissions": (AdminStaffPermissions.HANDLE_CLIENT_REQUESTS,
                        AdminStaffPermissions.HANDLE_CLIENT_COMPLAINTS,
                        AdminStaffPermissions.HANDLE_USER_REQUESTS,
                        AdminStaffPermissions.HANDLE_USER_COMPLAINTS,
                        AdminStaffPermissions.CREATE_COUPONS,
                        AdminStaffPermissions.ISSUE_COUPONS,
                        AdminStaffPermissions.MANAGE_USERS,
                        AdminStaffPermissions.MANAGE_CLIENTS)
    },
    {
        "department": Department.INVENTORY,
        "post": AdminStaffPosts.INVENTORY_MANAGER,
        "permissions": (AdminStaffPermissions.MANAGE_PHARMACY_STOCK)
    },
    {
        "department": Department.PHARMACY,
        "post": AdminStaffPosts.EXECUTIVE_PHARMACIST,
        "permissions": (AdminStaffPermissions.HANDLE_PHARMACY_ORDERS)
    },
    {
        "department": Department.PHARMACY,
        "post": AdminStaffPosts.SENIOR_EXECUTIVE_PHARMACIST,
        "permissions": (AdminStaffPermissions.HANDLE_PHARMACY_ORDERS,
                        AdminStaffPermissions.HANDLE_PHARMACY_HELP_REQUESTS)
    }
]


# Create your models here.
class AdminStaff(TimeStampMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    dob = models.DateField()
    image = models.TextField()
    post = EnumChoiceField(AdminStaffPosts)
    designation = models.CharField(max_length=256, blank=True)
    department = EnumChoiceField(Department)
    permissions = ArrayField(EnumChoiceField(AdminStaffPermissions))

class MedicineCompositionElement(models.Model):
    element = models.CharField(max_length=256)  

class MedicineForm(ChoiceEnum):
    TABLET = 'tablet'
    SYRUP_OR_GEL = 'syrup_or_gel'
    OTHER = 'OTHER'
    
class Medicine(models.Model):
    name = models.CharField(max_length=256)
    composition = models.ManyToManyField(MedicineCompositionElement, related_name='medicine_composition')
    description = models.TextField()
    other_details = models.TextField()
    used_for = ArrayField(models.CharField(max_length=256))
    highlights = ArrayField(models.CharField(max_length=256))

class MedicineUnit(models.Model):
    medicine_form = EnumChoiceField(MedicineForm)
    quantity_per_unit = models.PositiveIntegerField()
    volume_per_unit = models.PositiveIntegerField()
    unit_details = ArrayField(models.CharField(max_length=256))

class MedicineStock(TimeStampMixin):
    Medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    medicine_unit = models.ForeignKey(MedicineUnit, on_delete=models.CASCADE)
    # Volume will be used for medicines which comes in bottle and unit is "ml"
    manufacturing_date = models.PositiveIntegerField()
    manufacturing_month = models.PositiveIntegerField()
    manufacturing_year = models.PositiveIntegerField()
    expiry_date = models.PositiveIntegerField()
    expiry_month = models.PositiveIntegerField()
    expiry_year = models.PositiveIntegerField()
    mrp = models.FloatField()
    discount = models.PositiveIntegerField()
    discount_type = EnumChoiceField(DiscountType)

class MedicineOrder(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    appointment_id = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    prescribed_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    prescribed_by_other = models.CharField(max_length=256, blank=True)
    prescription = models.TextField(blank=True)
    estimated_amount = models.FloatField()
    final_amount = models.FloatField()
    expected_delivery_date = models.DateField()

class MedicineOrderItem(models.Model):
    order = models.ForeignKey(MedicineOrder, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL)
    medicine_stock = models.ForeignKey
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()
    remark = models.CharField(max_length=256, blank=True)
        
class OrderStatus(ChoiceEnum):
    CREATED = 'created'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    PROCESSING = 'processing'
    PENDING = 'pending'
    SHIPPED = 'shipped'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    RETURN_REQUESTED = 'return_requested'
    RETURN_APPROVED = 'return_approved'
    RETURN_REJECTED = 'return_rejected'
    RETURN_CANCELLED = 'return_cancelled'
    RETURN_REFUSED = 'return_refused'
    # Refused by user - If courier partner went to user address and he didn't returned or he was not available etc.
    PICKUP_NOT_ACCEPTED = 'pickup_not_accepted'
    # Not accepted by courier partner - If courier partner find that medicine is not in acceptable condition
    PICKUP_COMPLETED = 'pickup_completed'
    REFUND_APPROVED = 'refund_approved'
    REFUND_INITIATED = 'refund_initiated'
    REFUND_COMPLETED = 'refund_completed'

class MedicineOrderStatus(TimeStampMixin):
    medicine_order = models.ForeignKey(MedicineOrder, on_delete=models.CASCADE)
    status = EnumChoiceField(OrderStatus,
                            default=OrderStatus.CREATED)
    details = models.CharField(max_length=256, blank=True)
    remark = models.CharField(max_length=256, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL)    
