import requests

from django.conf import settings


def query_url(filter_id, jira_url=None):
    jira_url = jira_url or settings.JIRA_URL
    return "{}/rest/api/2/search?jql=filter={}&maxResults=999".format(
        jira_url,
        filter_id,
    )


def fetch_query_results(filter_id):
    url = query_url(filter_id)
    results = requests.get(url, auth=settings.JIRA_AUTH).json()
    return results


def summarize_results(results):
    summary = {
        'incomplete': 0,
        'complete': 0,
        'pct_complete': 0,
        'total': 0,
    }
    total = results['total']
    for issue in results['issues']:
        if issue['fields']['status']['name'] in settings.JIRA_DONE:
            summary['complete'] += 1
        else:
            summary['incomplete'] += 1

    summary['total'] = total
    summary['pct_complete'] = summary['complete'] / float(total)
    return summary


def summarize_query(filter_id):
    return summarize_results(fetch_query_results(filter_id))
