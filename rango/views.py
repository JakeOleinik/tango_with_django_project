from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response

def about(request):
    # If the visits session varible exists, take it and use it.
    # If it doesn't, we haven't visited the site so set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context = {'boldmessage': "About page!", 'visits': count}
    # remember to include the visit data
    return render(request, 'rango/about.html', context)
	

def category(request, category_name_slug):
    context = {}
    try:
        category = Category.objects.filter(slug=category_name_slug)[0]
        context['category_name'] = category.name
        category.views+=1
        category.save()

        pages = Page.objects.filter(category=category)
        context['pages'] = pages

        context['category'] = category
    except:
        pass

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
            context['result_list'] = result_list


    return render(request, 'rango/category.html', context)

def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)

			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()
        

	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
    if request.method == 'GET':
        if 'pageid' in request.GET:
            pageid = request.GET['pageid']
            page = Page.objects.get(id=pageid)
            page.views+=1
            print page, page.views
            page.save()
            return HttpResponseRedirect(page.url)
    return HttpResponseRedirect('/rango/')

def add_profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            return HttpResponseRedirect('/rango/')

        else:
            print profile_form.errors
    else:
        profile_form = UserProfileForm()

    return render(request,
        'rango/profile_registration.html',
        {'profile_form': profile_form})

#Uses AJAX
@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)

# HELPER function
def get_category_list(max_results=0, starts_with=''):
    cat_list = Category.objects.all()
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        cat_list = cat_list[:max_results]
    return cat_list

#Uses AJAX
def suggest_category(request):
    print 'reached'
    cat_list = []
    context = {}
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        if 'actid' in request.GET.keys():
            actid = request.GET['actid']
            act_cat = Category.objects.get(id=actid)
            context['act_cat'] = act_cat

    cat_list = get_category_list(8, starts_with)
    context['cats'] = cat_list


    return render(request, 'rango/category_list.html', context)



