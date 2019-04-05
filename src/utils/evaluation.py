from __future__ import division

import numpy as np


def auto_correlation_time(x, s, mu, var):
    b, t, d = x.shape
    act_ = np.zeros([d])
    for i in range(0, b):
        y = x[i] - mu
        p, n = y[:-s], y[s:]
        act_ += np.mean(p * n, axis=0) / var
    act_ = act_ / b
    return act_


def effective_sample_size(x, mu, var):
    """
    Calculate the effective sample size of sequence generated by MCMC.
    :param x:
    :param mu: mean of the variable
    :param var: variance of the variable
    :param logger: logg
    :return: effective sample size of the sequence
    Make sure that `mu` and `var` are correct!
    """
    # batch size, step, dimension
    b, t, d = x.shape
    ess_ = np.ones([d])
    for s in range(1, t):
        p = auto_correlation_time(x, s, mu, var)
        if np.sum(p > 0.05) == 0:
            break
        else:
            for j in range(0, d):
                if p[j] > 0.05:
                    ess_[j] += 2.0 * p[j] * (1.0 - float(s) / t)

    return t / ess_


def acceptance_rate(z):
    cnt = z.shape[0] * (z.shape[1] - 1)
    for i in range(0, z.shape[0]):
        for j in range(1, z.shape[1]):
            if np.min(np.equal(z[i, j - 1], z[i, j])):
                cnt -= 1
    return cnt / float(z.shape[0] * (z.shape[1] - 1))


def mean_jump_distance(z):
    d = 0
    cnt = z.shape[0] * (z.shape[1] - 1)
    for i in range(0, z.shape[0]):
        for j in range(1, z.shape[1]):
            d += np.linalg.norm(z[i, j - 1] - z[i, j])
    return d / cnt


def gelman_rubin_diagnostic(x, mu=None):
    m, n = x.shape[0], x.shape[1]
    theta = np.mean(x, axis=1)
    sigma = np.var(x, axis=1)
    # theta_m = np.mean(theta, axis=0)
    theta_m = mu if mu is not None else np.mean(theta, axis=0)
    b = float(n) / float(m-1) * np.sum((theta - theta_m) ** 2)
    w = 1. / (float(m) * np.sum(sigma, axis=0) + 1e-5)
    v = float(n-1) / float(n) * w + float(m+1) / float(m * n) * b
    r_hat = np.sqrt(v / w)
    return r_hat


def autocor_ESS(A):
    A = A * (A > 0.05)
    return 1. / (1. + 2 * np.sum(A[1:]))


def autocovariance(X, tau=0):
  dT, dN, dX = np.shape(X)
  s = 0.
  for t in range(dT - tau):
    x1 = X[t, :, :]
    x2 = X[t+tau, :, :]

    s += np.sum(x1 * x2) / dN

  return s / (dT - tau)


def acl_spectrum(X, scale):
    n = X.shape[0]
    return np.array([autocovariance(X / scale, tau=t) for t in range(n-1)])
