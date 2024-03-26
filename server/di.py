from injector import Injector, SingletonScope
from server.database.client import SupabaseClient
from settings.settings import Settings, unsafe_typed_settings

def create_application_injector() -> Injector:
    _injector = Injector(auto_bind=True)
    _injector.binder.bind(Settings, to=unsafe_typed_settings)
    SUPABASE_URL = unsafe_typed_settings.supabase.url
    SUPABASE_KEY = unsafe_typed_settings.supabase.service_role_key
    _injector.binder.bind(SupabaseClient, to=SupabaseClient(SUPABASE_URL,SUPABASE_KEY), scope=SingletonScope)
    return _injector


"""
Global injector for the application.

Avoid using this reference, it will make your code harder to test.

Instead, use the `request.state.injector` reference, which is bound to every request
"""
global_injector: Injector = create_application_injector()
