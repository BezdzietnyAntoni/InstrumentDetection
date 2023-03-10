"""
Module include function used for parametrization raw audio waveform and 
save them in pickle form.
"""

import pickle
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt



def display_mfccs_params(mfccs, d1_mfccs, d2_mfccs):
    """
    Display mfccs parameters

    Args:
        mfccs (np.ndarray): mfccs params
        d1_mfccs (np.ndarray): mfccs delta params
        d2_mfccs (np.ndarray): mfccs second delta params
    """
    fig, ax = plt.subplots(nrows=3, sharex=True, sharey=True)
    fig.set_size_inches((10,6))
    img1 = librosa.display.specshow(mfccs, ax=ax[0], x_axis='time')
    ax[0].set(title='MFCC')
    ax[0].set_ylabel('Index')
    ax[0].set_yticks(range(0, mfccs.shape[0], 2))
    ax[0].label_outer()
    img2 = librosa.display.specshow(d1_mfccs, ax=ax[1], x_axis='time')
    ax[1].set(title=r'MFCC-$\Delta$')
    ax[1].set_ylabel('Index')
    ax[1].set_yticks(range(0, d1_mfccs.shape[0], 2))
    ax[1].label_outer()
    img3 = librosa.display.specshow(d2_mfccs, ax=ax[2], x_axis='time')
    ax[2].set(title=r'MFCC-$\Delta^2$')
    ax[2].set_ylabel('Index')
    ax[2].set_yticks(range(0, d2_mfccs.shape[0], 2))
    fig.colorbar(img1, ax=[ax[0]])
    fig.colorbar(img2, ax=[ax[1]])
    fig.colorbar(img3, ax=[ax[2]])


def mfccs_parametrization(signal : np.ndarray, fs : int = 22050 , n_coef : int = 14):
    """
    Return mfccs and delta mfccs params

    Args:
        signal (np.ndarray): Parametrization signal
        fs (int): Sampling rate
        n_coef (int): Number of coef
    Return:
        param (list): [mfccs, d1_mfccs, d2_mfccs]
    """
    mfccs    = librosa.feature.mfcc(signal, sr = fs, n_mfcc = n_coef)
    d1_mfccs = librosa.feature.delta(mfccs, order=1)
    d2_mfccs = librosa.feature.delta(mfccs, order=2)

    return [mfccs, d1_mfccs, d2_mfccs]


def mfccs_parametrization_dataset(df : pd.DataFrame, data_path : str, n_coef : int = 14):
    """
    Return mfccs and delta mfccs for all set in dataset

    Args:
        df (pd.DataFrame): DataFrame with field `FileName`
        data_path (str): Path to data
        n_coef (int): Number of coef

    Returns:
        extracted_mfccs (list): List of `dict` with keys 
        (`file_name`, `class`, `mfccs`, `d1_mfccs`, `d2_mfccs`)
    """

    extracted_mfccs = []

    for index_num,row in tqdm(df.iterrows()):
        path = data_path + row['FileName']
        signal, sr = librosa.load(path)
        mfccs, d1_mfccs, d2_mfccs = mfccs_parametrization(signal, sr, n_coef)
        extracted_mfccs.append({'file_name' : row['FileName'], 
                                'class'     : row['Class'], 
                                'mfccs'     : mfccs,
                                'd1_mfccs'  : d1_mfccs,
                                'd2_mfccs'  : d2_mfccs})

    return extracted_mfccs


def mfccs_features(mfccs_param : list):
    """
    Get features (statistics [`median`, `mean`, `std`]) from mfccs parameters

    Args:
        mfccs_param (list): Parametrization signal

    Returns:
        features (np.ndarray): Array of features based on basic statistics
    """

    field = ['mfccs', 'd1_mfccs', 'd2_mfccs']
    statistics = [np.median, np.mean, np.std]
    n_statistics =  len(statistics) * len(field) * len(mfccs_param[0]['mfccs'])
    
    features = np.zeros((len(mfccs_param), n_statistics))

    for i in range(len(mfccs_param)):
        features[i] = np.concatenate([s(mfccs_param[i][f], axis = 1) for s in statistics for f in field])

    return features


def get_target(mfccs_param : list):
    """
    Get target for mfccs param

    Args:
        mfccs_param (list): Parameters in standard mfccs 

    Returns:
        target(list): List of target
    """
    return [row['class'] for row in mfccs_param]


def get_file(mfccs_param : list):
    """
    Get file_name for mfccs param

    Args:
        mfccs_param (list): Parameters in standard mfccs 

    Returns:
        target(list): List of file_name
    """
    return [row['file_name'] for row in mfccs_param]


def read_feature(mfccs_feature_path : str):
    """
    Read pickle music features

    Args:
        mfccs_feature_path (str): Path to pickle mfccs feature file

    Returns:
        mfccs (dict): Unpickle mfccs feature 
    """

    with open(mfccs_feature_path, 'rb') as f_mfccs_feature:
        mfccs_feature = pickle.load(f_mfccs_feature)  
    
    return mfccs_feature