import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pickle
import shutil
from tabulate import tabulate


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)


class Logger:
    """
    The Logger class is used printing statistics, saving/loading models and plotting.

    Parameters
    ----------
    prefix_path : Path
        The variable is used for specifying the root of the path where the plots and models are saved.
    mode: str
        The variable specifies in which mode we are currently running. (shooting | defense | normal)
    quiet: boolean
        This variable is used to specify whether the prints are hidden or not.
    """

    def __init__(self, prefix_path, mode, quiet=False) -> None:
        self.prefix_path = Path(prefix_path)
        self.reward_prefix_path = self.prefix_path.joinpath('rewards')
        self.prefix_path.mkdir(exist_ok=True)
        self.reward_prefix_path.mkdir(exist_ok=True)
        self.quiet = quiet

        if not self.quiet:
            print(f"Running in mode: {mode}")

    def save_model(self, model, filename):
        savepath = self.prefix_path.joinpath(filename).with_suffix('.pkl')
        with open(savepath, 'wb') as outp:
            pickle.dump(model, outp, pickle.HIGHEST_PROTOCOL)

    def print_episode_info(self, game_outcome, episode_counter, step, total_reward, epsilon=0):
        if not self.quiet:
            padding = 8 if game_outcome == 0 else 0
            print(
                '{} {:>4}: Done after {:>3} steps. \tReward: {:<15}Epsilon: {:<15}'.format(
                    " " * padding, episode_counter, step + 1, round(total_reward, 2), round(epsilon, 2)))

    def print_stats(self, rew_stats, touch_stats, won_stats, lost_stats):
        if not self.quiet:
            print(tabulate([['Mean reward', np.around(np.mean(rew_stats), 3)],
                            ['Mean touch', np.around(np.mean(list(touch_stats.values())), 3)],
                            ['Mean won', np.around(np.mean(list(won_stats.values())), 3)],
                            ['Mean lost', np.around(np.mean(list(lost_stats.values())), 3)]], tablefmt='grid'))

    def load_model(self, filename):
        load_path = self.prefix_path.joinpath(filename).with_suffix('.pkl')
        with open(load_path, 'rb') as inp:
            return pickle.load(inp)

    def hist(self, data, title, filename=None, show=True):
        plt.figure()
        plt.hist(data, density=True)
        plt.title(title)

        plt.savefig(self.reward_prefix_path.joinpath(filename).with_suffix('.pdf'))
        if show:
            plt.show()
        plt.close()

    def plot_running_mean(self, data, title, filename=None, show=True):
        plt.figure()
        data_np = np.asarray(data)
        mean = running_mean(data_np, 50)
        plt.plot(mean)
        plt.title(title)

        plt.savefig(self.prefix_path.joinpath(filename).with_suffix('.pdf'))
        if show:
            plt.show()
        plt.close()

    def clean_rew_dir(self):
        shutil.rmtree(self.reward_prefix_path, ignore_errors=True)
        self.reward_prefix_path.mkdir(exist_ok=True)
