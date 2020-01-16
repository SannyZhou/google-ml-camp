# -*- coding: utf-8 -*-
import torch
import torch.nn as nn


class GRU(nn.Module):
    def __init__(self,
                 layers,
                 input_dim,
                 output_dim,
                 bias=True,
                 batch_first=False,
                 dropout=0.0,
                 bidirectional=True):
        super(GRU, self).__init__()
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.num_layers = layers
        self.gru = torch.nn.GRU(input_size=input_dim,
                                hidden_size=output_dim,
                                num_layers=layers,
                                batch_first=batch_first,
                                bias=bias,
                                bidirectional=bidirectional,
                                dropout=dropout)

    def forward(self, inputs, seq_len=None, init_state=None, ori_state=False):
        if seq_len is not None:
            seq_len = seq_len.int()
            sorted_seq_len, indices = torch.sort(seq_len, descending=True)
            if self.batch_first:
                sorted_inputs = inputs[indices]
            else:
                sorted_inputs = inputs[:, indices]
            packed_inputs = torch.nn.utils.rnn.pack_padded_sequence(
                sorted_inputs,
                sorted_seq_len,
                batch_first=self.batch_first,
            )
            outputs, states = self.gru(packed_inputs, init_state)
        else:
            outputs, state = self.gru(inputs, init_state)

        if ori_state:
            return outputs, states
        if self.bidirectional:
            last_layer_hidden_state = states[2 * (self.num_layers - 1):]
            last_layer_hidden_state = torch.cat((last_layer_hidden_state[0], last_layer_hidden_state[1]), 1)
        else:
            last_layer_hidden_state = states[self.num_layers - 1]
            last_layer_hidden_state = last_layer_hidden_state[0]

        _, reversed_indices = torch.sort(indices, descending=False)
        last_layer_hidden_state = last_layer_hidden_state[reversed_indices]
        padding_out, _ = torch.nn.utils.rnn.pad_packed_sequence(outputs,
                                                                batch_first=self.batch_first)
        if self.batch_first:
            padding_out = padding_out[reversed_indices]
        else:
            padding_out = padding_out[:, reversed_indices]
        return padding_out, last_layer_hidden_state
