"""Functions and classes for interacting with JIRA."""
import logging

import requests

from django.conf import settings

LOGGER = logging.getLogger("dashboard.services.jira")


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


def fetch_query_results(filter_id, requests=requests, logger=LOGGER):
    """
    Get results from JIRA.

    Args:
        filter_id (int): ID of JIRA filter to query_url
    Returns:
        list[JIRA.Issue]: List of issue objects from query
    """
    url = query_url(filter_id)

    fetch_message = "fetch_query_results: FETCH {} as {}".format(url, settings.JIRA_AUTH[0])
    logger.info(fetch_message)

    results = requests.get(url, auth=settings.JIRA_AUTH, verify=settings.JIRA_SSL_VERIFY).json()

    if 'errorMessages' in results.keys():
        logger.warning('{} produced errors: {}'.format(fetch_message, results['errorMessages']))

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
    logger = logging.getLogger("dashboard.services.jira.summarize_results")
    summary = {
        'incomplete': 0,
        'complete': 0,
        'pct_complete': 0,
        'total': 0,
        'errors': [],
    }
    summary['errors'] = results.get('errorMessages', [])
    if summary['errors']:
        #  Short circuit
        return summary

    if results.get('total', 0) == 0:
        # Short circuit
        return summary

    total = results['total']
    for issue in results['issues']:
        if issue['fields']['status']['name'].strip() in settings.JIRA_DONE:
            logger.debug("COMPLETE: {} <{}> in <{}>".format(issue['key'], issue['fields']['status']['name'], settings.JIRA_DONE))
            summary['complete'] += 1
        else:
            logger.debug("INCOMPLETE: {} <{}> not in <{}>".format(issue['key'], issue['fields']['status']['name'], settings.JIRA_DONE))
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
    try:
        int(filter_id)
    except ValueError:
        return {}
    return summarize_results(fetch_query_results(filter_id))
