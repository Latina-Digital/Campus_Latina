from django.apps import AppConfig


class ApiDataConfig(AppConfig):
    name = "apps.apidata"
    verbose_name = "Datos del campus (API)"

    def ready(self):
        from django.db.models.signals import m2m_changed, post_delete, pre_save

        from . import sync

        pre_save.connect(sync.on_pre_save, dispatch_uid="apidata-pre-save")
        post_delete.connect(sync.on_post_delete, dispatch_uid="apidata-post-delete")
        m2m_changed.connect(sync.on_m2m_changed, dispatch_uid="apidata-m2m")
