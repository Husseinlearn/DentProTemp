import re
from django.core.exceptions import ValidationError

def validate_full_name(value: str) -> str:
    """
    Enforces that the full name contains at least four words.
    """
    if not value:
        raise ValidationError("الاسم الكامل مطلوب.")
    val_clean = value.strip()
    words = val_clean.split()
    if len(words) < 4:
        raise ValidationError("الاسم الكامل يجب أن يتكون من أربع كلمات على الأقل (الاسم الأول والثاني والثالث والأخير مجتمعين).")
    return val_clean

def validate_phone_number(value: str) -> str:
    """
    Enforces format: starts with 7 and has exactly 9 digits (e.g. 7XXXXXXXX).
    """
    if not value:
        raise ValidationError("رقم الهاتف مطلوب.")
    val_clean = value.strip()
    if not re.match(r'^7\d{8}$', val_clean):
        raise ValidationError("رقم الهاتف يجب أن يبدأ بـ 7 ويتكون من 9 أرقام. مثل (7XXXXXXXX).")
    return val_clean

def validate_email_format(value: str) -> str:
    """
    Validates standard email format using regular expressions.
    """
    if not value:
        return value
    val_clean = value.strip()
    email_regex = r'^[\w\.\+-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, val_clean):
        raise ValidationError("صيغة البريد الإلكتروني غير صحيحة.")
    return val_clean

def validate_gender(value: str) -> str:
    """
    Validates gender against allowed Arabic and English values.
    """
    if not value:
        raise ValidationError("الجنس مطلوب.")
    val_clean = value.strip()
    accepted = ['male', 'female', 'other', 'ذكر', 'أنثى', 'انثى', 'غير ذلك', 'اخر', 'آخر']
    if val_clean.lower() not in [g.lower() for g in accepted]:
        raise ValidationError(
            "الجنس يجب أن يكون أحد القيم المقبولة (ذكر، أنثى، غير ذلك، male، female، other)."
        )
    return val_clean
