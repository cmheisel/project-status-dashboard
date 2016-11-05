import logging

from better.lib import Forecaster

from .summaries import for_date_range

logger = logging.getLogger('dashboard.services.pedictions')


def throughput_history(summaries):
    """Calculates the change in completion for a list of summaries.
    Args:
        summaries (List[ProjectSummary]): List of project summaries to analyze
    Returns:
        List[int]: The change in number of items complete between each set of two summaries provided.
    """
    history = []
    for i in range(len(summaries)-1):
        throughput = summaries[i+1].complete - summaries[i].complete
        if throughput < 0: throughput = 0
        history.append(throughput)
    return history


def forecast(throughputs, backlog_size, num_simulations=10000, seed=None):
    """Monte Carlo forecast given the provided backlog and throughput histories.
    Args:
        throughputs (List[int]): Number of items completed per period
        backlog_size (int): How many items remain incomplete
        num_simulations (int: 10000): How many simulations should be run
        seed (None): Provide a seed for the random number generator
    Returns:
        List[int]: The 50th, 80th, and 90th percentile # of periods remaining in the project
    """
    results = Forecaster().forecast(throughputs, backlog_size, num_simulations=num_simulations, seed=seed)
    return [results.percentile(50), results.percentile(80), results.percentile(90)]


def for_project(filter_id, backlog_size, start_date):
    """Forecast a project
    Args:
        filter_id (int): The filter_id for the project in question.
        backlog_size (int): How many items remain incomplete
        start_date (Date): How far back should we look for team history to simulate with
    Returns:
        List[int]: The 50th, 80th, and 90th percentile # of periods remaining in the project
    """
    logger.debug("for_project: {}, {}, {}".format(filter_id, backlog_size, start_date))
    summaries = for_date_range(filter_id, start_date)
    logger.debug("for_Project: {} -- summaries {}".format(filter_id, [s.complete for s in summaries]))
    throughputs = throughput_history(summaries)
    logger.debug("for_project: {} -- throughputs: {}".format(filter_id, throughputs))
    return forecast(throughputs, backlog_size)
