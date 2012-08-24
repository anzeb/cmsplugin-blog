from django.utils.translation import ugettext_lazy as _

from tagging.models import TaggedItem
from tagging.utils import get_tag_list

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.utils import get_language_from_request
from cms.models.pluginmodel import CMSPlugin

from simple_translation.utils import get_translation_filter_language

from cmsplugin_blog.models import LatestEntriesPlugin, Entry, ArchivePlugin

class CMSLatestEntriesPlugin(CMSPluginBase):
    """
        Plugin class for the latest entries
    """
    model = LatestEntriesPlugin
    name = _('Latest entries')
    render_template = "cmsplugin_blog/latest_entries.html"
    
    def render(self, context, instance, placeholder):
        """
            Render the latest entries
        """
        if 'month' in context["request"].GET and 'year' in context["request"].GET :
            month = context["request"].GET['month']
            year = context["request"].GET['year']
            qs = Entry.published.filter(pub_date__month=month, pub_date__year=year)
        else:
            qs = Entry.published.all()
        
        if instance.current_language_only:
            language = get_language_from_request(context["request"])
            kw = get_translation_filter_language(Entry, language)
            qs = qs.filter(**kw)
            
        if instance.tagged:
            tags = get_tag_list(instance.tagged)
            qs  = TaggedItem.objects.get_by_model(qs , tags)
            # change render template - using tag
            self.render_template = "cmsplugin_blog/latest_entries_" + str(tags[0]) + ".html"        

        latest = qs[:instance.limit]
        
        context.update({
            'instance': instance,
            'latest': latest,
            'object_list': latest,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(CMSLatestEntriesPlugin)

class SideMenu(CMSPluginBase):
    """
        Plugin class for the side menu
    """
    model = ArchivePlugin
    name = _("Side-menu archive plugin")
    render_template = "cmsplugin_blog/side_menu.html"

    def render(self, context, instance, placeholder):
        """
            Render the sidebar arhive menu
        """ 
        # change render template - using tag
        if (instance.optionalTemplate):
            self.render_template = instance.optionalTemplate
        elif instance.tagged:
            tags = get_tag_list(instance.tagged)
            self.render_template = "cmsplugin_blog/side_menu_" + str(tags[0]) + ".html"           

        qs = Entry.published.filter(tags=tags[0]) 

        context.update({
            'instance': instance,
            'archive': qs,
            'object_list': qs,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(SideMenu)


