from django.views.generic import TemplateView, ListView


class IndexTemplateView(TemplateView):
    template_name = 'main/index.html'


