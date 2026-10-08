from django.apps import AppConfig


class ServicesConfig(AppConfig):
    name = "services"

    def ready(self):
        """Auto-seed the demo content so a fresh checkout shows data.

        Runs on `runserver`/`migrate`. Safe no-op when tables are missing or
        when content already exists.
        """
        try:
            import warnings

            from django.db import connection

            # Silence Django's "query during app initialization" warning: this
            # read really is the point of the hook and is fully safe.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                tables = set(connection.introspection.table_names())
                if "services_service" not in tables:
                    return
                from services.models import Service

                if Service.objects.exists():
                    return
                from django.core.management import call_command

                call_command("seed_demo", verbosity=0)
        except Exception:
            # Never block startup because of the auto-seed.
            return