from django.http import HttpResponse


def index(request):
    return HttpResponse("查看数字专辑销售数据请访问http://y.saoju.net/szzj/")
