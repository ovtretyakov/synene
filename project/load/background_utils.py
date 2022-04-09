from background_task import background

from project.core.models import LoadSource

@background
def load_source_download(load_source_pk, local_files):
    load_source = LoadSource.objects.get(pk=load_source_pk)
    load_source.download(local_files)
