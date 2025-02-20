"""Test FCN."""
import numpy as np
from keras_fcn import FCN
from tensorflow.keras import backend as K


def is_same_shape(shape, expected_shape, data_format=None):
    """Test helper."""
    if data_format is None:
        data_format = K.image_data_format()
    if data_format == 'channels_first':
        expected_shape = (expected_shape[0],
                          expected_shape[3],
                          expected_shape[1],
                          expected_shape[2])
    return shape == expected_shape


def test_fcn_vgg16_shape():
    """Test output shape."""
    if K.image_data_format() == 'channels_first':
        input_shape = (3, 500, 500)
    else:
        input_shape = (500, 500, 3)
    fcn_vgg16 = FCN(input_shape=input_shape, classes=21)

    layers = [l.name for l in fcn_vgg16.layers]
    assert 'upscore_feat1' in layers
    assert 'upscore_feat2' in layers
    assert 'upscore_feat3' in layers

    for l in fcn_vgg16.layers:
        if l.name == 'block1_pool':
            test_shape = (None, 250, 250, 64)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'block2_pool':
            test_shape = (None, 125, 125, 128)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'block3_pool':
            test_shape = (None, 63, 63, 256)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'block4_pool':
            test_shape = (None, 32, 32, 512)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'block5_pool':
            test_shape = (None, 16, 16, 512)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'dropout_2':
            test_shape = (None, 16, 16, 4096)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'upscore_feat1':
            test_shape = (None, 32, 32, 21)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'upscore_feat2':
            test_shape = (None, 63, 63, 21)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'upscore_feat3':
            test_shape = (None, 500, 500, 21)
            assert is_same_shape(l.output_shape, test_shape)
        elif l.name == 'score':
            test_shape = (None, 500, 500, 21)
            assert is_same_shape(l.output_shape, test_shape)
    assert is_same_shape(fcn_vgg16.output_shape, (None, 500, 500, 21))

    input_shape = (1366, 768, 3)
    fcn_vgg16 = FCN(input_shape=input_shape, classes=21)
    assert is_same_shape(fcn_vgg16.output_shape, (None, 1366, 768, 21))


def test_fcn_vgg16_correctness():
    """Test output not NaN."""
    if K.image_data_format() == 'channels_first':
        input_shape = (3, 500, 500)
        x = np.random.rand(1, 3, 500, 500)
        y = np.random.randint(21, size=(1, 500, 500))
        y = np.eye(21)[y]
        y = np.transpose(y, (0, 3, 1, 2))
    else:
        input_shape = (500, 500, 3)
        x = np.random.rand(1, 500, 500, 3)
        y = np.random.randint(21, size=(1, 500, 500))
        y = np.eye(21)[y]
    fcn_vgg16 = FCN(classes=21, input_shape=input_shape)
    fcn_vgg16.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
    fcn_vgg16.fit(x, y, batch_size=1, epochs=1)
    loss = fcn_vgg16.evaluate(x, y, batch_size=1)
    assert not np.any(np.isinf(loss))
    assert not np.any(np.isnan(loss))
    y_pred = fcn_vgg16.predict(x, batch_size=1)
    assert not np.any(np.isinf(y_pred))
    assert not np.any(np.isnan(y_pred))
