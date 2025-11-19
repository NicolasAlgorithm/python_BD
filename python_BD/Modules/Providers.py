class Provider:
    def __init__(self, provider_id, name, contact_info):
        self.provider_id = provider_id
        self.name = name
        self.contact_info = contact_info

class ProviderManager:
    def __init__(self):
        self.providers = {}

    def create_provider(self, provider_id, name, contact_info):
        if provider_id in self.providers:
            raise ValueError("Provider ID already exists.")
        self.providers[provider_id] = Provider(provider_id, name, contact_info)

    def read_provider(self, provider_id):
        return self.providers.get(provider_id)

    def update_provider(self, provider_id, name=None, contact_info=None):
        provider = self.providers.get(provider_id)
        if provider is None:
            raise ValueError("Provider not found.")
        if name:
            provider.name = name
        if contact_info:
            provider.contact_info = contact_info

    def delete_provider(self, provider_id):
        if provider_id not in self.providers:
            raise ValueError("Provider not found.")
        del self.providers[provider_id]