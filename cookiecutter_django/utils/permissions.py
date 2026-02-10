# from typing import Any

# from rest_framework.exceptions import PermissionDenied
# from rest_framework.permissions import BasePermission
# from rest_framework.request import Request
# from rest_framework.views import APIView

# from core.backend.devices.models import Device
# from core.backend.discos.models import Staff
# from core.utils.json_schema_interface import UserTypes


# class AccountPermissions:
#     class IsDisco(BasePermission):
#         def has_permission(self, request: Request, view: APIView) -> bool:
#             if request.user.account.is_disco:
#                 return True
#             raise PermissionDenied("Only a disco can make this request")

#         def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
#             return bool(request.user.account == obj.disco.account)

#     class IsDiscoOrStaff(BasePermission):
#         def has_permission(self, request: Request, view: APIView) -> bool:
#             if request.user.account.is_consumer:
#                 raise PermissionDenied("This request can only be made by discos and staff")
#             if request.user.account.type in [UserTypes.DISCO, UserTypes.STAFF]:
#                 return True
#             raise PermissionDenied("Only a disco can make this request")

#         def has_object_permission(self, request: Request, view: APIView, obj: Device) -> bool:
#             if request.user.account.is_consumer:
#                 raise PermissionDenied("This request can only be made by discos and staff")
#             if request.user.account.is_disco:
#                 if obj.disco.account == request.user.account:
#                     return True
#             if request.user.account.is_staff:
#                 staff = Staff.objects.get(account=request.user.account)
#                 if obj.staffs.contains(staff):
#                     return True
#             raise PermissionDenied("Only a disco can make this request")

#     class IsConsumer(BasePermission):
#         def has_permission(self, request: Request, view: APIView) -> bool:
#             if request.user.account.is_consumer:
#                 return True

#         def has_object_permission(self, request: Request, view: APIView, obj: Device) -> bool:
#             if request.user.account.is_consumer:
#                 return True

#     class IsStaffAdmin(BasePermission):
#         def has_permission(self, request: Request, view: APIView) -> bool:
#             if request.user.account.is_staff:
#                 staff = Staff.objects.get(account=request.user.account)
#                 if staff.permissions.contains("ADMIN"):
#                     return True
#                 raise PermissionDenied("You need to be an admin to make this request")
