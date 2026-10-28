from django.apps import AppConfig


class ApiDataConfig(AppConfig):
    name = "apps.apidata"
    verbose_name = "Datos del campus (API)"

    def ready(self):
        from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save

        from . import live, sync

        pre_save.connect(sync.on_pre_save, dispatch_uid="apidata-pre-save")
        post_delete.connect(sync.on_post_delete, dispatch_uid="apidata-post-delete")
        m2m_changed.connect(sync.on_m2m_changed, dispatch_uid="apidata-m2m")
        post_save.connect(live.on_change, dispatch_uid="apidata-live-save")
        post_delete.connect(live.on_change, dispatch_uid="apidata-live-delete")
        m2m_changed.connect(live.on_m2m_change, dispatch_uid="apidata-live-m2m")
