from sklearn.exceptions import NotFittedError
from abc import ABCMeta, abstractmethod
from scipy.sparse import csr_matrix
import warnings
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, roc_auc_score
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.externals import six


# Warnings


class AlphaZeroWarning(Warning):
    pass


class NotImplementedYet(Warning):
    pass


# Base Naive Bayes classifier class


class BaseNB(six.with_metaclass(ABCMeta, BaseEstimator)):

    _estimator_type = "classifier"

    def __init__(self):
        self.is_fitted = False
        self.classes_ = None
        self.class_count_ = None

    # Properties

    @property
    def complement_class_count_(self):
        '''

        Complement class count, i.e. number of occurrences of all the samples with
        all the classes except the given class c

        '''
        from bayes.utils import get_complement_matrix
        size = len(self.class_count_)
        return self.class_count_.dot(get_complement_matrix(size))

    @property
    def complement_class_log_proba_(self):
        '''

        Complement class probability, i.e. logprob of occurrence of a sample, which
        does not belong to the given class c

        '''
        all_samples_count = np.float64(np.sum(self.class_count_))
        return np.log(self.complement_class_count_ / all_samples_count)

    @property
    def class_log_proba_(self):
        '''
        Log probability of class occurrence
        '''
        all_samples_count = np.float64(np.sum(self.class_count_))
        return np.log(self.class_count_ / all_samples_count)


    # Fitting model

    def fit(self, X, y):
        '''

        Fit model to given training set

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.
        y : array-like, shape (n_samples,)
            Target values.
        Returns
        -------
        self : Naive Bayes estimator object
            Returns self.
        '''
        self._reset()
        self._partial_fit(X, y)
        return self

    @abstractmethod
    def partial_fit(self, X, y, classes=None):
        """
        Incremental fit on a batch of samples.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.
        classes : array-like, shape = [n_classes], optional (default=None)
            List of all the classes that can possibly appear in the y vector.
            Must be provided at the first call to partial_fit, can be omitted
            in subsequent calls.

        Returns
        -------
        self : object
             Returns self.
        """

    @abstractmethod
    def _partial_fit(self, X, y, classes=None, first_partial_fit=None):
        ''''''

    @abstractmethod
    def predict(self, X):
        """
        Perform classification on an array of test vectors X.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Unseen samples vector
        Returns
        -------
        C : array, shape = [n_samples]
            Predicted target values for X

        """

    def _update_complement_features(self, X, y_one_hot):
        '''

        Compute complement features counts

        Parameters
        ----------
        X: numpy array (n_samples, n_features)
            Matrix of input samples
        y_one_hot: numpy array (n_samples, n_classes)
            Binary matrix encoding input
        '''
        # FIXME: complement_features nomenclature is incoherent
        if not self.is_fitted:
            self.complement_features = X.T.dot(np.logical_not(y_one_hot))
        else:
            self.complement_features += X.T.dot(np.logical_not(y_one_hot))

    def _update_features(self, X, y_one_hot):
        '''

        Compute features counts

        Parameters
        ----------
        X: numpy array (n_samples, n_features)
            Matrix of input samples
        y_one_hot: numpy array (n_samples, n_classes)
            Binary matrix encoding input
        '''
        if not self.is_fitted:
            self.features_ = X.T.dot(y_one_hot)
        else:
            self.features_ += X.T.dot(y_one_hot)



    @abstractmethod
    def predict_log_proba(self, X):
        """
        Return log-probability estimates for the test vector X.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
        Returns
        -------
        C : array-like, shape = [n_samples, n_classes]
            Returns the log-probability of the samples for each class in
            the model. The columns correspond to the classes in sorted
            order, as they appear in the attribute `classes_`.
        """

    @abstractmethod
    def _reset(self):
        ''''''

    def predict_proba(self, X):
        """
        Return probability estimates for the test vector X.
        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
        Returns
        -------
        C : array-like, shape = [n_samples, n_classes]
            Returns the probability of the samples for each class in
            the model. The columns correspond to the classes in sorted
            order, as they appear in the attribute `classes_`.
        """
        # TODO: Handle float exponent error
        return np.exp(self.predict_log_proba(X))

    # Scores

    def accuracy_score(self, X, y):
        '''

        Return acuracy score

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.

        Returns
        -------
        accuracy_score: float
            Accuracy on the given test set

        '''
        self._check_is_fitted()
        return accuracy_score(y, self.predict(X))

    # def f1_score(self, X, y):
    #     self._check_is_fitted()
    #     return f1_score(y, self.predict(X))
    #
    # def precision_score(self, X, y):
    #     self._check_is_fitted()
    #     return precision_score(y, self.predict(X))
    #
    # def recall_score(self, X, y):
    #     self._check_is_fitted()
    #     return recall_score(y, self.predict(X))
    #
    # def roc_auc_score(self, X, y):
    #     self._check_is_fitted()
    #     return roc_auc_score(y, self.predict(X))

    # Checking params & states

    def _check_is_fitted(self):
        if not self.is_fitted:
            raise NotFittedError

    def _check_alpha_param(self):
        if self.alpha == 0.0:
            warnings.warn('Alpha sholud not be zero. It may cause division by zero', AlphaZeroWarning)

    def _not_implemented_yet(self, message):
        warnings.warn(NotImplementedYet(message))

    # def safe_mult(self, input_array, internal_array):
    #     if isinstance(input_array, csr_matrix):
    #         input_array = input_array.toarray()
    #     return input_array * internal_array

    def safe_matmult(self, input_array, internal_array):
        if isinstance(input_array, csr_matrix):
            input_array = input_array.toarray()
        return input_array.dot(internal_array.T)
