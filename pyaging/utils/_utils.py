import os
import torch
import ntpath
import os
from urllib.request import urlretrieve
from functools import wraps
from ..logger import LoggerManager, main_tqdm


#def progress(message: str, indent_level: int = 1):
#    """
#    Decorator to log the progress of a function.
#
#    Parameters:
#    - message (str): Description of the function's purpose or current step.
#    - indent_level (int): Indentation level for the log message.
#
#    Returns:
#    - Function: A wrapped function with added logging for progress tracking.
#    """
#
#    def decorator(func):
#        @wraps(func)
#        def wrapper(*args, **kwargs):
#            logger = args[-1]  # Assumes logger is the last argument
#            logger.start_progress(f"{message} started", indent_level=indent_level)
#            result = func(*args, **kwargs)
#            logger.finish_progress(f"{message} finished", indent_level=indent_level)
#            return result
#
#        return wrapper
#
#    return decorator

def progress(message: str):
    """
    Decorator to log the progress of a function.

    Parameters:
    - message (str): Description of the function's purpose or current step.
    - indent_level (int): Indentation level for the log message.

    Returns:
    - Function: A wrapped function with added logging for progress tracking.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract indent_level from kwargs, default to 1 if not provided
            indent_level = kwargs.pop('indent_level', 1)

            logger = args[-1]  # Assumes logger is the last positional argument
            logger.start_progress(f"{message} started", indent_level=indent_level)
            result = func(*args, **kwargs)
            logger.finish_progress(f"{message} finished", indent_level=indent_level)
            return result

        return wrapper

    return decorator

    

@progress("Load all clock metadata")
def load_clock_metadata(logger, indent_level: int = 1) -> dict:
    """
    Loads the metadata of all available clocks.

    Args:
    - logger: Logger object for logging messages.

    Returns:
    - pandas DataFrame with genome metadata.
    """
    file_id = '1w4aR_Z6fY4HAWFk1seYf6ELbZYb3GSmZ'
    url = f"https://drive.google.com/uc?id={file_id}"
    dir="./pyaging_data"
    file_path =  'all_clock_metadata.pt'
    file_path = os.path.join(dir, file_path)
    
    if os.path.exists(file_path):
        logger.info(f'Data found in {file_path}', indent_level=2)
    else:
        if not os.path.exists(dir):
            os.mkdir("pyaging_data")
        logger.info(f"Downloading data to {file_path}", indent_level=2)
        logger.indent_level = 2
        urlretrieve(url, file_path, reporthook=logger.request_report_hook)

    # Read data
    all_clock_metadata = torch.load("./pyaging_data/all_clock_metadata.pt")
    return all_clock_metadata


def find_clock_by_doi(search_doi: str) -> None:
    """
    Loads all clock metadata and searches for the doi.

    Parameters:
    - search_doi (str): The DOI string to search for within the .pt files.

    Returns:
    - list: Filenames of .pt files containing the specified DOI, or an empty list if not found.
    """
    logger = LoggerManager.gen_logger("find_clock_by_doi")
    logger.first_info("Starting find_clock_by_doi function")

    # Load all metadata
    all_clock_metadata = load_clock_metadata(logger)

    # Message to indicate the start of the search process
    message = "Searching for clock based on DOI"
    logger.start_progress(f"{message} started")
    matching_clocks = []

    # Loop through clocks in the dictionary
    for clock_name in main_tqdm(list(all_clock_metadata.keys()), indent_level=2):
        clock_dict = all_clock_metadata[clock_name]
        if "doi" in clock_dict and clock_dict["doi"] == search_doi:
            matching_clocks.append(clock_name)

    # Logging the results
    if matching_clocks:
        logger.info(
            f"Clocks with DOI {search_doi}: {', '.join(matching_clocks)}", indent_level=2
        )
    else:
        logger.warning(f"No files found with DOI {search_doi}", indent_level=2)
    logger.finish_progress(f"{message} finished")

    logger.done()


def cite_clock(clock_name: str) -> None:
    """
    Retrieves the citation for a specific clock name.

    Parameters:
    - clock_name (str): The name of the clock for which the citation is requested.

    Returns:
    - str: Citation string for the specified clock, or an empty string if not found.
    """
    logger = LoggerManager.gen_logger("cite_clock")
    logger.first_info("Starting cite_clock function")

    clock_name = clock_name.lower()

    # Load all metadata
    all_clock_metadata = load_clock_metadata(logger)

    message = f"Searching for citation of clock {clock_name}"
    logger.start_progress(f"{message} started")
    citation = ""

    if clock_name in list(all_clock_metadata.keys()):
        clock_dict = all_clock_metadata[clock_name]
        if "citation" in clock_dict:
            citation = clock_dict["citation"]
            logger.info(f"Citation for {clock_name}:", indent_level=2)
            logger.info(citation, indent_level=2)
        else:
            logger.warning(
                f"Citation not found in {clock_name}", indent_level=2
            )
    else:
        logger.warning(
            f"{clock_name} is not currently available in pyaging", indent_level=2
        )

    logger.finish_progress(f"{message} finished")
    logger.done()
    

def show_all_clocks() -> None:
    """
    Calculate the predicted biological age based on methylation data using a specified model.

    This function applies a pre-trained machine learning model to a given dataset to estimate the
    biological age of the samples. The input data should be preprocessed appropriately to match the
    format expected by the model. The function returns a list of predicted ages corresponding to each sample.

    Parameters
    ----------
    model : object
        A pre-trained machine learning model. This model should implement the `predict` method,
        such as models from scikit-learn or a custom model adhering to this interface.
        
    data : array-like, shape (n_samples, n_features)
        Methylation data for the samples. Each row corresponds to a sample, and each column
        corresponds to a specific methylation site. The data should be preprocessed and normalized
        as required by the `model`.

    Returns
    -------
    predicted_ages : ndarray, shape (n_samples,)
        An array containing the predicted biological ages for each sample. The predictions are
        generated by the `model` based on the input `data`.

    Raises
    ------
    ValueError
        If the input data is not properly formatted or if the model is not compatible.

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestRegressor
    >>> model = RandomForestRegressor()
    >>> data = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    >>> calculate_age_prediction(model, data)
    array([30.5, 35.7])

    Notes
    -----
    The model should be trained on a dataset with a similar distribution to the `data` provided
    for prediction. The accuracy of the predictions highly depends on the model's training and
    the quality of the input data.

    See Also
    --------
    sklearn.ensemble.RandomForestRegressor : A random forest regressor model from scikit-learn.
    preprocess_data : Function for preprocessing data to the required format.

    References
    ----------
    .. [1] Smith, A. B., et al. (2020). "Predicting Age with Methylation Data: A Machine Learning
           Approach." Journal of Aging Research, vol. 2020, Article ID 123456, 12 pages.
           https://doi.org/10.1155/2020/123456

    """
    logger = LoggerManager.gen_logger("show_all_clocks")
    logger.first_info("Starting show_all_clocks function")

    # Load all metadata
    all_clock_metadata = load_clock_metadata(logger)

    # Message to indicate the start of the search process
    message = "Showing all available clock names"
    logger.start_progress(f"{message} started")
    for clock_name in list(all_clock_metadata.keys()):
        logger.info(clock_name, indent_level=2)
    logger.finish_progress(f"{message} finished")

    logger.done()
    

def get_clock_metadata(clock_name: str) -> None:
    """
    Loads all clock metadata and prints the metadata for .
    
    Parameters:
    - clock_name (str): The name of the clock for which the metadata is requested.

    Returns:
    - str: Citation metadata for the specified clock, or an empty string if not found.
    """
    logger = LoggerManager.gen_logger("get_clock_metadata")
    logger.first_info("Starting get_clock_metadata function")

    # Load all metadata
    all_clock_metadata = load_clock_metadata(logger)

    # Lowercase clock name
    clock_name = clock_name.lower()
    clock_dict = all_clock_metadata[clock_name]

    # Message to indicate the start of the search process
    message = f"Showing {clock_name} metadata"
    logger.start_progress(f"{message} started")
    for key in list(clock_dict.keys()):
        logger.info(f"{key}: {clock_dict[key]}", indent_level=2)
    logger.finish_progress(f"{message} finished")

    logger.done()
