# copyright (c) 2019 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

import paddle
import paddle.fluid as fluid
from paddle.fluid.param_attr import ParamAttr

__all__ = [
    "ResNet", "ResNet18_vd", "ResNet34_vd", "ResNet50_vd", "ResNet101_vd",
    "ResNet152_vd", "ResNet200_vd"
]


class ResNet():
    def __init__(self, layers=50, is_3x3=False):
        self.layers = layers
        self.is_3x3 = is_3x3

    def net(self, input, class_dim=1000, data_format="NCHW"):
        is_3x3 = self.is_3x3
        layers = self.layers
        supported_layers = [18, 34, 50, 101, 152, 200]
        assert layers in supported_layers, \
            "supported layers are {} but input layer is {}".format(supported_layers, layers)

        if layers == 18:
            depth = [2, 2, 2, 2]
        elif layers == 34 or layers == 50:
            depth = [3, 4, 6, 3]
        elif layers == 101:
            depth = [3, 4, 23, 3]
        elif layers == 152:
            depth = [3, 8, 36, 3]
        elif layers == 200:
            depth = [3, 12, 48, 3]
        num_filters = [64, 128, 256, 512]
        if is_3x3 == False:
            conv = self.conv_bn_layer(
                input=input,
                num_filters=64,
                filter_size=7,
                stride=2,
                act='relu',
                data_format=data_format)
        else:
            conv = self.conv_bn_layer(
                input=input,
                num_filters=32,
                filter_size=3,
                stride=2,
                act='relu',
                name='conv1_1',
                data_format=data_format)
            conv = self.conv_bn_layer(
                input=conv,
                num_filters=32,
                filter_size=3,
                stride=1,
                act='relu',
                name='conv1_2',
                data_format=data_format)
            conv = self.conv_bn_layer(
                input=conv,
                num_filters=64,
                filter_size=3,
                stride=1,
                act='relu',
                name='conv1_3',
                data_format=data_format)

        conv = fluid.layers.pool2d(
            input=conv,
            pool_size=3,
            pool_stride=2,
            pool_padding=1,
            pool_type='max',
            data_format=data_format)

        if layers >= 50:
            for block in range(len(depth)):
                for i in range(depth[block]):
                    if layers in [101, 152, 200] and block == 2:
                        if i == 0:
                            conv_name = "res" + str(block + 2) + "a"
                        else:
                            conv_name = "res" + str(block + 2) + "b" + str(i)
                    else:
                        conv_name = "res" + str(block + 2) + chr(97 + i)
                    conv = self.bottleneck_block(
                        input=conv,
                        num_filters=num_filters[block],
                        stride=2 if i == 0 and block != 0 else 1,
                        if_first=block == i == 0,
                        name=conv_name,
                        data_format=data_format)
        else:
            for block in range(len(depth)):
                for i in range(depth[block]):
                    conv_name = "res" + str(block + 2) + chr(97 + i)
                    conv = self.basic_block(
                        input=conv,
                        num_filters=num_filters[block],
                        stride=2 if i == 0 and block != 0 else 1,
                        if_first=block == i == 0,
                        name=conv_name,
                        data_format=data_format)

        pool = fluid.layers.pool2d(
            input=conv,
            pool_type='avg',
            global_pooling=True,
            data_format=data_format)
        pool_channel = pool.shape[1] if data_format == "NCHW" else pool.shape[
            -1]
        stdv = 1.0 / math.sqrt(pool_channel * 1.0)

        out = fluid.layers.fc(
            input=pool,
            size=class_dim,
            param_attr=fluid.param_attr.ParamAttr(
                initializer=fluid.initializer.Uniform(-stdv, stdv)))

        return out

    def conv_bn_layer(self,
                      input,
                      num_filters,
                      filter_size,
                      stride=1,
                      groups=1,
                      act=None,
                      name=None,
                      data_format="NCHW"):
        conv = fluid.layers.conv2d(
            input=input,
            num_filters=num_filters,
            filter_size=filter_size,
            stride=stride,
            padding=(filter_size - 1) // 2,
            groups=groups,
            act=None,
            param_attr=ParamAttr(name=name + "_weights"),
            bias_attr=False,
            data_format=data_format)
        if name == "conv1":
            bn_name = "bn_" + name
        else:
            bn_name = "bn" + name[3:]
        return fluid.layers.batch_norm(
            input=conv,
            act=act,
            param_attr=ParamAttr(name=bn_name + '_scale'),
            bias_attr=ParamAttr(bn_name + '_offset'),
            moving_mean_name=bn_name + '_mean',
            moving_variance_name=bn_name + '_variance',
            data_layout=data_format)

    def conv_bn_layer_new(self,
                          input,
                          num_filters,
                          filter_size,
                          stride=1,
                          groups=1,
                          act=None,
                          name=None,
                          data_format="NCHW"):
        pool = fluid.layers.pool2d(
            input=input,
            pool_size=2,
            pool_stride=2,
            pool_padding=0,
            pool_type='avg',
            ceil_mode=True,
            data_format=data_format)

        conv = fluid.layers.conv2d(
            input=pool,
            num_filters=num_filters,
            filter_size=filter_size,
            stride=1,
            padding=(filter_size - 1) // 2,
            groups=groups,
            act=None,
            param_attr=ParamAttr(name=name + "_weights"),
            bias_attr=False,
            data_format=data_format)
        if name == "conv1":
            bn_name = "bn_" + name
        else:
            bn_name = "bn" + name[3:]
        return fluid.layers.batch_norm(
            input=conv,
            act=act,
            param_attr=ParamAttr(name=bn_name + '_scale'),
            bias_attr=ParamAttr(bn_name + '_offset'),
            moving_mean_name=bn_name + '_mean',
            moving_variance_name=bn_name + '_variance',
            data_layout=data_format)

    def shortcut(self,
                 input,
                 ch_out,
                 stride,
                 name,
                 if_first=False,
                 data_format="NCHW"):
        ch_in = input.shape[1] if data_format == "NCHW" else input.shape[-1]
        if ch_in != ch_out or stride != 1:
            if if_first:
                return self.conv_bn_layer(
                    input,
                    ch_out,
                    1,
                    stride,
                    name=name,
                    data_format=data_format)
            else:
                return self.conv_bn_layer_new(
                    input,
                    ch_out,
                    1,
                    stride,
                    name=name,
                    data_format=data_format)
        elif if_first:
            return self.conv_bn_layer(
                input, ch_out, 1, stride, name=name, data_format=data_format)
        else:
            return input

    def bottleneck_block(self,
                         input,
                         num_filters,
                         stride,
                         name,
                         if_first,
                         data_format="NCHW"):
        conv0 = self.conv_bn_layer(
            input=input,
            num_filters=num_filters,
            filter_size=1,
            act='relu',
            name=name + "_branch2a",
            data_format=data_format)
        conv1 = self.conv_bn_layer(
            input=conv0,
            num_filters=num_filters,
            filter_size=3,
            stride=stride,
            act='relu',
            name=name + "_branch2b",
            data_format=data_format)
        conv2 = self.conv_bn_layer(
            input=conv1,
            num_filters=num_filters * 4,
            filter_size=1,
            act=None,
            name=name + "_branch2c",
            data_format=data_format)

        short = self.shortcut(
            input,
            num_filters * 4,
            stride,
            if_first=if_first,
            name=name + "_branch1",
            data_format=data_format)

        return fluid.layers.elementwise_add(x=short, y=conv2, act='relu')

    def basic_block(self, input, num_filters, stride, name, if_first,
                    data_format):
        conv0 = self.conv_bn_layer(
            input=input,
            num_filters=num_filters,
            filter_size=3,
            act='relu',
            stride=stride,
            name=name + "_branch2a",
            data_format=data_format)
        conv1 = self.conv_bn_layer(
            input=conv0,
            num_filters=num_filters,
            filter_size=3,
            act=None,
            name=name + "_branch2b",
            data_format=data_format)
        short = self.shortcut(
            input,
            num_filters,
            stride,
            if_first=if_first,
            name=name + "_branch1",
            data_format=data_format)
        return fluid.layers.elementwise_add(x=short, y=conv1, act='relu')


def ResNet18_vd():
    model = ResNet(layers=18, is_3x3=True)
    return model


def ResNet34_vd():
    model = ResNet(layers=34, is_3x3=True)
    return model


def ResNet50_vd():
    model = ResNet(layers=50, is_3x3=True)
    return model


def ResNet101_vd():
    model = ResNet(layers=101, is_3x3=True)
    return model


def ResNet152_vd():
    model = ResNet(layers=152, is_3x3=True)
    return model


def ResNet200_vd():
    model = ResNet(layers=200, is_3x3=True)
    return model
