#TF and huggingface pipeline imports
import tensorflow as tf;
from transformers import pipeline;

#Test tensorflow (from https://www.tensorflow.org/install/pip#windows-native)
print(tf.reduce_sum(tf.random.normal([1000, 1000])))
#Expected output: A tensorflow tensor (e.g. tf.Tensor(650.9678, shape=(), dtype=float32))

#Check tensorflow recognises GPU (from https://www.tensorflow.org/install/pip#windows-native)
print(tf.config.list_physical_devices('GPU'))
#Expected output: A list containing a GPU (e.g. [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')])

#Test huggingface pipeline (from https://huggingface.co/docs/transformers/installation)
print(pipeline('sentiment-analysis')('we love you'))
#Expected output: [{'label': 'POSITIVE', 'score': 0.9998704195022583}]