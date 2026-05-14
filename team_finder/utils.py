import random
import re
import uuid
from io import BytesIO
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont


PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")

GITHUB_ALLOWED_HOSTS = {"github.com", "www.github.com"}

GITHUB_URL_ERROR_MESSAGE = "Ссылка должна вести на GitHub."
PHONE_FORMAT_ERROR_MESSAGE = "Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
PHONE_EXISTS_ERROR = "Пользователь с таким телефоном уже существует."

AVATAR_IMAGE_SIZE = 256
AVATAR_FONT_SIZE = 128
AVATAR_CENTER_DIVISOR = 2
AVATAR_VERTICAL_OFFSET = 8
AVATAR_FONT_NAME = "DejaVuSans-Bold.ttf"
AVATAR_IMAGE_FORMAT = "PNG"
AVATAR_FILE_EXTENSION = "png"
AVATAR_TEXT_COLOR = "#FFFFFF"

AVATAR_BG_LIGHT_PURPLE = "#E9D5FF"
AVATAR_BG_LIGHT_MINT = "#BFDBFE"
AVATAR_BG_LIGHT_SAGE = "#BBF7D0"
AVATAR_BG_LIGHT_PEACH = "#FDE68A"
AVATAR_BG_LIGHT_ROSE = "#FBCFE8"
AVATAR_BG_LIGHT_YELLOW = "#DDD6FE"

AVATAR_BACKGROUND_COLORS = (
    AVATAR_BG_LIGHT_PURPLE,
    AVATAR_BG_LIGHT_MINT,
    AVATAR_BG_LIGHT_SAGE,
    AVATAR_BG_LIGHT_PEACH,
    AVATAR_BG_LIGHT_ROSE,
    AVATAR_BG_LIGHT_YELLOW,
)


def normalize_phone(phone: str) -> str:
    phone = (phone or "").strip().replace(" ", "").replace("-", "")
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


def validate_phone_format(phone: str) -> str:
    phone = normalize_phone(phone)
    if not PHONE_RE.match(phone):
        raise ValidationError(PHONE_FORMAT_ERROR_MESSAGE)

    return phone


def clean_phone(phone: str, user_model, instance=None) -> str:
    phone = validate_phone_format(phone)

    legacy_phone = "8" + phone[2:] if phone.startswith("+7") else phone
    users_with_same_phone = user_model.objects.filter(
        phone__in=[phone, legacy_phone])

    if instance and instance.pk:
        users_with_same_phone = users_with_same_phone.exclude(pk=instance.pk)

    if users_with_same_phone.exists():
        raise ValidationError(PHONE_EXISTS_ERROR)

    return normalize_phone(phone)


def validate_github_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return value

    parsed = urlparse(value)
    host = (parsed.netloc or "").lower()

    if host not in GITHUB_ALLOWED_HOSTS:
        raise ValidationError(GITHUB_URL_ERROR_MESSAGE)

    return value


def paginate_queryset(request, queryset, per_page: int):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def generate_initial_avatar(name: str, email: str) -> ContentFile:
    background_color = random.choice(AVATAR_BACKGROUND_COLORS)
    image = Image.new(
        "RGB",
        (AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE),
        background_color,
    )
    draw = ImageDraw.Draw(image)
    letter = (name[:1] or email[:1] or "U").upper()

    try:
        font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = (
        (AVATAR_IMAGE_SIZE - text_width) / AVATAR_CENTER_DIVISOR,
        (AVATAR_IMAGE_SIZE - text_height) / AVATAR_CENTER_DIVISOR
        - AVATAR_VERTICAL_OFFSET,
    )

    draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format=AVATAR_IMAGE_FORMAT)

    filename = f"avatar_{uuid.uuid4().hex}.{AVATAR_FILE_EXTENSION}"

    return ContentFile(buffer.getvalue(), name=filename)
