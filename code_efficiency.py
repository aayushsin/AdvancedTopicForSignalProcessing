#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2015.
# Distributed under the "STEINWURF EVALUATION LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import sys
import matplotlib.pyplot as plt

import kodo


def main():
    """Simple example showing how to encode and decode a block of memory."""
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 8
    symbol_size = 160

    # In the following we will make an encoder/decoder factory.
    # The factories are used to build actual encoders/decoders
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(symbols, symbol_size)
    encoder = encoder_factory.build()

    packets = [0 for i in range(symbols)]

    num_runs = 1000
    print("Processing started")
    for i in range(num_runs):
        decoder_factory = kodo.FullVectorDecoderFactoryBinary(symbols, symbol_size)
        decoder = decoder_factory.build()

        # Create some data to encode. In this case we make a buffer
        # with the same size as the encoder's block size (the max.
        # amount a single encoder can encode)
        # Just for fun - fill the input data with random data
        data_in = os.urandom(encoder.block_size())

        # Assign the data buffer to the encoder so that we can
        # produce encoded symbols
        encoder.set_const_symbols(data_in)
        packet_number = 0
        encoder.set_systematic_off()
        last_rank = -1
        while not decoder.is_complete():
            # Generate an encoded packet
            packet = encoder.write_payload()
            #print("Packet {} encoded!".format(packet_number))

            # Pass that packet to the decoder
            decoder.read_payload(packet)
            #print("Packet {} decoded!".format(packet_number))
            packet_number += 1
            #print("rank: {}/{}".format(decoder.rank(), decoder.symbols()))
            curr_rank = decoder.rank()
            if curr_rank == last_rank:
                packets[curr_rank] += 1
            #packets[curr_rank] += 1
            last_rank = curr_rank

        #print("Processing finished")

        # The decoder is complete, now copy the symbols from the decoder
        data_out = decoder.copy_from_symbols()

        # Check if we properly decoded the data
        #print("Checking results")
        if data_out == data_in:
            pass #print("Data decoded correctly")
        else:
            print("Unable to decode please file a bug report :)")
            sys.exit(1)
    print("Processing finished")
    packets = [val/float(num_runs) for val in packets ]   
    print(packets)
    plt.plot([i for i in range(symbols)],packets)
    plt.show()
if __name__ == "__main__":
    main()
