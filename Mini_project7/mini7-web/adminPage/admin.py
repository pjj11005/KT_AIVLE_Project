from django.contrib import admin

# Register your models here.
from .models import ChatLog, CsvUpload
# Register your models here.

class ChatLogAdmin(admin.ModelAdmin):
    list_display=('timestamp','short_question','short_answer')
    list_filter=('timestamp',)
    search_fields=('queston','answer')
    list_per_page=20

    def short_question(self, obj):
        return obj.question[:15]  # 질문의 앞 50자만 표시
    short_question.short_description = 'Question'

    def short_answer(self, obj):
        return obj.answer[:15]  # 답변의 앞 50자만 표시
    short_answer.short_description = 'Answer'

admin.site.register(ChatLog,ChatLogAdmin)
admin.site.register(CsvUpload)

# from django.contrib import admin 
# class ChatgptAdminSite(admin.AdminSite):
#     site_header='ChatGPT Admin'
#     site_title='ChatGPT Admin Portal'
# chatgpt_admin_site=ChatgptAdminSite(name='chatgptadmin')
# chatgpt_admin_site.register()
# from django.contrib.admin import AdminSite as DjangoAdminSite

# class AdminSite(DjangoAdminSite):
#     site_header='ChatGPT Admin'
#     site_url=settings.FRONTEND_URL

#     def get_url(self):
#         def wrap(view, cacheable=False):
#             def wrapper(*args, **kwargs):
#                 return self.admin_view(view,cacheable)(*args,**kwargs)
#             wrapper.admin_site = self
#             return update_wrapper(wrapper, view)
#         urls = [
#             path("myview", wrap(self.my_view), name="myview"),
#         ]
#         urls += super().get_urls()
#         return urls
#     def my_view(self, request, *args, **kwargs):
#         context = dict(super().each_context(request))
#         return TemplateResponse(request, "admin/my_view/test.html", context)


