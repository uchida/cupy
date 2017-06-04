import unittest

import numpy

import cupy
from cupy import cuda
from cupy import testing


@testing.gpu
class TestTrace(unittest.TestCase):

    _multiprocess_can_split_ = True

    @testing.for_all_dtypes()
    @testing.numpy_cupy_allclose()
    def test_trace(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4, 5), xp, dtype)
        return a.trace(1, 3, 2)

    @testing.for_all_dtypes()
    @testing.numpy_cupy_allclose()
    def test_external_trace(self, xp, dtype):
        a = testing.shaped_arange((2, 3, 4, 5), xp, dtype)
        return xp.trace(a, 1, 3, 2)


@testing.parameterize(*testing.product({
    'shape': [(1,), (2,)],
    'ord': [-numpy.Inf, -2, -1, 0, 1, 2, 3, numpy.Inf],
    'axis': [0, None],
    'keepdims': [True, False],
}) + testing.product({
    'shape': [(1, 2), (2, 2)],
    'ord': [-numpy.Inf, -1, 1, numpy.Inf, 'fro'],
    'axis': [(0, 1), None],
    'keepdims': [True, False],
}) + testing.product({
    'shape': [(2, 2, 2)],
    'ord': [-numpy.Inf, -2, -1, 0, 1, 2, 3, numpy.Inf],
    'axis': [0, 1, 2],
    'keepdims': [True, False],
}) + testing.product({
    'shape': [(2, 2, 2)],
    'ord': [-numpy.Inf, -1, 1, numpy.Inf, 'fro'],
    'axis': [(0, 1), (0, 2), (1, 2)],
    'keepdims': [True, False],
})
)
@testing.gpu
@testing.with_requires('numpy>=1.11.2')  # The old version dtype is strange
class TestNorm(unittest.TestCase):

    _multiprocess_can_split_ = True

    @testing.for_all_dtypes()
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_norm(self, xp, dtype):
        a = testing.shaped_arange(self.shape, xp, dtype)
        with testing.NumpyError(divide='ignore'):
            return xp.linalg.norm(a, self.ord, self.axis, self.keepdims)


@testing.parameterize(*testing.product({
    'array': [
        [[1, 2], [3, 4]],
        [[1, 2], [1, 2]],
        [[0, 0], [0, 0]],
        [1, 2],
        [0, 1],
        [0, 0],
    ],
    'tol': [None, 1]
}))
@unittest.skipUnless(
    cuda.cusolver_enabled, 'Only cusolver in CUDA 8.0 is supported')
@testing.gpu
class TestMatrixRank(unittest.TestCase):

    _multiprocess_can_split_ = True

    @testing.for_all_dtypes(no_float16=True)
    @testing.numpy_cupy_array_equal()
    def test_matrix_rank(self, xp, dtype):
        a = xp.array(self.array, dtype=dtype)
        y = xp.linalg.matrix_rank(a, tol=self.tol)
        if xp is cupy:
            # Note numpy returns int
            self.assertIsInstance(y, cupy.ndarray)
            self.assertEqual(y.dtype, 'l')
            self.assertEqual(y.shape, ())
        return xp.array(y)


class TestSlogdet(unittest.TestCase):

    _multiprocess_can_split_ = True

    @testing.for_float_dtypes(no_float16=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_slogdet(self, xp, dtype):
        a = testing.shaped_arange((2, 2), xp, dtype) + 1
        sign, logdet = xp.linalg.slogdet(a)
        return xp.array([sign, logdet], dtype)

    @testing.for_float_dtypes(no_float16=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_slogdet_3(self, xp, dtype):
        a = testing.shaped_arange((2, 2, 2), xp, dtype) + 1
        sign, logdet = xp.linalg.slogdet(a)
        return xp.array([sign, logdet], dtype)

    @testing.for_float_dtypes(no_float16=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_slogdet_4(self, xp, dtype):
        a = testing.shaped_arange((2, 2, 2, 2), xp, dtype) + 1
        sign, logdet = xp.linalg.slogdet(a)
        return xp.array([sign, logdet], dtype)

    @testing.for_float_dtypes(no_float16=True)
    @testing.numpy_cupy_allclose(rtol=1e-3, atol=1e-4)
    def test_slogdet_fail(self, xp, dtype):
        a = xp.zeros((3, 3), dtype)
        sign, logdet = xp.linalg.slogdet(a)
        return xp.array([sign, logdet], dtype)

    @testing.numpy_cupy_raises(numpy.linalg.LinAlgError)
    def test_slogdet_one_dim(self, xp, dtype):
        a = testing.shaped_arange((2,), xp, dtype)
        xp.linalg.slogdet(a)

