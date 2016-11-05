from better.lib import Forecaster


def throughput_history(summaries):
    history = []
    for i in range(len(summaries)-1):
        history.append(summaries[i+1].complete - summaries[i].complete)
    return history


def forecast(throughputs, backlog_size, num_simulations=10000, seed=None):
    results = Forecaster().forecast(throughputs, backlog_size, num_simulations, seed)
    return [results.percentile(50), results.percentile(80), results.percentile(90)]
