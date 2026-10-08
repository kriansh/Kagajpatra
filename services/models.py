from django.db import models


class Service(models.Model):
    """A government service the citizen can look up (birth certificate, tax, ...)."""

    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=8, default="📄", help_text="Emoji used on cards")
    name_en = models.CharField(max_length=120)
    name_ne = models.CharField(max_length=120)
    tagline_en = models.CharField(max_length=255)
    tagline_ne = models.CharField(max_length=255)
    overview_en = models.TextField(blank=True)
    overview_ne = models.TextField(blank=True)
    office_en = models.CharField(
        max_length=200, help_text="Which office handles this service"
    )
    office_ne = models.CharField(max_length=200)
    fee_en = models.CharField(max_length=200, blank=True)
    fee_ne = models.CharField(max_length=200, blank=True)
    timeline_en = models.CharField(max_length=200, blank=True)
    timeline_ne = models.CharField(max_length=200, blank=True)
    deadline_en = models.CharField(
        max_length=200, blank=True, help_text="Statutory deadline, e.g. register within 35 days"
    )
    deadline_ne = models.CharField(max_length=200, blank=True)
    tips_en = models.TextField(blank=True)
    tips_ne = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name_en"]

    def __str__(self):
        return self.name_en

    def name(self, lang="en"):
        return self.name_ne if lang == "ne" else self.name_en

    def tagline(self, lang="en"):
        return self.tagline_ne if lang == "ne" else self.tagline_en

    def as_summary(self, lang="en"):
        """Compact text used to ground the AI assistant."""
        parts = [f"{self.name(lang)} — {self.tagline(lang)}"]
        if getattr(self, f"office_{lang}"):
            parts.append(f"Office: {getattr(self, f'office_{lang}')}")
        if getattr(self, f"fee_{lang}"):
            parts.append(f"Fee: {getattr(self, f'fee_{lang}')}")
        if getattr(self, f"deadline_{lang}"):
            parts.append(f"Deadline: {getattr(self, f'deadline_{lang}')}")
        return " | ".join(parts)


class ChecklistItem(models.Model):
    """One document/material the citizen must bring for a service."""

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="checklist")
    group_en = models.CharField(max_length=120, help_text="e.g. Your documents")
    group_ne = models.CharField(max_length=120)
    label_en = models.CharField(max_length=255)
    label_ne = models.CharField(max_length=255)
    note_en = models.CharField(max_length=255, blank=True)
    note_ne = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.name_en}: {self.label_en}"


class Step(models.Model):
    """Ordered process step for a service."""

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="steps")
    title_en = models.CharField(max_length=255)
    title_ne = models.CharField(max_length=255)
    detail_en = models.TextField(blank=True)
    detail_ne = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.name_en}: {self.title_en}"


class WorkingDay(models.Model):
    """Office hours per weekday (Nepal: Saturday is the weekly holiday)."""

    DAYS = [
        (0, "Sunday"),
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
    ]
    day = models.PositiveSmallIntegerField(choices=DAYS, unique=True)
    open_time = models.TimeField(null=True, blank=True, help_text="Blank = closed")
    close_time = models.TimeField(null=True, blank=True)
    note_en = models.CharField(max_length=255, blank=True)
    note_ne = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["day"]

    def __str__(self):
        return self.get_day_display()

    @property
    def is_closed(self):
        return self.open_time is None or self.close_time is None

    @property
    def is_half_day(self):
        if self.is_closed:
            return False
        return "half" in self.note_en.lower() or "आधा" in self.note_ne


class Holiday(models.Model):
    """Public holiday (all offices closed)."""

    date = models.DateField(unique=True)
    name_en = models.CharField(max_length=150)
    name_ne = models.CharField(max_length=150)
    note_en = models.CharField(max_length=255, blank=True)
    note_ne = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} {self.name_en}"

    def name(self, lang="en"):
        return self.name_ne if lang == "ne" else self.name_en


class SiteInfo(models.Model):
    """Singleton-ish settings shown site-wide (address, generic office info)."""

    key = models.SlugField(unique=True, default="default")
    label_en = models.CharField(max_length=150)
    label_ne = models.CharField(max_length=150)
    value_en = models.CharField(max_length=400)
    value_ne = models.CharField(max_length=400)
    icon = models.CharField(max_length=8, default="ℹ️")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label_en
