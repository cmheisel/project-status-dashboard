"""Functions and classes for interacting with JIRA."""

import requests

from django.conf import settings


def query_url(filter_id, jira_url=None):
    """
    Create a JIRA query URL to fetch results.

    Args:
        filter_id (int): ID of JIRA filter to query
        jira_url (str): FQDN and scheme Example: 'https://jira.example.com'
    Returns:
        str: URL
    """
    jira_url = jira_url or settings.JIRA_URL
    return "{}/rest/api/2/search?jql=filter={}&maxResults=999".format(
        jira_url,
        filter_id,
    )


def fetch_query_results(filter_id):
    """
    Get results from JIRA.

    Args:
        filter_id (int): ID of JIRA filter to query_url
    Returns:
        list[JIRA.Issue]: List of issue objects from query
    """
    url = query_url(filter_id)
    results = requests.get(url, auth=settings.JIRA_AUTH, verify=settings.JIRA_SSL_VERIFY).json()
    return results


def summarize_results(results):
    """
    Summarize the JIRA issues into a standard dictionary.

    Args:
        results (list[JIRA.Issue]): List of issue objects from a JIRA query
    Returns:
        dict:
            'incomplete': (int) Count of issues who's status is not in
                settings.JIRA_DONE
            'complete': (int) Count of issues whose status is
                in settings.JIRA_DONE
            'pct_complete': (float) complete/total
            'total': (int) Total of all issues: complete and incomplete
            'fetched_at': (datetime) When the results were pulled
    """
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
    """
    Summarize the results of a JIRA filter.

    Args:
        filter_id (int): ID of JIRA filter
    Returns:
        dict: Results from summarize_results
    """
    return summarize_results(fetch_query_results(filter_id))
