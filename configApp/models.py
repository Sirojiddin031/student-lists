
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    
    def create_user(self, phone, password=None, **extra_fields):
        
        if not phone:
            raise ValueError('The Phone number must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '998900404001'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    username = None
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField('Departments', related_name='teachers')
    course = models.ManyToManyField('Course', related_name="teachers")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.user.phone
    
    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('studying', 'Studying'),
        ('graduated', 'Graduated'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.student} - {self.course} ({self.status})"

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField('Departments', related_name='worker')
    course = models.ManyToManyField(Course, related_name='worker')
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone

class Departments(models.Model):
    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    age = models.IntegerField()
    group = models.ManyToManyField('Group', related_name='student')
    course = models.ManyToManyField(Course, related_name='student')
    is_line = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.user.phone
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

class Parents(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    descriptions = models.CharField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class Day(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class Rooms(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class TableType(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class Table(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Rooms, on_delete=models.RESTRICT)
    type = models.ForeignKey(TableType, on_delete=models.RESTRICT)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.start_time

class Group(models.Model):
    
    name = models.CharField(max_length=255)
    students = models.ManyToManyField(Student, related_name="groups")
    title = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    teacher = models.ManyToManyField(Worker, related_name='teacher')
    table = models.ForeignKey(Table, on_delete=models.RESTRICT)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.CharField(max_length=15, blank=True, null=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class Topics(models.Model):
    title = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class GroupHomeWork(models.Model):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    topic = models.ForeignKey(Topics, on_delete=models.RESTRICT)
    
    is_active = models.BooleanField(default=True)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

class HomeWork(models.Model):
    groupHomeWork = models.ForeignKey(GroupHomeWork, on_delete=models.RESTRICT)
    price = models.CharField(max_length=5, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    link = models.URLField()
    
    is_active = models.BooleanField(default=False)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

class AttendanceLevel(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class Attendance(models.Model):
    level = models.ForeignKey(AttendanceLevel, on_delete=models.RESTRICT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)

    def __str__(self):
        return self.level

from typing import TYPE_CHECKING, Any, List, Optional, Union

from django.contrib.auth import models as auth_models
from django.db.models.manager import EmptyManager
from django.utils.functional import cached_property

from rest_framework.settings import api_settings

if TYPE_CHECKING:
    from .models import Token


class TokenUser:
    """
    Token orqali autentifikatsiya qilinadigan foydalanuvchi klassi.
    Bu klass JWT asosida autentifikatsiya qilingan foydalanuvchilar uchun ishlatiladi.
    """

    is_active = True  # Token orqali kirgan foydalanuvchi har doim aktiv bo‘ladi

    _groups = EmptyManager(auth_models.Group)
    _user_permissions = EmptyManager(auth_models.Permission)

    def __init__(self, token: "Token") -> None:
        self.token = token

    def __str__(self) -> str:
        return f"TokenUser {self.id}"

    @cached_property
    def id(self) -> Union[int, str]:
        return self.token[api_settings.USER_ID_CLAIM]

    @cached_property
    def pk(self) -> Union[int, str]:
        return self.id

    @cached_property
    def phone(self) -> str:
        """Foydalanuvchining telefon raqami"""
        return self.token.get("phone", "")

    @cached_property
    def full_name(self) -> str:
        """Foydalanuvchining to‘liq ismi"""
        return self.token.get("full_name", "")

    @cached_property
    def is_staff(self) -> bool:
        return self.token.get("is_staff", False)

    @cached_property
    def is_superuser(self) -> bool:
        return self.token.get("is_superuser", False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TokenUser):
            return NotImplemented
        return self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def save(self) -> None:
        raise NotImplementedError("Token foydalanuvchilari DB da saqlanmaydi")

    def delete(self) -> None:
        raise NotImplementedError("Token foydalanuvchilari DB da saqlanmaydi")

    def set_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token foydalanuvchilari DB da saqlanmaydi")

    def check_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token foydalanuvchilari DB da saqlanmaydi")

    @property
    def groups(self) -> auth_models.Group:
        return self._groups

    @property
    def user_permissions(self) -> auth_models.Permission:
        return self._user_permissions

    def get_group_permissions(self, obj: Optional[object] = None) -> set:
        return set()

    def get_all_permissions(self, obj: Optional[object] = None) -> set:
        return set()

    def has_perm(self, perm: str, obj: Optional[object] = None) -> bool:
        return False

    def has_perms(self, perm_list: List[str], obj: Optional[object] = None) -> bool:
        return False

    def has_module_perms(self, module: str) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True

    def get_phone(self) -> str:
        return self.phone

    def __getattr__(self, attr: str) -> Optional[Any]:
        """Token serializerida qo‘shimcha claimlar bo‘lsa, ularni olish uchun"""
        return self.token.get(attr, None)
