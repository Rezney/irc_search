from django.shortcuts import render, redirect
from django.views.generic import View
from core.models import IRCMessage
from .forms import SearchForm
from itertools import chain


class HomeView(View):
    def get(self, request):
        ctx = []
        irc_channels = IRCMessage.objects.values('irc_channel').distinct()
        # If there are no messages in our DB we send an empty context and
        # handle informing the user in the template
        if not irc_channels:
            return render(request, 'irc_home.html')

        for channel in irc_channels:
            channel = channel['irc_channel']
            latest = IRCMessage.objects.filter(
                irc_channel=channel).values_list('date').latest('date')
            earliest = IRCMessage.objects.filter(
                irc_channel=channel).values_list('date').earliest('date')
            count = IRCMessage.objects.filter(irc_channel=channel).count()
            ctx.append({
                "name": channel,
                "latest": latest,
                "earliest": earliest,
                "count": count,
            })

        return render(request, 'irc_home.html', {'channel_details': ctx})


class SearchView(View):
    def get(self, request):
        # lets take channel_id from request when we click at channel details
        # in home
        channel_id = request.GET.get("channel_id", None)
        search_form = SearchForm(initial={"irc_channels": [channel_id]} if
                                 channel_id else None)
        irc_channels = IRCMessage.objects.values('irc_channel').distinct()
        if not irc_channels:
            return render(request, 'irc_home.html')
        # provide available channels for search and the form
        return render(request, 'irc_search.html',
                      {'form': search_form, 'channels': irc_channels})


class ResultsView(View):
    def get(self, request):
        channel_data = []

        request.session['search_term'] = None
        request.session['search_term2'] = None

        picked_channels = request.GET.getlist('irc_channels', [])

        search_str = request.GET.get('search_str')
        author = request.GET.get('author', None)
        contains = request.GET.get('contains', None)
        not_contain = request.GET.get('not_contain', None)
        not_older_then = request.GET.get('not_older_then', None)

        request.session['last_search_url'] = request.get_full_path()

        for channel in picked_channels:
            messages = IRCMessage.objects.filter(irc_channel=channel).order_by("-date")
            if not_older_then:
                messages = messages.filter(date__gte=not_older_then)
            if author:
                messages = messages.filter(nick=author)
            if search_str:
                messages = messages.filter(message__icontains=search_str)
                # we put search_str into session so we can use it for
                # highlighting, same for contains
                request.session['search_term'] = search_str
            if contains:
                messages = messages.filter(message__icontains=contains)
                request.session['search_term2'] = contains
            if not_contain:
                messages = messages.exclude(message__icontains=not_contain)
            channel_data.append({
                "name": channel,
                "messages": messages,
            })

        return render(request, 'irc_results.html',
                      {'channel_data': channel_data})


class LookAroundView(View):
    def get(self, request, channel, message_id):
        message_id = int(message_id)
        # we use message_picked for highlighting in the lookaround view
        message_picked = IRCMessage.objects.filter(
                         irc_channel=channel).get(pk=message_id)
        lookbehind = reversed(IRCMessage.objects.filter(irc_channel=channel).filter(date__lte=message_picked.date, pk__lt=message_picked.pk).order_by("-date", "-pk")[:7])
        lookahead = IRCMessage.objects.filter(irc_channel=channel).filter(date__gte=message_picked.date, pk__gt=message_picked.pk).order_by("date", "pk")[:7]

        lookaround = list(chain(lookbehind, [message_picked], lookahead))

        return render(request, 'irc_lookaround.html',
                      {'lookaround': lookaround, 'channel': channel,
                       'message_picked': message_picked}
                      )

