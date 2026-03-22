from two_factor import urls as two_factor_urls


app_name = "two_factor"

if isinstance(two_factor_urls.urlpatterns, tuple):
    urlpatterns = two_factor_urls.urlpatterns[0]
else:
    urlpatterns = two_factor_urls.urlpatterns
